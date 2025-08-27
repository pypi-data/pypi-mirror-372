import os, re
from dacite import from_dict
from gitlab_evaluate.migration_readiness.jenkins.data_classes.plugin import JenkinsPlugin
from sklearn.cluster import KMeans
import numpy as np
import torch.nn as nn
import torch
import sqlite3
import requests
from urllib.parse import quote, urlparse
import xml.etree.ElementTree as ET
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from gitlab_ps_utils.processes import MultiProcessing
from gitlab_evaluate.migration_readiness.jenkins.jenkins import MultiProcessJenkins
from gitlab_evaluate.migration_readiness.jenkins.auto_encoder import AutoEncoder
from gitlab_evaluate.migration_readiness.jenkins.simple_neural_network import SimpleNN

# Core pipeline engines we don't want to count as "used plugins"
CORE_PIPELINE_PLUGINS = {
    "workflow-api","workflow-cps","workflow-job",
    "workflow-durable-task-step","workflow-basic-steps",
    "pipeline-stage-step","pipeline-input-step","pipeline-model-definition",
    "scm-api"
}

# Groovy tokens we should ignore when scanning for step/function calls
GROOVY_KEYWORDS = {
    'if','else','for','while','do','try','catch','finally','switch','case','break','continue','return','def','boolean','int','float','double','String','Map','List','null','true','false','new','class','static','public','private','protected','as','in'
}

class JenkinsEvaluateClient():
    def __init__(self, host, user, token, ssl_verify, processes=None, scm=None) -> None:
        self.setup_db()
        self.processes = processes
        self.server = MultiProcessJenkins(host, username=user, password=token, ssl_verify=ssl_verify, processes=self.processes)
        self.user = self.server.get_whoami()
        self.version = self.server.get_version()
        self.plugins = self.server.get_plugins_info()
        self.jobs, self.job_types = self.server.get_all_jobs()
        self.multi = MultiProcessing()

        # HTTP client for direct fetches
        self.host = host.rstrip('/')
        self._http = requests.Session()
        self._http.auth = (user, token)
        self._http.verify = ssl_verify
        self._http.headers.update({'Accept': '*/*', 'User-Agent': 'Evaluate-Client'})

        # Optional SCM configuration
        self.scm = scm or {} 

        self._config_cache = {}
        self._jfile_cache = {}

    def setup_db(self):
        if os.path.exists('jenkins.db'):
            os.remove('jenkins.db')
        con = sqlite3.connect('jenkins.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("CREATE TABLE jobs(_class, name, url, color, fullName UNIQUE)")
        cur.execute("CREATE TABLE job_types(type)")
        cur.execute("CREATE TABLE jobs_to_process(id UNIQUE, job)")
        con.commit()
        con.close()
    
    def drop_tables(self):
        con = sqlite3.connect('jenkins.db')
        cur = con.cursor()
        cur.execute("DROP TABLE jobs")
        cur.execute("DROP TABLE job_types")
        con.commit()
        con.close()

    def list_of_plugins(self):
        for plugin in self.plugins:
            yield from_dict(JenkinsPlugin, plugin)
    
    def estimate_resource_usage(self, job_name):
        """
        Estimates CPU and memory usage based on build duration and job type.
        """
        builds = self.server.get_job_info(job_name).get('builds', [])
        total_cpu_usage = 0
        total_memory_usage = 0
        build_count = 0

        for build in builds:
            build_number = build.get('number')
            build_info = self.server.get_build_info(job_name, build_number)
            duration = build_info.get('duration', 0)  # in milliseconds
            # Estimate CPU usage as a function of duration
            estimated_cpu = self.estimate_cpu_usage(duration)
            # Estimate memory usage based on job type or other factors
            estimated_memory = self.estimate_memory_usage(job_name)
            total_cpu_usage += estimated_cpu
            total_memory_usage += estimated_memory
            build_count += 1

        avg_cpu = total_cpu_usage / build_count if build_count > 0 else 0
        avg_memory = total_memory_usage / build_count if build_count > 0 else 0

        return {
            'cpu': avg_cpu,
            'memory': avg_memory
        }

    def estimate_cpu_usage(self, duration):
        """
        Estimates CPU usage based on build duration.
        """
        # Convert duration from milliseconds to seconds
        duration_seconds = duration / 1000.0
        # We assume CPU usage is proportional to duration
        # Arbitrary factor - Here we asssume that 1 seconds represents 1/2 cpu usage
        cpu_usage = duration_seconds * 0.5 
        return cpu_usage

    def estimate_memory_usage(self, job_name):
        """
        Estimates memory usage based on job type or characteristics.
        """
        job_info = self.server.get_job_info(job_name)
        job_class = job_info.get('_class', '')
        if 'Maven' in job_class:
            return 1024  # Assume Maven jobs use 1024MB on average
        elif 'WorkflowJob' in job_class:
            return 2048  # Assume Pipeline jobs use 2048MB on average
        else:
            return 512  # Default memory usage in MB for other job types

    def build_job_data(self, job):
        job_name = job['fullName']
        job_history = self.get_job_history(job_name)
        total_executions = len(job_history)
        total_duration = sum(build['duration'] for build in job_history)
        success_count = sum(1 for build in job_history if build['result'] == 'SUCCESS')
        avg_duration = total_duration / total_executions if total_executions > 0 else 0
        success_rate = success_count / total_executions if total_executions > 0 else 0

        resource_usage = self.estimate_resource_usage(job_name)

        return {
            'fullname': job.get('fullName', "N/A"),
            'name': job_name,
            'url': job.get('url', "N/A"),
            'color': job.get('color', "N/A"),
            '_class': job.get('_class', "N/A"),
            'execution_frequency': total_executions,
            'avg_duration': avg_duration,
            'success_rate': success_rate,
            'cpu_usage (estimate)': resource_usage['cpu'],
            'memory_usage (estimate)': resource_usage['memory']
        }
    
    def build_full_job_list(self):
        return list(self.multi.start_multi_process(self.build_job_data, self.jobs, processes=self.processes))

    def get_job_history(self, job_name):
        # Retrieve job build history and return relevant data
        builds = self.server.get_job_info(job_name).get('builds', [])
        build_data = []
        for build in builds:
            build_info = self.server.get_build_info(job_name, build.get('number'))
            build_data.append({
                'number': build.get('number', 'N/A'),
                'duration': build_info.get('duration', 0),
                'result': build_info.get('result', 'UNKNOWN'),
                'timestamp': build_info.get('timestamp', 0)
            })
        return build_data
    
    def train_predictive_model(self, job_data):
        input_size = 2
        hidden_size = 10
        output_size = 1
        model = SimpleNN(input_size, hidden_size, output_size)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

        X = np.array([[job['execution_frequency'], job['avg_duration']] for job in job_data])
        y = np.array([job['success_rate'] for job in job_data])
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        y = y.reshape(-1, 1)

        dataset = TensorDataset(torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32))
        dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

        model.train()
        for epoch in range(100):  # loop over the dataset multiple times
            for inputs, targets in dataloader:
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        return model, scaler

    def predict_impact(self, model, scaler, job):
        model.eval()
        inputs = scaler.transform([[job['execution_frequency'], job['avg_duration']]])
        inputs = torch.tensor(inputs, dtype=torch.float32)
        output = model(inputs).item()
        return output

    def train_anomaly_detection_model(self, job_data):
        input_size = 3
        hidden_size = 2
        model = AutoEncoder(input_size, hidden_size)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

        X = np.array([[job['execution_frequency'], job['avg_duration'], job['success_rate']] for job in job_data])
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        dataset = TensorDataset(torch.tensor(X, dtype=torch.float32))
        dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

        model.train()
        for epoch in range(100):  # loop over the dataset multiple times
            for inputs, in dataloader:
                outputs = model(inputs)
                loss = criterion(outputs, inputs)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        return model, scaler

    def detect_anomalies(self, model, scaler, job_data):
        model.eval()
        X = np.array([[job['execution_frequency'], job['avg_duration'], job['success_rate']] for job in job_data])
        X = scaler.transform(X)
        inputs = torch.tensor(X, dtype=torch.float32)
        outputs = model(inputs)
        losses = ((outputs - inputs) ** 2).mean(dim=1).detach().numpy()

        return losses > np.percentile(losses, 95)
    
    def cluster_jobs(self, job_data):
        # Convert job data to a suitable format for clustering
        job_features = np.array([[job['execution_frequency'], job['avg_duration'], job['success_rate']] for job in job_data])
        kmeans = KMeans(n_clusters=min(3, len(job_data)), random_state=0).fit(job_features)
        return kmeans.labels_

    def get_shared_library_count_from_text(self, jenkinsfile_text: str) -> int:
        if not jenkinsfile_text:
            return 0
        try:
            # Examples this regex matches:
            #   @Library('acme-utils')      -> "acme-utils"
            #   @Library("team-lib@2.3.1")  -> "team-lib@2.3.1"
            #   @Library('lib1@main,lib2')  -> "lib1@main,lib2"
            count1 = len(re.findall(r'@Library\(\s*[\"\']([^\"\']+)[\"\']\s*\)', jenkinsfile_text))

            # Examples this regex matches:
            #   library('acme-utils')     -> "acme-utils"
            #   library("team-lib@main")  -> "team-lib@main"
            count2 = len(re.findall(r'\blibrary\s*\(\s*[\"\']([^\"\']+)[\"\']\s*\)', jenkinsfile_text))
            return count1 + count2
        except Exception:
            return 0

    def _full_name_to_job_path(self, full_name: str) -> str:
        parts = [quote(p, safe='') for p in (full_name or '').split('/')]
        return '/'.join(f'job/{p}' for p in parts if p)

    def get_job_config_xml(self, full_name: str) -> str:
        if not full_name:
            return ''
        if full_name in self._config_cache:
            return self._config_cache[full_name]

        xml_text = ''
        try:
            xml_text = self.server.get_job_config(full_name)
        except Exception:
            xml_text = ''
        if not xml_text:
            path = self._full_name_to_job_path(full_name)
            url = f"{self.host}/{path}/config.xml"
            try:
                r = self._http.get(url, timeout=30)
                if r.ok:
                    xml_text = r.text
            except Exception:
                xml_text = ''
        self._config_cache[full_name] = xml_text or ''
        return self._config_cache[full_name]

    def _parse_inline_script_from_config(self, config_xml: str) -> str:
        if not config_xml:
            return ''
        try:
            root = ET.fromstring(config_xml)
            for defn in root.findall('.//definition'):
                clazz = defn.get('class', '')
                if 'CpsFlowDefinition' in clazz:
                    script_el = defn.find('script')
                    if script_el is not None and script_el.text:
                        return script_el.text
        except Exception:
            return ''
        return ''

    def _extract_scm_details(self, config_xml: str) -> dict:
        out = {
            'host_type': 'unknown',
            'base_url': None,
            'project_path': None,
            'branch': None,
            'script_path': None,
            'repo_http_url': None,
            'repo_ssh_url': None,
            'browser_url': None,
        }
        if not config_xml:
            return out
        try:
            root = ET.fromstring(config_xml)
            sp = root.find('.//definition/scriptPath')
            if sp is not None and sp.text:
                out['script_path'] = sp.text.strip()
            head_name = root.find('.//properties//BranchJobProperty//branch//head//name')
            if head_name is not None and head_name.text:
                out['branch'] = head_name.text.strip()
            else:
                bs = root.find('.//scm//branches//name')
                if bs is not None and bs.text:
                    out['branch'] = bs.text.strip()
            u = root.find('.//scm//userRemoteConfigs//url')
            if u is not None and u.text:
                url = u.text.strip()
                if url.startswith('http://') or url.startswith('https://'):
                    out['repo_http_url'] = url
                elif url.startswith('git@'):
                    out['repo_ssh_url'] = url
            b = root.find('.//scm//browser//url')
            if b is not None and b.text:
                out['browser_url'] = b.text.strip()
            obj = root.find(".//actions//jenkins.scm.api.metadata.ObjectMetadataAction//objectUrl")
            if not out['browser_url'] and obj is not None and obj.text:
                out['browser_url'] = obj.text.strip()
            candidate = out['browser_url'] or out['repo_http_url'] or out['repo_ssh_url']
            if candidate:
                if candidate.startswith('git@') and ':' in candidate:
                    host, path = candidate.split(':', 1)
                    host = host.split('@', 1)[1]
                    candidate_http = f"https://{host}/{path}"
                else:
                    candidate_http = candidate
                if candidate_http.endswith('.git'):
                    candidate_http = candidate_http[:-4]
                slug = candidate_http
                if '/-/' in slug:
                    slug = slug.split('/-/', 1)[0]
                parsed = urlparse(slug)
                if parsed.scheme and parsed.netloc:
                    out['base_url'] = f"{parsed.scheme}://{parsed.netloc}"
                    out['project_path'] = parsed.path.strip('/')
                    if 'gitlab' in parsed.netloc:
                        out['host_type'] = 'gitlab'
                    elif 'github' in parsed.netloc:
                        out['host_type'] = 'github'
                else:
                    out['project_path'] = slug
        except Exception:
            return out
        return out

    def _gitlab_fetch_file_by_details(self, details: dict, token: str | None) -> str:
        base_url = details.get('base_url')
        project_path = details.get('project_path')
        branch = details.get('branch') or 'main'
        file_path = details.get('script_path') or 'Jenkinsfile'
        if not base_url or not project_path:
            return ''
        try:
            project_id = quote(project_path, safe='')
            file_id = quote(file_path, safe='')
            ref = quote(branch, safe='')
            url = f"{base_url}/api/v4/projects/{project_id}/repository/files/{file_id}/raw?ref={ref}"
            headers = {}
            if token:
                headers['PRIVATE-TOKEN'] = token
            r = requests.get(url, headers=headers, timeout=30)
            if r.ok:
                return r.text
        except Exception:
            return ''
        return ''

    def _github_fetch_file_by_details(self, details: dict, token: str | None) -> str:
        base_url = 'https://api.github.com'
        project_path = details.get('project_path')
        branch = details.get('branch') or 'main'
        file_path = details.get('script_path') or 'Jenkinsfile'
        if not project_path:
            return ''
        try:
            headers = {'Accept': 'application/vnd.github.raw+json'}
            if token:
                headers['Authorization'] = f"Bearer {token}"
            api = f"{base_url}/repos/{project_path}/contents/{file_path}?ref={quote(branch, safe='')}"
            r = requests.get(api, headers=headers, timeout=30)
            if r.ok:
                return r.text
        except Exception:
            return ''
        return ''

    def get_jenkinsfile_text(self, full_name: str, config_xml: str) -> str:
        cache_key = f"{full_name}::jfile"
        if cache_key in self._jfile_cache:
            return self._jfile_cache[cache_key]
        inline = self._parse_inline_script_from_config(config_xml)
        if inline:
            self._jfile_cache[cache_key] = inline
            return inline
        details = self._extract_scm_details(config_xml)
        text = ''
        if details.get('host_type') == 'gitlab':
            token = (self.scm.get('gitlab') or {}).get('token')
            text = self._gitlab_fetch_file_by_details(details, token)
        elif details.get('host_type') == 'github':
            token = (self.scm.get('github') or {}).get('token')
            text = self._github_fetch_file_by_details(details, token)
        self._jfile_cache[cache_key] = text or ''
        return self._jfile_cache[cache_key]

    def _extract_candidate_steps(self, jenkinsfile_text: str) -> set:
        if not jenkinsfile_text:
            return set()
        txt = re.sub(r"/\*.*?\*/", "", jenkinsfile_text, flags=re.S)
        txt = re.sub(r"//.*?$", "", txt, flags=re.M)
        tokens = re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?)\s*\(", txt)
        steps = set()
        for t in tokens:
            base = t.split('.', 1)[0]
            if base in GROOVY_KEYWORDS:
                continue
            steps.add(t)
        return steps

    def get_plugin_count_from_config(self, config_xml: str) -> int:
        if not config_xml:
            return 0
        try:
            plugins = set(re.findall(r'plugin=\"([^@\"]+)(?:@[^\"]*)?\"', config_xml))
            return len(plugins)
        except Exception:
            return 0

    def get_plugin_count_for_job(self, job: dict, config_xml: str, jenkinsfile_text: str) -> int:
        """
        - Pipeline jobs (WorkflowJob/MBP branches): use Jenkinsfile heuristics against installed plugins.
        - Freestyle/other: config-based.
        """
        job_class = job.get('_class', '') or ''
        is_pipeline = ('WorkflowJob' in job_class) or ('flow-definition' in (config_xml or ''))
        if is_pipeline:
            b = self.approx_plugin_count_by_alias(jenkinsfile_text)
            if b > 0:
                return b
            return self.get_plugin_count_from_config(config_xml)
        else:
            return self.get_plugin_count_from_config(config_xml)


    # Heuristic approach to count plugins using installed plugins + Jenkinsfile
    def approx_plugin_count_by_alias(self, jenkinsfile_text: str) -> int:
        if not jenkinsfile_text:
            return 0
        def norm(s: str) -> str:
            return ''.join(ch for ch in (s or '').lower() if ch.isalnum())

        # Build a token set from the Jenkinsfile
        raw_tokens = self._extract_candidate_steps(jenkinsfile_text)
        tokens = set()
        for tok in raw_tokens:
            base = tok.split('.', 1)[0]
            tokens.add(norm(base))              # e.g., withCredentials -> withcredentials, docker.build -> docker
            tokens.add(norm(tok.replace('.', '')))  # e.g., docker.build -> dockerbuild

        used = set()
        for p in (self.plugins or []):
            short = (p.get('shortName') or p.get('short_name') or '').strip()
            longn = (p.get('longName') or p.get('displayName') or '').strip()
            if not short:
                continue
            sid = norm(short)
            aliases = {sid}
            # Add hyphen/underscore/space segments as aliases (docker-workflow -> docker, workflow)
            for seg in re.split(r'[-_ ]+', short):
                if seg:
                    aliases.add(norm(seg))
            for seg in re.split(r'[-_ ]+', longn):
                if seg:
                    aliases.add(norm(seg))

            # Match strategy: equality or substring (>= 4 chars to reduce noise)
            matched = False
            for a in list(aliases):
                if len(a) < 4:
                    continue
                for t in tokens:
                    if t == a or t.startswith(a) or a.startswith(t) or (a in t) or (t in a):
                        matched = True
                        break
                if matched:
                    break
            if matched:
                used.add(short)
        return len([u for u in used if u not in CORE_PIPELINE_PLUGINS])
    
    def classify_tshirt_size(self, job: dict, plugin_count: int, shared_lib_count: int, loc: int, jenkinsfile_text: str) -> str:
        cls = job.get('_class', '')
        predicted_impact = job.get('predicted_impact', 0)
        anomaly = bool(job.get('anomaly', False))
        dynamic_groovy = bool(re.search(r'\bload\s*\(|\bGroovyShell\b|\bevaluate\s*\(', jenkinsfile_text or ''))
        if shared_lib_count > 10 or loc > 1000 or anomaly or predicted_impact < 0:
            return 'XL'
        if 'FreeStyleProject' in cls and (plugin_count <= 5 and shared_lib_count == 0):
            return 'S'
        if shared_lib_count <= 3 and plugin_count <= 10 and predicted_impact >= 0.5:
            return 'M'
        if 'WorkflowMultiBranchProject' in cls or plugin_count > 10 or (3 <= shared_lib_count <= 10) or dynamic_groovy or 0 <= predicted_impact <= 0.5:
            return 'L'
        return 'Unknown'
