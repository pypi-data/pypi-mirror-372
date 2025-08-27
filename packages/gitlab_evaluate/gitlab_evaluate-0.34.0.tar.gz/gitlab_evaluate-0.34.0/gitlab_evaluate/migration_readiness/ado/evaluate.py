from urllib.parse import urljoin
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
import requests
import base64
import sys
import time

class AdoEvaluateClient():
    def __init__(self, host, token, api_version, verify=True):
        self.host = host
        self.total_repositories = 0
        self.total_disabled_repositories = 0
        self.total_uninitialized_repositories = 0
        encoded_pat = base64.b64encode(f":{token}".encode()).decode()
        self.headers = {
            'Authorization': f'Basic {encoded_pat}',
            'Content-Type': 'application/json'
        }
        self.params = {
            'api-version': api_version
        }
        self.session = requests.Session()
        self.session.verify = verify
        if not verify:
            print("Ignoring SSL verification")
            disable_warnings(InsecureRequestWarning)

    def generate_request_url(self, host, api, sub_api=None):
        base_url = host
        if not (base_url.startswith("https://") or base_url.startswith("http://")):
            print("Invalid URL. Please provide a valid URL.")
            sys.exit(1)
        if sub_api and "dev.azure.com" in self.host:
            base_url_parts = base_url.split("://", 1)
            base_url = f"{base_url_parts[0]}://{sub_api}.{base_url_parts[1]}"
        return urljoin(base_url + '/', api)

    def get_descriptor(self, project_id, params=None):
        url = self.generate_request_url(self.host, api=f"_apis/graph/descriptors/{project_id}", sub_api="vssps")
        try:
            response = self.session.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()["value"]
        except Exception as e:
            print(f"Error fetching descriptors {url}: {e}", file=sys.stderr)

    def get_project_administrators_group(self, project_id, params=None):
        scopeDescriptor = self.get_descriptor(project_id)
        url = self.generate_request_url(self.host, api=f"_apis/graph/groups?scopeDescriptor={scopeDescriptor}", sub_api="vssps")
        try:
            response = self.session.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            project_admins = next((item for item in response.json()["value"] if item["displayName"] == "Project Administrators"), None)
            if project_admins:
                return project_admins["originId"]
            else:
                return None
        except Exception as e:
            print(f"Error fetching descriptors {url}: {e}", file=sys.stderr)

    def get_project_administrators(self, project_id, params=None):
        project_group_id = self.get_project_administrators_group(project_id)
        url = self.generate_request_url(self.host, api=f"_apis/GroupEntitlements/{project_group_id}/members", sub_api="vsaex")
        try:
            response = self.session.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            admins = []
            for member in response.json()["members"]:
                admins.append(f"{member['user']['displayName']} <{member['user']['mailAddress']}>")
            return admins
        except Exception as e:
            print(f"Error fetching descriptors {url}: {e}", file=sys.stderr)
    
    def get_project_users(self, project_id, params=None):
        scopeDescriptor = self.get_descriptor(project_id)
        url = self.generate_request_url(self.host, api=f"_apis/graph/users?scopeDescriptor={scopeDescriptor}", sub_api="vssps")
        users = []
        
        while True:
            try:
                response = self.session.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                for member in response.json()["value"]:
                    users.append(f"{member['displayName']} <{member['mailAddress']}>")
            except Exception as e:
                print(f"Error fetching descriptors {url}: {e}", file=sys.stderr)
            
            # check if rate limit has been hit
            self.wait_timer(response.headers, "Project Users List")
            
            if not any(key.lower() == "x-ms-continuationtoken" for key in response.headers):
                break  # No more pages
            # There is page, so get the continuation token for the next page
            params["continuationToken"] = response.headers["X-MS-ContinuationToken"]
        
        return users

    def get_work_items(self, project_id, project_name, params=None):
        params.update(self.params)
        url = self.generate_request_url(self.host, api=f"{project_id}/_apis/wit/wiql")
        query = {
            "query": (
                "SELECT [System.Id], [System.Title], [System.State] "
                "FROM WorkItems "
                "WHERE [System.TeamProject] = @project"
            )
        }
        return self.session.post(url, headers=self.headers, params=params, json=query)

    def get_release_definitions(self, project_id, params=None):
        params.update(self.params)
        url = self.generate_request_url(self.host, api=f"{project_id}/_apis/release/definitions", sub_api="vsrm")
        return self.session.get(url, headers=self.headers, params=params)

    def get_build_definitions(self, project_id, params=None):
        params.update({
            "includeAllProperties": "true",
        })
        url = self.generate_request_url(self.host, api=f"{project_id}/_apis/build/definitions")
        return self.session.get(url, headers=self.headers, params=params)

    def get_commits(self, project_id, repository_id, params=None):
        if params is None:
            params = {}
        params.update(self.params)
        url = self.generate_request_url(self.host, api=f"{project_id}/_apis/git/repositories/{repository_id}/commits")
        return self.session.get(url, headers=self.headers, params=params)

    def get_prs(self, project_id, repository_id, params=None):
        if params is None:
            params = {}
        params.update(self.params)
        params.setdefault("status", "all")
        url = self.generate_request_url(self.host, api=f"{project_id}/_apis/git/repositories/{repository_id}/pullrequests")
        return self.session.get(url, headers=self.headers, params=params)

    def get_branches(self, project_id, repository_id, params=None):
        params.update(self.params)
        url = self.generate_request_url(self.host, api=f"{project_id}/_apis/git/repositories/{repository_id}/refs")
        return self.session.get(url, headers=self.headers, params=params)

    def get_repos(self, project_id, params=None):
        params.update(self.params)
        url = self.generate_request_url(self.host, api=f"{project_id}/_apis/git/repositories")
        return self.session.get(url, headers=self.headers, params=params)

    def get_project(self, project_id, params=None):
        url = self.generate_request_url(self.host, api=f"_apis/projects/{project_id}")
        return self.session.get(url, headers=self.headers, params=params)

    def get_projects(self, params=None):
        params.update(self.params)
        url = self.generate_request_url(self.host, api='_apis/projects')
        return self.session.get(url, headers=self.headers, params=params)

    def get_project_properties(self, project_id, params=None):
        url = self.generate_request_url(self.host, api=f"_apis/projects/{project_id}/properties")
        return self.session.get(url, headers=self.headers, params=params)

    def get_users(self, params=None):
        params.update(self.params)
        url = self.generate_request_url(self.host, api='_apis/graph/users', sub_api="vssps")
        return self.session.get(url, headers=self.headers, params=params)

    def get_agent_pools(self, params=None):
        params.update(self.params)
        url = self.generate_request_url(self.host, api='_apis/distributedtask/pools')
        return self.session.get(url, headers=self.headers, params=params)

    def get_feeds(self, params=None):
        if params is None:
            params = {}
        params.update(self.params)
        url = self.generate_request_url(self.host, api='_apis/packaging/feeds', sub_api="feeds")
        return self.session.get(url, headers=self.headers, params=params)

    def get_packages(self, feed_id, project_id, params=None):
        if project_id:
            url = self.generate_request_url(self.host, api=f'{project_id}/_apis/packaging/feeds/{feed_id}/packages', sub_api="feeds")
        else:
            url = self.generate_request_url(self.host, api=f'_apis/packaging/feeds/{feed_id}/packages', sub_api="feeds")
        return self.session.get(url, headers=self.headers, params=params)

    def get_package_metrics_batch(self, payload, feed_id, project_id=None):
        if project_id:
            url = self.generate_request_url(self.host, api=f'{project_id}/_apis/packaging/feeds/{feed_id}/packagemetricsbatch', sub_api="feeds")
        else:
            url = self.generate_request_url(self.host, api=f'_apis/packaging/feeds/{feed_id}/packagemetricsbatch', sub_api="feeds")
        return self.session.post(url, headers=self.headers, data=payload, params=self.params)
    
    def get_variable_groups(self, project_id, params=None):
        params.update(self.params)
        url = self.generate_request_url(self.host, api=f"{project_id}/_apis/distributedtask/variablegroups")
        return self.session.get(url, headers=self.headers, params=params)

    def get_wikis(self, project_id, params=None):
        url = self.generate_request_url(self.host, api=f"{project_id}/_apis/wiki/wikis")
        return self.session.get(url, headers=self.headers, params=params)

    def get_source_details(self, params=None):
        url = self.generate_request_url(self.host, api='_home/About')
        return self.session.get(url, headers=self.headers, params=params)

    def retry_request(self, request_func, params, *args, max_retries=2, retry_delay=2):
        for retry_count in range(max_retries):
            response = request_func(*args, params=params)
            if response.status_code == 200:
                return response
            
            if response.status_code == 429 and any(key.lower() == "retry-after" for key in response.headers):
                retry_delay = int(response.headers['Retry-After'])
            
            print(f"Received error {response.status_code} for the URL {response.url} Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        print(f"Max retries reached ({retry_count}). Unable to complete the request.")
        # raise Exception(f"Failed to complete the request after {max_retries} retries: {response.status_code}")

    def wait_timer(self, headers, api_type):
        if any(key.lower() == "retry-after" for key in headers):
            retry_delay = int(headers["Retry-After"])
            
            print(f'Rate Limit Hit for {api_type} API. Retrying in {retry_delay} Seconds')
            time.sleep(retry_delay)

    def test_connection(self, params=None):
        params.update(self.params)
        url = self.generate_request_url(self.host, api='_apis/ConnectionData')
        return self.session.get(url, headers=self.headers, params=params)

    def handle_getting_project_data(self, project):
        if not self.session.verify:
            disable_warnings(InsecureRequestWarning)
        params = {}
        total_repos = 0
        total_build_definitions_classic = 0
        total_build_definitions_yaml = 0
        total_release_definitions = 0
        total_work_items = 0
        print(f"Fetching project data from {project.get('name')}")
        project_id = project["id"]
        project_name = project["name"]
        if "dev.azure.com" in self.host:
            print(f"Retriving project administrators in {project_name}...")
            project_admins = self.get_project_administrators(project_id, params)
            if project_admins and isinstance(project_admins, list):
                project_admins_str = ', '.join(project_admins)
            else:
                project_admins_str = str(project_admins) if project_admins else "No administrators found"

            print(f"Retriving all project users in {project_name}...")
            project_users = self.get_project_users(project_id, params)

            if project_users and isinstance(project_users, list):
                project_users_str = ', '.join(project_users)
            else:
                project_users_str = str(project_users) if project_users else "No users found"
        else:
            print("Project administrators and users retrieval is not supported for this URL. Skipping ... ")
            project_admins_str = "N/A"
            project_users_str = "N/A"

        print(f"Retriving total repositories, yaml definitions, classic releases and work items in {project_name}...")
        get_repos_response = self.retry_request(self.get_repos, params, project_id)
        if get_repos_response:
            total_repos = len(get_repos_response.json().get("value", []))

        get_build_definitions_response = self.retry_request(self.get_build_definitions, params, project_id)
        if get_build_definitions_response:
            for definition in get_build_definitions_response.json().get("value", []):
                if definition.get("process", {}).get("type") == 2:  # Multi-stage YAML
                    total_build_definitions_yaml += 1
                elif definition.get("process", {}).get("type") == 1:  # Classic
                    total_build_definitions_classic += 1

        get_release_definitions_response = self.retry_request(self.get_release_definitions, params, project_id)
        if get_release_definitions_response:
            total_release_definitions = len(get_release_definitions_response.json().get("value", []))

        get_work_items_response = self.retry_request(self.get_work_items, params, project_id, project_name)
        if get_work_items_response:
            total_work_items = len(get_work_items_response.json().get("workItems", []))

        tfvc_project = False
        wiki_info = "N/A"
        try:
            print(f"Checking if {project_name} is a TFVC project...")
            properties_response = self.get_project_properties(project_id)
            properties = properties_response.json().get("value", [])
            for prop in properties:
                if prop.get("name") == "System.SourceControlTfvcEnabled" and prop.get("value") == "True":
                    tfvc_project = True
                    break
                
            print(f"Checking if {project_name} has wiki...")
            wikis_response = self.get_wikis(project_id, params)
            if wikis_response and wikis_response.status_code == 200:
                wiki_info = len(wikis_response.json().get("value", []))
            else:
                wiki_info = "N/A"
        except Exception as e:
            print(f"Failed to get project properties for TFVC check: {e}")


        project_data = {
            'Project ID': project.get('id', 'N/A'),
            'URL': project.get('url', 'N/A'),
            'Name': project.get('name', 'N/A'),
            'Total Repositories': total_repos,
            'Total Build Definitions (Classic)': total_build_definitions_classic,
            'Total Build Definitions (Multi-stage YAML)': total_build_definitions_yaml,
            'Total Release Definitions': total_release_definitions,
            'Total Work Items': total_work_items,
            'Administrators': project_admins_str,
            'Project Users': project_users_str,
            'TFVC': tfvc_project,
            'Wiki': wiki_info
        }
        return project_data

    def handle_getting_repo_data(self, project):
        if not self.session.verify:
            disable_warnings(InsecureRequestWarning)
        repos_data = []
        params = {
            "$top": "100"
        }
        project_id = project.get("id")
        print(f"Fetching repositories for project {project_id}...")

        while True:
            response = self.get_repos(project_id, params)
            repos = response.json()
            self.total_repositories += len(repos.get('value'))
            repos_data.extend(repos.get('value'))
            for repo in repos['value']:
                print(f"Processing repository {repo.get('name')} in project {project_id}...")
                if repo.get("isDisabled", False):
                    self.total_disabled_repositories += 1
                if repo.get("size") is not None and repo.get("size") == 0:
                    self.total_uninitialized_repositories += 1

            # Print progress
            print(f"Project {project_id}: Retrieved and processed {self.total_repositories} repositories so far...")

            # check if rate limit has been hit
            self.wait_timer(response.headers, "Project Repositories List")

            # Check if there's a next page
            if not any(key.lower() == "x-ms-continuationtoken" for key in response.headers):
                break  # No more pages
            # There is page, so get the continuation token for the next page
            params["continuationToken"] = response.headers["X-MS-ContinuationToken"]

        return repos_data
