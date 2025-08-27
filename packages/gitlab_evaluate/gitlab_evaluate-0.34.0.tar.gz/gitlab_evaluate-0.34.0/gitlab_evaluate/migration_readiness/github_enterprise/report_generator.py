from sys import exit as sys_exit
import datetime
import xlsxwriter
from gitlab_evaluate.lib import utils
from gitlab_evaluate.migration_readiness.github_enterprise.evaluate import GithubEvaluateClient

class GithubReportGenerator:

    def __init__(self, host, token, filename=None, output_to_screen=False, processes=None):
        self.host = host
        self.api_page_size = 100
        self.github_client = GithubEvaluateClient(host, token)
        self.validate_token()
        if filename:
            self.workbook = xlsxwriter.Workbook(f'{filename}.xlsx')
        else:
            self.workbook = xlsxwriter.Workbook('github_evaluate_report')
        self.app_stats = self.workbook.add_worksheet('App Stats')
        self.align_left = self.workbook.add_format({'align': 'left'})
        self.header_format = self.workbook.add_format({'bg_color': 'black', 'font_color': 'white', 'bold': True, 'font_size': 10})
        self.users_sheet = self.workbook.add_worksheet('Users')
        self.teams_sheet = self.workbook.add_worksheet('Teams')
        self.orgs_sheet = self.workbook.add_worksheet('Organizations')
        self.repos_sheet = self.workbook.add_worksheet('Repositories')
        self.output_to_screen = output_to_screen
        self.using_admin_token = self.is_admin_token()
        self.processes = processes
        self.org_columns = [
            'Name',
            'ID',
            'URL',
            'Description',
            # v2
            'Repositories',
            'Packages',
            'Members',
            'Runners'
        ]
        self.team_columns = [
            'Org',
            'Name',
            'ID',
            'URL',
            'Description',
            # v2
            'Members'
        ]
        self.repo_columns = [
            'Org/User',
            'Personal',
            'ID',
            'URL',
            'last_activity_at',
            'Branches',
            'Commit Count',
            'Pull Requests',
            'Issues',
            'Repository Size in MB',
            'Tags',
            'Repository Archived',
            # v2
            'Artifacts',
            #'Secrets',
            #'Variables',
            'Workflows',
            'Workflow Runs',
            'Releases',
            # v3
            'Members',
            'Runners'
        ]
        self.user_columns = [
            'Username',
            'Email',
            'Admin',
            'Type',
            'JoinedAt',
            # v2
            'Packages',
            'Repositories'
        ]
        utils.write_headers(0, self.repos_sheet, self.repo_columns, self.header_format)
        utils.write_headers(0, self.users_sheet, self.user_columns, self.header_format)
        utils.write_headers(0, self.teams_sheet, self.team_columns, self.header_format)
        utils.write_headers(0, self.orgs_sheet, self.org_columns, self.header_format)

    def write_workbook(self):
        self.app_stats.autofit()
        self.repos_sheet.autofit()
        self.users_sheet.autofit()
        self.orgs_sheet.autofit()
        self.workbook.close()

    def get_app_stats(self):
        app_properties = {
            "installed_version": "N/A"
        }
        response = self.github_client.get_application_properties()
        if response.status_code != 200:
            print(f"Failed to fetch application properties: {response.status_code} - {response.text}")
        else:
            app_properties = response.json()
        
        report_stats = [
            ('Basic information from source', self.host),
            ('Customer', '<CUSTOMERNAME>'),
            ('Date Run', utils.get_date_run()),
            ('Source', 'Github'),
            ('Github Version', app_properties.get('installed_version')),
            ('Total Orgs', len(self.get_total_orgs())),
            ('Total Repositories', self.get_total_repositories()),
            ('Total Archived Repositories', self.get_total_archived_repositories()),
            ('Total Users', len(self.get_total_users())),
            ('Total Teams', len(self.get_total_teams()))
        ]

        for row, stat in enumerate(report_stats):
            self.app_stats.write(row, 0, stat[0])
            self.app_stats.write(row, 1, stat[1])

        return report_stats

    def get_total_orgs(self):
        params = {'per_page': self.api_page_size}
        print("Fetching all orgs...")
        response = self.github_client.get_orgs(params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch orgs: {response.status_code} - {response.text}")
        orgs = response.json()
        print(f"Retrieved {len(orgs)} orgs")

        # populate orgs with runners
        # Fetch org runners
        print(f"Fetching org runners")
        for org in orgs:
            org['total_runners'] = 0
            res = self.github_client.get_org_runners(org_key=org['login'])
            if res.status_code != 200:
                print(f"Failed to fetch {org['login']} org runners: {res.status_code} - {res.text}")
            else:
                org['total_runners'] = len(res.json())

        # populate orgs with members
        for org in orgs:
            org['total_members'] = 0
            res = self.github_client.get_org_members(org_key=org['login'])
            if res.status_code != 200:
                print(f"Failed to fetch {org['login']} org members: {res.status_code} - {res.text}")
            else:
                org['total_members'] = len(res.json())

        # populate orgs with repos
        for org in orgs:
            org['total_repos'] = 0
            res = self.github_client.get_org_repos(org_key=org['login'])
            if res.status_code != 200:
                print(f"Failed to fetch {org['login']} org repos: {res.status_code} - {res.text}")
            else:
                org['total_repos'] = len(res.json())

        # pupulate org packages
        for org in orgs:
            org['packages_count'] = 0
            res = self.github_client.get_org_packages(org_key=org['login'])
            if res.status_code != 200:
                print(f"Failed to fetch org {org['login']} packages: {res.status_code} - {res.text}")
            else:
                org['packages_count'] = len(res.json())

        return orgs

    def get_total_users(self):
        params = {'per_page': self.api_page_size}
        print("Fetching all users...")
        response = self.github_client.get_users(params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch users: {response.status_code} - {response.text}")

        users = response.json()
        
        print(f"Retrieved {len(users)} users")
        return users

    def get_total_teams(self):
        total_teams = []
        orgs = self.get_total_orgs()
        print("Fetching all teams for all orgs...")

        for org in orgs:
            org_key = org['login']
            params = {'per_page': self.api_page_size}

            response = self.github_client.get_org_teams(org_key, params=params)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch teams for org {org_key}: {response.status_code} - {response.text}")

            teams = response.json()
            for team in teams:
                team['parent_org_login'] = org['login']
            total_teams.extend(teams)

            print(f"Org {org_key}: Retrieved {len(total_teams)} teams")
        return total_teams

    def get_total_repositories(self):
        total_repos = 0
        orgs = self.get_total_orgs()
        users = self.get_total_users()
        print("Fetching total repositories for all orgs...")

        for org in orgs:
            org_key = org['login']
            params = {'per_page': self.api_page_size}
            response = self.github_client.get_org_repos(org_key, params=params)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch repositories for org {org_key}: {response.status_code} - {response.text}")

            repos = response.json()
            total_repos += len(repos)

            print(f"Org {org_key}: Retrieved {total_repos} repositories")

        print("Fetching total repositories for all users...")

        for user in users:
            user_key = user['login']
            params = {'per_page': self.api_page_size}

            response = self.github_client.get_user_repos(user_key, params=params)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch repositories for user {user_key}: {response.status_code} - {response.text}")

            repos = response.json()
            total_repos += len(repos)

            print(f"User {user_key}: Retrieved {total_repos} repositories")

        return total_repos

    def get_total_archived_repositories(self):
        archived_count = 0
        orgs = self.get_total_orgs()
        users = self.get_total_users()
        print("Fetching total archived repositories for all orgs...")

        for org in orgs:
            org_key = org['login']
            params = {'per_page': self.api_page_size}

            response = self.github_client.get_org_repos(org_key, params=params)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch repositories for org {org_key}: {response.status_code} - {response.text}")

            repos = response.json()
            for repo in repos:
                if repo.get('archived', False):
                    archived_count += 1

            print(f"Org {org_key}: Retrieved {archived_count} archived repositories")

        print("Fetching total archived repositories for all users...")

        for user in users:
            user_key = user['login']
            params = {'per_page': self.api_page_size}

            response = self.github_client.get_user_repos(user_key, params=params)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch repositories for user {user_key}: {response.status_code} - {response.text}")

            repos = response.json()
            for repo in repos:
                if repo.get('archived', False):
                    archived_count += 1

            print(f"User {user_key}: Retrieved {archived_count} archived repositories")

        return archived_count

    def handle_getting_data(self):
        params = {'per_page': self.api_page_size}

        # handling repos
        print("Fetching org data...")
        orgs = self.get_total_orgs()

        for org in orgs:
            org_key = org['login']
            print(f"Fetching data for org {org_key}...")
            self.handle_getting_repo_data(org_key, False)

        print("Fetching users data...")
        response_users = self.github_client.get_users(params=params)

        if response_users.status_code != 200:
            raise Exception(f"Failed to fetch users: {response_users.status_code} - {response_users.text}")

        users = response_users.json()

        for user in users:
            user_key = user['login']
            print(f"Fetching data for user {user_key}...")
            self.handle_getting_repo_data(user_key, True)

        # handling organizations
        print("Fetching organizations data...")
        for org in orgs:
            org_data = {
                'Name': org['login'],
                'ID': org['id'],
                'URL': org['url'],
                'Description': org['description'],
                # v2
                'Repositories': org['total_repos'],
                'Packages': org['packages_count'],
                'Members': org['total_members'],
                'Runners': org['total_runners']
            }
            utils.append_to_workbook(self.orgs_sheet, [org_data], self.org_columns)

        # handling teams
        print("Fetching team data...")
        teams = self.get_total_teams()
        for team in teams:
            # get team members
            members_count = 0
            res = self.github_client.get_team_members(org_key=team['parent_org_login'], team_key=team['name'])
            if res.status_code != 200:
                print(f"Failed to fetch team {team['name']} members: {res.status_code} - {res.text}")
            else:
                members_count = len(res.json())

            #
            team_data = {
                'Org': team['parent_org_login'],
                'Name': team['name'],
                'ID': team['id'],
                'URL': team['url'],
                'Description': team['description'],
                # v2
                'Members': members_count
            }
            utils.append_to_workbook(self.teams_sheet, [team_data], self.team_columns)

    def handle_getting_repo_data(self, owner_key, is_user_repo):
        params = {'per_page': self.api_page_size}
        total_repos = 0

        if is_user_repo is False:
            print(f"Fetching repositories for org {owner_key}...")

            response = self.github_client.get_org_repos(owner_key, params=params)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch repositories for org {owner_key}: {response.status_code} - {response.text}")

            repos = response.json()
            total_repos += len(repos)

            for repo in repos:
                print(f"Processing repository {repo['name']} in org {owner_key}...")
                self.write_repo_output_to_file(repo, False)

            # Print progress
            print(f"Org {owner_key}: Retrieved and processed {total_repos} repositories")
        else:
            print(f"Fetching repositories for user {owner_key}...")

            response = self.github_client.get_user_repos(owner_key, params=params)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch repositories for user {owner_key}: {response.status_code} - {response.text}")

            repos = response.json()
            total_repos += len(repos)

            for repo in repos:
                print(f"Processing repository {repo['name']} from user {owner_key}...")
                self.write_repo_output_to_file(repo, True)

            # Print progress
            print(f"User {owner_key}: Retrieved and processed {total_repos} repositories")


    def handle_getting_user_data(self):
        params = {'per_page': self.api_page_size}
        print("Fetching user data...")
        response = self.github_client.get_admin_users(params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch users: {response.status_code} - {response.text}")

        users = response.json()
        users = [user for user in users if user.get("type") != "Organization"]
        orgs = [user for user in users if user.get("type") == "Organization"]

        for user in users:
            user_details_res = self.github_client.get_user_by_id(user['id'])
            if user_details_res.status_code != 200:
                raise Exception(f"Failed to user details {user['id']}: {user_details_res.status_code} - {user_details_res.text}")
            user_details = user_details_res.json()
            
            # get user packages (we don' raise error on status != 200 when packages feature is disabled)
            # 404 is the status_code when it's disabled
            user_packages = False
            user_packages_res = self.github_client.get_user_packages(user['login'])
            if user_packages_res.status_code != 200:
                print(f"Failed to get user packages for user {user['login']}: {user_packages_res.status_code} - {user_packages_res.text}")
            else:
                user_packages = user_packages_res.json()
            
            user_repos = False
            user_repos_res = self.github_client.get_user_repos(user['login'])
            if user_repos_res.status_code != 200:
                print(f"Failed to get user repos for {user['login']}: {user_repos_res.status_code} - {user_repos_res.text}")
            else:
                user_repos = user_repos_res.json()

            user_data = {
                'Username': user['login'],
                'Email': user_details['email'],
                'Admin': user_details['site_admin'],
                'Type': user_details['type'],
                'JoinedAt': user_details['created_at'],
                # v2
                'Packages': 'N/A' if user_packages is False else len(user_packages),
                'Repositories': 'N/A' if user_repos is False else len(user_repos),
            }
            utils.append_to_workbook(self.users_sheet, [user_data], self.user_columns)

        print(f"Retrieved {len(users)} users")

    def write_repo_output_to_file(self, repo, is_user_repo):
        org_key = repo['owner']['login']
        repo_name = repo['name']

        # Get branches count
        branches_response = self.github_client.get_repo_branches(org_key, repo_name)
        if branches_response.status_code != 200:
            raise Exception(f"Failed to fetch branches for repo {repo_name}: {branches_response.status_code} - {branches_response.text}")
        branches = branches_response.json()

        # Get issues
        issues_response = self.github_client.get_repo_issues(org_key, repo_name)
        if issues_response.status_code != 200:
            raise Exception(f"Failed to fetch issues for repo {repo_name}: {issues_response.status_code} - {issues_response.text}")
        issues = issues_response.json()

        # Get pull requests count with pagination
        pull_requests = []
        params = {'per_page': self.api_page_size}
        print(f"Fetching pull requests for repo {repo_name}...")
        prs_response = self.github_client.get_repo_prs(org_key, repo_name, params=params)
        if prs_response.status_code != 200:
            raise Exception(f"Failed to fetch pull requests for repo {repo_name}: {prs_response.status_code} - {prs_response.text}")
        pull_requests = prs_response.json()
        print(f"Retrieved {len(pull_requests)} pull requests")

        # Get last commit information to determine last activity
        commits_response = self.github_client.get_repo_commits(org_key, repo_name)
        if commits_response.status_code != 200 and commits_response.status_code != 409:
            raise Exception(f"Failed to fetch commits for repo {repo_name}: {commits_response.status_code} - {commits_response.text}")
        
        # default values for empty repo
        commits = []
        last_activity = None
        commit_count = 0

        # if repo not empty
        if commits_response.status_code != 409:
            commits = commits_response.json()
            last_activity = commits[0]['commit']['author']['date'] if commits else 'N/A'
            if last_activity != 'N/A':
                dt = datetime.datetime.strptime(last_activity, "%Y-%m-%dT%H:%M:%SZ")
                dt = dt.replace(tzinfo=datetime.timezone.utc)
                last_activity = datetime.datetime.fromtimestamp(dt.timestamp()).strftime('%c')
            commit_count = len(commits)

        # Get repository size
        repository_size = self.github_client.get_repo_size(repo)

        # Get tags count
        tags_response = self.github_client.get_repo_tags(org_key, repo_name)
        if tags_response.status_code != 200:
            raise Exception(f"Failed to fetch tags for repo {repo_name}: {tags_response.status_code} - {tags_response.text}")
        tags = tags_response.json()

        #
        # Optional features:
        # anything linked GH actions will return 500/404 errors until you enable actions in the GHES admin GUI
        # so we don't raise Exception on status != 200 ... we only print a warning
        #
        # Additionally regarding secrets and variables, even the site admin has no access to those by default,
        # unless the site admin is explicitely added as a repo admin
        #
        # Organisation runners and runner groups also require admin membership, even for the site admin
        #
        artifacts_res = self.github_client.get_repo_artifacts(org_key, repo_name, paginate=False)
        artifacts = False
        if artifacts_res.status_code != 200:
            print(f"Failed to fetch artifacts for repo {repo_name}: {artifacts_res.status_code} - {artifacts_res.text}")
        else:
            artifacts = artifacts_res.json()
        
        # Even if you are a site admin, this is not enough to access secrets, you will have to be added as a repo admin member
        #secrets_res = self.github_client.get_repo_secrets(org_key, repo_name, paginate=False)
        #secrets = False
        #if secrets_res.status_code != 200:
        #    print(f"Failed to fetch secrets for repo {repo_name}: {secrets_res.status_code} - {secrets_res.text}")
        #else:
        #    secrets = secrets_res.json()
        
        # Even if you are a site admin, this is not enough to access variables, you will have to be added as a repo admin member
        #variables_res = self.github_client.get_repo_vars(org_key, repo_name, paginate=False)
        #variables = False
        #if variables_res.status_code != 200:
        #    print(f"Failed to fetch vars for repo {repo_name}: {variables_res.status_code} - {variables_res.text}")
        #else:
        #    variables = variables_res.json()
        
        workflow_res = self.github_client.get_repo_workflows(org_key, repo_name, paginate=False)
        workflows = False
        if workflow_res.status_code != 200:
            print(f"Failed to fetch workflow for repo {repo_name}: {workflow_res.status_code} - {workflow_res.text}")
        else:
            workflows = workflow_res.json()
        
        workflow_runs_res = self.github_client.get_repo_workflow_runs(org_key, repo_name, paginate=False)
        workflow_runs = False
        if workflow_runs_res.status_code != 200:
            print(f"Failed to fetch workflow runs for repo {repo_name}: {workflow_runs_res.status_code} - {workflow_runs_res.text}")
        else:
            workflow_runs = workflow_runs_res.json()
        
        releases_res = self.github_client.get_repo_releases(org_key, repo_name)
        releases = False
        if releases_res.status_code != 200:
            print(f"Failed to fetch releases for repo {repo_name}: {releases_res.status_code} - {releases_res.text}")
        else:
            releases = releases_res.json()
        
        members_res = self.github_client.get_repo_collaborators(org_key, repo_name)
        members = False
        if members_res.status_code != 200:
            print(f"Failed to fetch members for repo {repo_name}: {members_res.status_code} - {members_res.text}")
        else:
            members = members_res.json()
        
        runners_res = self.github_client.get_repo_runners(org_key, repo_name)
        runners = False
        if runners_res.status_code != 200:
            print(f"Failed to fetch runners for repo {repo_name}: {runners_res.status_code} - {runners_res.text}")
        else:
            runners = runners_res.json()

        repo_data = {
            'Org/User': repo['owner']['login'],
            'Personal': is_user_repo,
            'ID': repo['id'],
            'URL': repo['html_url'],
            'last_activity_at': last_activity,
            'Branches': len(branches),
            'Commit Count': commit_count,
            'Pull Requests': len(pull_requests),
            'Issues': len(issues),
            'Repository Size in MB': repository_size,
            'Tags': len(tags),
            'Repository Archived' : self.github_client.is_repo_archived(org_key, repo_name),
            # v2
            'Artifacts' : "N/A" if artifacts is False else artifacts['total_count'],
            #'Secrets' : "N/A" if secrets is False else secrets['total_count'],
            #'Variables' : "N/A" if variables is False else variables['total_count'],
            'Workflows' : "N/A" if workflows is False else workflows['total_count'],
            'Workflow Runs' : "N/A" if workflow_runs is False else workflow_runs['total_count'],
            'Releases' : "N/A" if releases is False else len(releases),
            # v3
            'Members': "N/A" if members is False else len(members),
            'Runners': "N/A" if runners is False else len(runners),
        }
        utils.append_to_workbook(self.repos_sheet, [repo_data], self.repo_columns)
        if self.output_to_screen:
            print(f"Repository Data: {repo_data}")

    def validate_token(self):
        response = self.github_client.get_users()
        if response.status_code != 200:
            print("Invalid token. Exiting...")
            sys_exit(1)

    def is_admin_token(self):
        response = self.github_client.get_admin_stats()
        return response.status_code == 200
