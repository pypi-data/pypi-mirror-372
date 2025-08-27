from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import json
from time import time
import hashlib

class SimpleCacheSession(requests.Session):
    def __init__(self, expire_after=300, *args, **kwargs):
        """
        Initialize the SimpleCacheSession.

        :param expire_after: Cache expiration time in seconds (default: 300 seconds).
        """
        super().__init__(*args, **kwargs)
        self.expire_after = expire_after
        self.cache = {}

    def _make_cache_key(self, method, url, params=None, data=None, headers=None):
        """
        Create a cache key based on the request parameters.

        :param method: HTTP method (e.g. "GET")
        :param url: Request URL.
        :param params: Query parameters.
        :param data: Request data.
        :param headers: Request headers.
        :return: A string representing the MD5 hash of the key data.
        """
        key_data = {
            "method": method.upper(),
            "url": url,
            "params": params or {},
            "data": data or {},
            "headers": headers or {}
        }
        # Generate a consistent string representation and hash it.
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()

    def request(self, method, url, **kwargs):
        """
        Override the request method to implement GET request caching.

        :param method: HTTP method.
        :param url: Request URL.
        :param kwargs: Additional parameters for the request.
        :return: A requests.Response-like object.
        """
        if method.upper() == "GET":
            key = self._make_cache_key(method, url,
                                       params=kwargs.get("params"),
                                       data=kwargs.get("data"),
                                       headers=kwargs.get("headers"))
            current_time = time()

            # If we have a cached response that hasn't expired, return it.
            if key in self.cache:
                cached_response, timestamp = self.cache[key]
                if current_time - timestamp < self.expire_after:
                    print("Returning cached response for", url)
                    return cached_response

            # Otherwise, perform the GET request.
            response = super().request(method, url, **kwargs)
            # Cache the response along with the current timestamp.
            self.cache[key] = (response, current_time)
            return response

        # For non-GET requests, bypass caching.
        return super().request(method, url, **kwargs)

class GithubEvaluateClient():
    def __init__(self, host, token):
        self.host = host.rstrip('/') + "/api/v3"
        self.headers = {'Authorization': f'Bearer {token}', 'X-GitHub-Api-Version': '2022-11-28'}
        self.session = self._create_session()

    def _create_session(self):
        session = SimpleCacheSession(expire_after=3000) # x2 speedup measured
        #session = requests.Session() # uncached version
        retries = Retry(total=2,
                        backoff_factor=1,
                        status_forcelist=[500, 502, 503, 504, 429])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session

    def paginate(self, url, params=None, headers=None, list_key=None):
        """
        Paginate through an API endpoint until no 'next' link is found.
        
        Instead of raising errors, if a request returns an error status,
        this method returns that response immediately.
        
        If the JSON content of the first page is a list, the .json() method
        on the final returned response will be a concatenation of all pages.
        Otherwise, it returns the JSON from the first (and only) page.
        
        :param url: The initial URL for the GET request.
        :param params: (Optional) Query parameters for the first request.
        :param headers: (Optional) Headers for the requests. If not provided,
                        self.headers is used.
        :return: A response‑like object (an instance of requests.Response) whose
                 .json() method returns the aggregated result.
        """
        headers = headers or self.headers
        aggregated_data = None
        is_list = None
        first_response = None

        while url:
            response = self.session.get(url, headers=headers, params=params)
            # Instead of raising an exception on error, just return the error response.
            if response.status_code >= 400:
                return response

            # Save the first successful response for status code and headers.
            if first_response is None:
                first_response = response

            data = response.json()
            # On the first page, determine if we are dealing with a list.
            if is_list is None :
                is_list = isinstance(data, list) or isinstance(data.get(list_key), list)
                if is_list:
                    aggregated_data = []
                else:
                    aggregated_data = data  # For non-list responses, just use the first page.
            # If the response is a list, aggregate (concatenate) the pages.
            if is_list:
                if list_key is None:
                    aggregated_data.extend(data)
                else:
                    aggregated_data.extend(data[list_key])
            else:
                # For non-list data, we ignore pagination.
                break

            # After the first request, query params have been applied.
            params = None

            # Look for the 'next' link in the Link header.
            link_header = response.headers.get("Link", "")
            next_url = None
            if link_header:
                # The header can contain multiple comma-separated links.
                for link in link_header.split(","):
                    parts = link.split(";")
                    if len(parts) < 2:
                        continue
                    link_url = parts[0].strip().strip("<>")
                    rel = parts[1].strip()
                    if rel == 'rel="next"':
                        next_url = link_url
                        break
            url = next_url

        # Build a new response-like object to return.
        new_response = requests.Response()
        if first_response is not None:
            new_response.status_code = first_response.status_code
            new_response.headers = first_response.headers
        else:
            new_response.status_code = 200
            new_response.headers = {}
        # Set the _content attribute so that .json() works as expected.
        new_response._content = json.dumps(aggregated_data).encode("utf-8")
        return new_response

    # admin methods
    def get_application_properties(self):
        url = f"{self.host}/meta"
        return self.paginate(url, headers=self.headers)

    def get_orgs(self, params=None):
        url = f"{self.host}/organizations"
        return self.paginate(url, headers=self.headers, params=params)

    def get_admin_stats(self, params=None):
        url = f"{self.host}/enterprise/stats/all"
        return self.paginate(url, headers=self.headers, params=params)

    def get_admin_users(self, params=None):
        url = f"{self.host}/users"
        return self.paginate(url, headers=self.headers, params=params)

    def get_users(self, params=None):
        url = f"{self.host}/users"
        return self.paginate(url, headers=self.headers, params=params)
    
    # organization methods
    def get_org_repos(self, org_key, params=None):
        url = f"{self.host}/orgs/{org_key}/repos"
        return self.paginate(url, headers=self.headers, params=params)

    def get_org_teams(self, org_key, params=None):
        url = f"{self.host}/orgs/{org_key}/teams"
        return self.paginate(url, headers=self.headers, params=params)

    def get_org_members(self, org_key, params=None):
        url = f"{self.host}/orgs/{org_key}/members"
        return self.paginate(url, headers=self.headers, params=params)

    def get_org_packages(self, org_key, params=None):
        url = f"{self.host}/orgs/{org_key}/packages"
        return self.paginate(url, headers=self.headers, params=params)

    def get_org_runners(self, org_key, params=None, paginate=True):
        url = f"{self.host}/orgs/{org_key}/actions/runners"
        if paginate is True:
            return self.paginate(url, headers=self.headers, params=params, list_key="runners")
        else:
            return self.session.get(url, headers=self.headers, params=params)

    def get_org_runner_groups(self, org_key, params=None, paginate=True):
        url = f"{self.host}/orgs/{org_key}/actions/runner-groups"
        if paginate is True:
            return self.paginate(url, headers=self.headers, params=params, list_key="runner_groups")
        else:
            return self.session.get(url, headers=self.headers, params=params)

    # user methods
    def get_user_repos(self, user_key, params=None):
        url = f"{self.host}/users/{user_key}/repos"
        return self.paginate(url, headers=self.headers, params=params)

    def get_user_packages(self, user_key, params=None, paginate=True):
        url = f"{self.host}/users/{user_key}/packages"
        if paginate is True:
            return self.paginate(url, headers=self.headers, params=params)
        else:
            return self.session.get(url, headers=self.headers, params=params)
    
    # team methods
    def get_team_members(self, org_key, team_key, params=None):
        url = f"{self.host}/orgs/{org_key}/teams/{team_key}/members"
        return self.paginate(url, headers=self.headers, params=params)

    # repository methods
    def get_repo_branches(self, org_key, repo_slug, params=None):
        url = f"{self.host}/repos/{org_key}/{repo_slug}/branches"
        return self.paginate(url, headers=self.headers, params=params)

    def get_user_by_id(self, id, params=None):
        url = f"{self.host}/user/{id}"
        return self.paginate(url, headers=self.headers, params=params)

    def get_repo_prs(self, org_key, repo_slug, params=None):
        url = f"{self.host}/repos/{org_key}/{repo_slug}/pulls"
        return self.paginate(url, headers=self.headers, params=params)

    def get_repo_commits(self, org_key, repo_slug, params=None):
        url = f"{self.host}/repos/{org_key}/{repo_slug}/commits"
        return self.paginate(url, headers=self.headers, params=params)

    def get_repo_issues(self, org_key, repo_slug, params=None):
        url = f"{self.host}/repos/{org_key}/{repo_slug}/issues"
        return self.paginate(url, headers=self.headers, params=params)

    def get_repo_artifacts(self, org_key, repo_slug, params=None, paginate=True):
        url = f"{self.host}/repos/{org_key}/{repo_slug}/actions/artifacts"
        if paginate is True:
            return self.paginate(url, headers=self.headers, params=params, list_key="artifacts")
        else:
            return self.session.get(url, headers=self.headers, params=params)

    def get_repo_secrets(self, org_key, repo_slug, params=None, paginate=True):
        url = f"{self.host}/repos/{org_key}/{repo_slug}/actions/secrets"
        if paginate is True:
            return self.paginate(url, headers=self.headers, params=params, list_key="secrets")
        else:
            return self.session.get(url, headers=self.headers, params=params)

    def get_repo_vars(self, org_key, repo_slug, params=None, paginate=True):
        url = f"{self.host}/repos/{org_key}/{repo_slug}/actions/variables"
        if paginate is True:
            return self.paginate(url, headers=self.headers, params=params, list_key="variables")
        else:
            return self.session.get(url, headers=self.headers, params=params)

    def get_repo_workflows(self, org_key, repo_slug, params=None, paginate=True):
        url = f"{self.host}/repos/{org_key}/{repo_slug}/actions/workflows"
        if paginate is True:
            return self.paginate(url, headers=self.headers, params=params, list_key="workflows")
        else:
            return self.session.get(url, headers=self.headers, params=params)

    def get_repo_workflow_runs(self, org_key, repo_slug, params=None, paginate=True):
        url = f"{self.host}/repos/{org_key}/{repo_slug}/actions/runs"
        if paginate is True:
            return self.paginate(url, headers=self.headers, params=params, list_key="workflow_runs")
        else:
            return self.session.get(url, headers=self.headers, params=params)

    def get_repo_runners(self, org_key, repo_slug, params=None, paginate=True):
        url = f"{self.host}/repos/{org_key}/{repo_slug}/actions/runners"
        if paginate is True:
            return self.paginate(url, headers=self.headers, params=params, list_key="runners")
        else:
            return self.session.get(url, headers=self.headers, params=params)

    def get_repo_runner_groups(self, org_key, repo_slug, params=None, paginate=True):
        url = f"{self.host}/repos/{org_key}/{repo_slug}/actions/runner-groups"
        if paginate is True:
            return self.paginate(url, headers=self.headers, params=params, list_key="runner_groups")
        else:
            return self.session.get(url, headers=self.headers, params=params)

    def get_repo_releases(self, org_key, repo_slug, params=None, paginate=True):
        url = f"{self.host}/repos/{org_key}/{repo_slug}/releases"
        if paginate is True:
            return self.paginate(url, headers=self.headers, params=params)
        else:
            return self.session.get(url, headers=self.headers, params=params)

    def get_repo_collaborators(self, org_key, repo_slug, params=None, paginate=True):
        url = f"{self.host}/repos/{org_key}/{repo_slug}/collaborators"
        if paginate is True:
            return self.paginate(url, headers=self.headers, params=params)
        else:
            return self.session.get(url, headers=self.headers, params=params)

    def get_repo_size(self, repo):
        repo_size = repo['size']
        return round(repo_size/1000, 2)

    def get_repo_tags(self, org_key, repo_slug, params=None):
        url = f"{self.host}/repos/{org_key}/{repo_slug}/tags"
        return self.paginate(url, headers=self.headers, params=params)

    def is_repo_archived(self, org_key, repo_slug):
        url = f"{self.host}/repos/{org_key}/{repo_slug}"
        response = self.paginate(url, headers=self.headers)

        if response.status_code == 200:
            repo_info = response.json()
            return repo_info.get('archived', False)
        response.raise_for_status()
        return False
