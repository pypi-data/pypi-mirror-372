from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests


class BitbucketEvaluateClient():
    def __init__(self, host, token):
        self.host = host.rstrip('/') + "/rest/api/1.0"
        self.headers = {'Authorization': f'Bearer {token}'}
        self.session = self._create_session()

    def _create_session(self):
        session = requests.Session()
        retries = Retry(total=5,
                        backoff_factor=1,
                        status_forcelist=[500, 502, 503, 504, 429])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session

    def get_application_properties(self):
        url = f"{self.host}/application-properties"
        return self.session.get(url, headers=self.headers)

    def get_projects(self, params=None):
        url = f"{self.host}/projects"
        return self.session.get(url, headers=self.headers, params=params)

    def get_repos(self, project_key, params=None):
        url = f"{self.host}/projects/{project_key}/repos"
        return self.session.get(url, headers=self.headers, params=params)

    def get_admin_users(self, params=None):
        url = f"{self.host}/admin/users"
        return self.session.get(url, headers=self.headers, params=params)

    def get_users(self, params=None):
        url = f"{self.host}/users"
        return self.session.get(url, headers=self.headers, params=params)

    def get_branches(self, project_key, repo_slug, params=None):
        url = f"{self.host}/projects/{project_key}/repos/{repo_slug}/branches"
        return self.session.get(url, headers=self.headers, params=params)

    def get_prs(self, project_key, repo_slug, params=None):
        url = f"{self.host}/projects/{project_key}/repos/{repo_slug}/pull-requests"
        return self.session.get(url, headers=self.headers, params=params)

    def get_commits(self, project_key, repo_slug, params=None):
        url = f"{self.host}/projects/{project_key}/repos/{repo_slug}/commits"
        return self.session.get(url, headers=self.headers, params=params)

    def get_repo_size(self, repo):
        # Grab the repo URL and build the URL to get repo size
        repo_url = repo['links']['self'][0]['href'].replace(
            '/browse', '/sizes')
        # Get repo size
        response = self.session.get(repo_url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch repository size for repo {repo_url}: {response.status_code} - {response.text}")
        response_json = response.json()
        # Convert size to MB
        repo_size = (response_json['repository'] +
                     response_json['attachments']) / 1024 / 1024
        return round(repo_size, 2)

    def get_tags(self, project_key, repo_slug, params=None):
        url = f"{self.host}/projects/{project_key}/repos/{repo_slug}/tags"
        return self.session.get(url, headers=self.headers, params=params)

    def is_repo_archived(self, project_key, repo_slug):
        url = f"{self.host}/projects/{project_key}/repos/{repo_slug}"
        response = self.session.get(url, headers=self.headers)

        if response.status_code == 200:
            repo_info = response.json()
            return repo_info.get('archived', False)
        response.raise_for_status()
        return False
