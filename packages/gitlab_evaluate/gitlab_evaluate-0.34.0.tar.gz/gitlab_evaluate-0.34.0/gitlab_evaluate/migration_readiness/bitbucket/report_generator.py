from sys import exit as sys_exit
import datetime
import xlsxwriter
from gitlab_evaluate.lib import utils
from gitlab_evaluate.migration_readiness.bitbucket.evaluate import BitbucketEvaluateClient

class BitbucketReportGenerator:

    def __init__(self, host, token, filename=None, output_to_screen=False, processes=None):
        self.host = host
        self.bitbucket_client = BitbucketEvaluateClient(host, token)
        self.validate_token()
        if filename:
            self.workbook = xlsxwriter.Workbook(f'{filename}.xlsx')
        else:
            self.workbook = xlsxwriter.Workbook('bitbucket_evaluate_report')
        self.app_stats = self.workbook.add_worksheet('App Stats')
        self.align_left = self.workbook.add_format({'align': 'left'})
        self.header_format = self.workbook.add_format({'bg_color': 'black', 'font_color': 'white', 'bold': True, 'font_size': 10})
        self.users = self.workbook.add_worksheet('Users')
        self.raw_output = self.workbook.add_worksheet('Raw Project Data')
        self.output_to_screen = output_to_screen
        self.using_admin_token = self.is_admin_token()
        self.processes = processes
        self.columns = [
            'Project',
            'ID',
            'URL',
            'last_activity_at',
            'Branches',
            'Commit Count',
            'Pull Requests',
            'Repository Size in MB',
            'Tags',
            'Repository Archived'
        ]
        self.user_headers = ['Username', 'Email', 'State']
        utils.write_headers(0, self.raw_output, self.columns, self.header_format)
        utils.write_headers(0, self.users, self.user_headers, self.header_format)

    def write_workbook(self):
        self.app_stats.autofit()
        self.raw_output.autofit()
        self.users.autofit()
        self.workbook.close()

    def get_app_stats(self):
        '''
            Gets Bitbucket instance stats
        '''
        response = self.bitbucket_client.get_application_properties()

        if response.status_code != 200:
            raise Exception(f"Failed to fetch application properties: {response.status_code} - {response.text}")

        app_properties = response.json()

        report_stats = [
            ('Basic information from source', self.host),
            ('Customer', '<CUSTOMERNAME>'),
            ('Date Run', utils.get_date_run()),
            ('Source', 'Bitbucket'),
            ('Bitbucket Version', app_properties.get('version')),
            ('Total Projects', len(self.get_total_projects())),
            ('Total Repositories', self.get_total_repositories()),
            ('Total Archived Repositories', self.get_total_archived_repositories())
        ]

        for row, stat in enumerate(report_stats):
            self.app_stats.write(row, 0, stat[0])
            self.app_stats.write(row, 1, stat[1])

        return report_stats

    def get_total_projects(self):
        all_projects = []
        params = {'limit': 100}
        print("Fetching all projects...")
        while True:
            response = self.bitbucket_client.get_projects(params=params)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch projects: {response.status_code} - {response.text}")

            projects = response.json()
            all_projects.extend(projects['values'])

            print(f"Retrieved {len(all_projects)} projects so far...")

            # Check if there's a next page
            if 'nextPageStart' in projects:
                params['start'] = projects['nextPageStart']
            else:
                break  # No more pages
        return all_projects

    def get_total_repositories(self):
        total_repos = 0
        projects = self.get_total_projects()
        print("Fetching total repositories for all projects...")

        for project in projects:
            project_key = project['key']
            params = {'limit': 100}
            while True:
                response = self.bitbucket_client.get_repos(project_key, params=params)

                if response.status_code != 200:
                    raise Exception(f"Failed to fetch repositories for project {project_key}: {response.status_code} - {response.text}")

                repos = response.json()
                total_repos += len(repos['values'])

                print(f"Project {project_key}: Retrieved {total_repos} repositories so far...")

                # Check if there's a next page
                if 'nextPageStart' in repos:
                    params['start'] = repos['nextPageStart']
                else:
                    break  # No more pages
        return total_repos

    def get_total_archived_repositories(self):
        archived_count = 0
        projects = self.get_total_projects()
        print("Fetching total archived repositories for all projects...")

        for project in projects:
            project_key = project['key']
            params = {'limit': 100}

            while True:
                response = self.bitbucket_client.get_repos(project_key, params=params)

                if response.status_code != 200:
                    raise Exception(f"Failed to fetch repositories for project {project_key}: {response.status_code} - {response.text}")

                repos = response.json()
                for repo in repos.get('values', []):
                    if repo.get('archived', False):
                        archived_count += 1

                print(f"Project {project_key}: Retrieved {archived_count} archived repositories so far...")

                # Check if there's a next page
                if 'nextPageStart' in repos:
                    params['start'] = repos['nextPageStart']
                else:
                    break  # No more pages
        return archived_count

    def handle_getting_data(self):
        params = {'limit': 100}
        print("Fetching project data...")
        while True:
            response = self.bitbucket_client.get_projects(params=params)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch projects: {response.status_code} - {response.text}")

            projects = response.json()

            for project in projects['values']:
                project_key = project['key']
                print(f"Fetching data for project {project_key}...")
                self.handle_getting_repo_data(project_key)

            # Check if there's a next page
            if 'nextPageStart' in projects:
                params['start'] = projects['nextPageStart']
            else:
                break  # No more pages

    def handle_getting_repo_data(self, project_key):
        params = {'limit': 100}
        total_repos = 0
        print(f"Fetching repositories for project {project_key}...")

        while True:
            response = self.bitbucket_client.get_repos(project_key, params=params)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch repositories for project {project_key}: {response.status_code} - {response.text}")

            repos = response.json()
            total_repos += len(repos['values'])

            for repo in repos['values']:
                print(f"Processing repository {repo['slug']} in project {project_key}...")
                self.write_output_to_files(repo)

            # Print progress
            print(f"Project {project_key}: Retrieved and processed {total_repos} repositories so far...")

            # Check if there's a next page
            if 'nextPageStart' in repos:
                params['start'] = repos['nextPageStart']
            else:
                break  # No more pages

    def handle_getting_user_data(self):
        params = {'limit': 100}
        print("Fetching user data...")
        while True:
            response = self.bitbucket_client.get_admin_users(params=params)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch users: {response.status_code} - {response.text}")

            users = response.json()

            for user in users['values']:
                user_data = {
                    'Username': user['name'],
                    'Email': user.get('emailAddress', 'N/A'),
                    'State': user['active']
                }
                utils.append_to_workbook(self.users, [user_data], self.user_headers)

            print(f"Retrieved {len(users['values'])} users so far...")

            # Check if there's a next page
            if 'nextPageStart' in users:
                params['start'] = users['nextPageStart']
            else:
                break  # No more pages

    def get_branches(self, project_key, repo_slug):
        """Fetch all branches for a repository with pagination."""
        branches = []
        params = {'limit': 100}
        print(f"Fetching branches for repo {repo_slug}...")
        
        while True:
            branches_response = self.bitbucket_client.get_branches(project_key, repo_slug, params=params)
            if branches_response.status_code != 200:
                raise Exception(f"Failed to fetch branches for repo {repo_slug}: {branches_response.status_code} - {branches_response.text}")

            response_json = branches_response.json()
            branches.extend(response_json['values'])
            print(f"Retrieved {len(branches)} branches so far...")

            # Check if there's a next page
            if 'nextPageStart' in response_json and response_json['nextPageStart'] is not None:
                params['start'] = response_json['nextPageStart']
            else:
                break
        
        return branches

    def get_pull_requests(self, project_key, repo_slug):
        """Fetch all pull requests for a repository with pagination."""
        pull_requests = []
        params = {'limit': 100}
        print(f"Fetching pull requests for repo {repo_slug}...")
        
        while True:
            prs_response = self.bitbucket_client.get_prs(project_key, repo_slug, params=params)
            if prs_response.status_code != 200:
                raise Exception(f"Failed to fetch pull requests for repo {repo_slug}: {prs_response.status_code} - {prs_response.text}")

            response_json = prs_response.json()
            pull_requests.extend(response_json['values'])
            print(f"Retrieved {len(pull_requests)} pull requests so far...")

            # Check if there's a next page
            if 'nextPageStart' in response_json and response_json['nextPageStart'] is not None:
                params['start'] = response_json['nextPageStart']
            else:
                break
        
        return pull_requests

    def get_commits(self, project_key, repo_slug):
        """Fetch all commits for a repository with pagination and determine last activity."""
        commits = []
        last_activity = 'N/A'
        params = {'limit': 100}
        print(f"Fetching commits for repo {repo_slug}...")
        
        while True:
            commits_response = self.bitbucket_client.get_commits(project_key, repo_slug, params=params)
            if commits_response.status_code != 200:
                raise Exception(f"Failed to fetch commits for repo {repo_slug}: {commits_response.status_code} - {commits_response.text}")

            response_json = commits_response.json()
            commits.extend(response_json['values'])

            # Determine last activity from the first commit (most recent)
            if commits and last_activity == 'N/A':
                last_activity = commits[0]['committerTimestamp']

            print(f"Retrieved {len(commits)} commits so far...")

            # Check if there's a next page
            if 'nextPageStart' in response_json and response_json.get('nextPageStart') is not None:
                params['start'] = response_json.get('nextPageStart')
            else:
                break
        
        # Convert timestamp to readable format
        if last_activity != 'N/A':
            last_activity = datetime.datetime.fromtimestamp(last_activity/1000).strftime('%c')
        
        return commits, last_activity

    def get_tags(self, project_key, repo_slug):
        """Fetch all tags for a repository with pagination."""
        tags = []
        params = {'limit': 100}
        print(f"Fetching tags for repo {repo_slug}...")
        
        while True:
            tags_response = self.bitbucket_client.get_tags(project_key, repo_slug, params=params)
            if tags_response.status_code != 200:
                raise Exception(f"Failed to fetch tags for repo {repo_slug}: {tags_response.status_code} - {tags_response.text}")

            response_json = tags_response.json()
            tags.extend(response_json['values'])
            print(f"Retrieved {len(tags)} tags so far...")

            # Check if there's a next page
            if 'nextPageStart' in response_json and response_json['nextPageStart'] is not None:
                params['start'] = response_json['nextPageStart']
            else:
                break
        
        return tags

    def write_output_to_files(self, repo):
        """Collect repository data and write to output files with error handling."""
        project_key = repo['project']['key']
        repo_slug = repo['slug']
        
        # Initialize default values
        branches, pull_requests, commits = [], [], []
        tags, last_activity = [], 'N/A'
        commit_count = 0
        repository_size = 0
        is_archived = False
        
        try:
            # Get branches
            branches = self.get_branches(project_key, repo_slug)
        except Exception as e:
            print(f"Error fetching branches: {str(e)}")
        
        try:
            # Get pull requests
            pull_requests = self.get_pull_requests(project_key, repo_slug)
        except Exception as e:
            print(f"Error fetching pull requests: {str(e)}")
        
        try:
            # Get commits and last activity
            commits, last_activity = self.get_commits(project_key, repo_slug)
            commit_count = len(commits)
        except Exception as e:
            print(f"Error fetching commits: {str(e)}")
        
        try:
            # Get tags
            tags = self.get_tags(project_key, repo_slug)
        except Exception as e:
            print(f"Error fetching tags: {str(e)}")
        
        try:
            # Get repository size
            repository_size = self.bitbucket_client.get_repo_size(repo)
        except Exception as e:
            print(f"Error fetching repository size: {str(e)}")
        
        try:
            # Check if repository is archived
            is_archived = self.bitbucket_client.is_repo_archived(project_key, repo_slug)
        except Exception as e:
            print(f"Error checking if repository is archived: {str(e)}")
        
        # Compile repository data
        repo_data = {
            'Project': repo['project']['name'],
            'ID': repo['id'],
            'URL': repo['links']['self'][0]['href'],
            'last_activity_at': last_activity,
            'Branches': len(branches),
            'Commit Count': commit_count,
            'Pull Requests': len(pull_requests),
            'Repository Size in MB': repository_size,
            'Tags': len(tags),
            'Repository Archived': is_archived
        }
        
        try:
            # Write data to workbook
            utils.append_to_workbook(self.raw_output, [repo_data], self.columns)
            if self.output_to_screen:
                print(f"Repository Data: {repo_data}")
        except Exception as e:
            print(f"Error writing output to files: {str(e)}")

    def validate_token(self):
        response = self.bitbucket_client.get_users()
        if response.status_code != 200:
            print("Invalid token. Exiting...")
            sys_exit(1)

    def is_admin_token(self):
        response = self.bitbucket_client.get_admin_users()
        return response.status_code == 200
