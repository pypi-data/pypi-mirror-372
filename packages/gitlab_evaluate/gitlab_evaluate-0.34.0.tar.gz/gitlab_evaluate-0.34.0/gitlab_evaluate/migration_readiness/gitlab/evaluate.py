import os
import sys
import sqlite3
from traceback import print_exc
from copy import deepcopy as copy
from json import dumps as json_dumps
from dacite import from_dict
from httpx import Client
from gitlab_ps_utils.misc_utils import safe_json_response
from gitlab_ps_utils.dict_utils import dig
from gitlab_evaluate import log
from gitlab_evaluate.lib import utils, db_utils
from gitlab_evaluate.migration_readiness.gitlab.flag_remediation import FlagRemediationMessages
from gitlab_evaluate.lib.api_models.user import User
from gitlab_evaluate.migration_readiness.gitlab import limits
from gitlab_evaluate.migration_readiness.gitlab.queries import *
from gitlab_evaluate.migration_readiness.gitlab import glapi
from gitlab_evaluate.migration_readiness.gitlab import constants
from gitlab_evaluate.migration_readiness.gitlab.data_classes.project import Project

class EvaluateApi():
    gitlab_api = glapi
    app_api_url = "/application/statistics"
    app_ver_url = "/version"

    supported_package_types = ['generic', 'npm', 'pypi', 'maven', 'helm']

    def __init__(self, ssl_verify=True, retain_db=False):
        self.setup_db(retain_db=retain_db)
        if ssl_verify:
            self.gitlab_api.client = Client(verify=ssl_verify)

    def setup_db(self, retain_db=False):
        if retain_db:
            log.info("Retaining DB from previous run")
            if not os.path.exists('gitlab.db'):
                log.error("No database found from previous run. Exiting")
                sys.exit(1)
        else:
            if os.path.exists('gitlab.db'):
                os.remove('gitlab.db')
            con = sqlite3.connect('gitlab.db', check_same_thread=False)
            cur = con.cursor()
            cur.execute(f"CREATE TABLE users({db_utils.schema_from_dataclass(User, primary_key='username')})")
            cur.execute(f"CREATE TABLE projects({db_utils.schema_from_dataclass(Project, primary_key='id')})")
            cur.execute(f"CREATE TABLE flagged_projects({db_utils.schema_from_dataclass(Project, primary_key='id')})")
            cur.execute(f"CREATE TABLE reports({db_utils.schema_from_list(constants.REPORT_HEADERS, primary_key='project')})")
            con.commit()
            con.close()


    def insert_project_data(self, project):
        """
            Function to store the job and job type in SQLite
            and then remove the processed job from the queue table
        """
        connection, cursor = utils.sqlite_connection('gitlab.db')
        try:
            insert_query = f"INSERT or IGNORE INTO projects VALUES {tuple(from_dict(Project, project).to_dict().values())}"
            cursor.execute(insert_query)
            connection.commit()
        except Exception as e:
            print("\t\t***Exception saving project data")
            print(e)
            print(print_exc())

    def insert_flagged_project_data(self, project):
        """
            Function to store the job and job type in SQLite
            and then remove the processed job from the queue table
        """
        connection, cursor = utils.sqlite_connection('gitlab.db')
        try:
            insert_query = f"INSERT or IGNORE INTO flagged_projects VALUES {tuple(from_dict(Project, project).to_dict().values())}"
            cursor.execute(insert_query)
            connection.commit()
        except Exception as e:
            print("\t\t***Exception saving flagged project data")
            print(e)
            print(print_exc())

    def insert_user_data(self, user: User):
        """
            Function to store the job and job type in SQLite
            and then remove the processed job from the queue table
        """
        connection, cursor = utils.sqlite_connection('gitlab.db')
        try:
            insert_query = f"INSERT or IGNORE INTO users VALUES {tuple(str(v) for v in user.to_dict().values())}"
            cursor.execute(insert_query)
            connection.commit()
        except Exception as e:
            print("\t\t***Exception saving user data")
            print(e)
            print(print_exc())

    def insert_report_data(self, project, reason):
        """
            Function to store the job and job type in SQLite
            and then remove the processed job from the queue table
        """
        connection, cursor = utils.sqlite_connection('gitlab.db')
        try:
            insert_query = f"INSERT or IGNORE INTO reports VALUES ('{project}', \"{reason}\")"
            cursor.execute(insert_query)
            connection.commit()
        except Exception as e:
            print("\t\t***Exception saving report data")
            print(e)
            print(print_exc())

    # Functions - Return API Data
    # Gets the X-Total from the statistics page with the -I on a curl
    def check_x_total_value_update_dict(self, check_func, p, host, token, api=None, value_column_name="DEFAULT_VALUE", over_column_name="DEFAULT_COLUMN_NAME", results={}):
        flag = False
        full_path = p.get('full_path')
        pid = p.get('id')
        if api:
            count = self.get_total_count(
                host, token, api, full_path, value_column_name, pid)
        else:
            count = results.get(value_column_name, 0)
        log.info(f"{full_path} - {value_column_name} retrieved count: {count}")
        if count is not None:
            num_over = check_func(count)
            if num_over:
                flag = True
            results[value_column_name] = count
            results[over_column_name] = num_over
        else:
            log.debug(
                f"No '{value_column_name}' retrieved for project '{full_path}' (ID: {pid})")
        return flag

    def check_count_stats(self, check_func, p, value_column_name="DEFAULT_VALUE", over_column_name="DEFAULT_COLUMN_NAME", results={}):
        """
            Compare data retrieved from project statistics with the provided threshold (using check_func)
        """
        flag = False
        full_path = p.get('full_path')
        count = dig(p, value_column_name, 'count', 0)
        log.info(f"{full_path} - {value_column_name} retrieved count: {count}")
        if count is not None:
            num_over = check_func(count)
            if num_over:
                flag = True
            results[value_column_name] = count
            results[over_column_name] = num_over
        else:
            log.debug(
                f"No '{value_column_name}' retrieved for project '{full_path}' (ID: {p.get('id')})")
        return flag

    def get_total_count(self, host, token, api, full_path, entity, project_id=None):
        formatted_entity = utils.to_camel_case(entity)
        query = {
            "query": """
                query {
                    project(fullPath: "%s") {
                        name,
                        %s {
                            count
                        }
                    }
                }
            """ % (full_path, formatted_entity)
        }

        gql_resp = safe_json_response(self.gitlab_api.generate_post_request(host, token, None, json_dumps(query), graphql_query=True))
        if count := dig(gql_resp, 'data', 'project', formatted_entity, 'count'):
            return count

        log.debug(
            f"Could not retrieve total '{api}' count via GraphQL, using API instead")
        return self.gitlab_api.get_count(host, token, api)

    def get_all_projects_by_graphql(self, source, token, full_path=None):
        after = ""
        levels = []
        try:
            while True:
                if full_path:
                    query = generate_group_project_query(full_path, after)
                    levels = ['data', 'group', 'projects', 'nodes']
                else:
                    query = generate_all_projects_query(after)
                    levels = ['data', 'projects', 'nodes']
                if resp := safe_json_response(
                        self.gitlab_api.generate_post_request(source, token, None, data=json_dumps(query), graphql_query=True)):
                    yield from dig(resp, *levels, default=[])
                    page_info = dig(resp, *levels[:-1], 'pageInfo', default={})
                    if cursor := page_info.get('endCursor'):
                        after = cursor
                    if not page_info.get('hasNextPage', False):
                        break
        except Exception as e:
            log.error(f"Failed to get all projects: {e}\n{print_exc()}")

    def get_all_container_tags(self, full_path, host, token):
        query = generate_container_registry_tag_count(full_path)
        levels = ['data', 'project', 'containerRepositories', 'nodes']
        log.info(f"Retrieving {full_path} registry repos")
        if resp := safe_json_response(
                self.gitlab_api.generate_post_request(host, token, None, data=json_dumps(query), graphql_query=True)):
            if tags := dig(resp, *levels, default=[]):
                return tags
            log.info(f"No tags for project '{full_path}'")
            return []

    def check_container_image_tags(self, host, token, project, results={}):
        """
            Retrieves total container image tag count
            and checks container registry size and return a flag if it is over a threshold.
        """
        total_tags = sum(x.get('tagsCount', 0) for x in self.get_all_container_tags(project.get('full_path'), host, token))
        container_registry_size = results.get('container_registry_size', 0)
        flag = False
        if total_tags is not None:
            num_over = utils.check_registry_size(container_registry_size)
            if num_over:
                flag = True
            results["container_tag_count"] = total_tags
            results["container_registry_size"] = container_registry_size
            results["container_registry_size_over"] = num_over
        return flag

    def genericGet(self, host, token, api):
        return safe_json_response(self.gitlab_api.generate_get_request(host=host, token=token, api=api))

    def getApplicationInfo(self, host, token):
        return self.genericGet(host, token, self.app_api_url)

    def getVersion(self, host, token):
        return self.genericGet(host, token, self.app_ver_url)

    def getArchivedProjectCount(self, host, token):
        if resp := self.gitlab_api.generate_get_request(host=host, token=token, api='projects?archived=True'):
            result = resp.headers.get('X-Total')
            return result

    def get_total_project_count(self, host, token, group_id):
        if resp := self.gitlab_api.generate_get_request(host=host, token=token, api=f'/groups/{group_id}/projects'):
            result = resp.headers.get('X-Total')
            return result

    def build_initial_results(self, project):
        return {
            'project': project.get('name'),
            'id': project.get('id'),
            'archived': project.get('archived'),
            'last_activity_at': project.get('last_activity_at'),
            'url': project.get('web_url'),
            'namespace': dig(project, 'namespace', 'full_path'),
        }

    def get_all_project_data(self, host, token, p):

        results = {}
        flags = []
        messages = ''
        if isinstance(p, dict) and p:
            p = utils.nested_snake_case(p)
            results = self.build_initial_results(p)

            pid = int(p.get('id', '').split('/')[-1])
            p['id'] = pid

            try:
                # Get project REST stats
                self.get_project_rest_stats(host, token, p, results)
                messages = FlagRemediationMessages(p.get('name'))

                if stats := p.get('statistics'):
                    results['packages_size'] = stats.get(
                        "packages_size", 0)
                    results['container_registry_size'] = stats.get(
                        "container_registry_size", 0)
                    self.get_extra_stats(stats, results)

                # Get number of pipelines per project
                pipeline_endpoint = f"projects/{pid}/pipelines"
                flags.append(self.handle_check(
                    messages,
                    self.check_count_stats(
                        utils.check_num_pl, p, "pipelines", "pipelines_over", results),
                    "pipelines",
                    limits.PIPELINES_COUNT))

                # Get number of issues per project
                issues_endpoint = f"projects/{pid}/issues"
                flags.append(self.handle_check(
                    messages,
                    self.check_count_stats(
                        utils.check_num_issues, p, "issues", "issues_over", results),
                    "issues",
                    limits.ISSUES_COUNT))

                # Get number of branches per project
                branches_endpoint = f"projects/{pid}/repository/branches"
                flags.append(self.handle_check(
                    messages,
                    self.check_x_total_value_update_dict(
                        utils.check_num_br, p, host, token, branches_endpoint, "branches", "branches_over", results),
                    "branches",
                    limits.BRANCHES_COUNT))

                # Get number of commits per project
                flags.append(self.handle_check(
                    messages,
                    self.check_x_total_value_update_dict(
                        utils.check_num_commits, p, host, token, None, "commits", "commits_count_over", results),
                    "commits",
                    limits.COMMITS_COUNT))

                # Get number of merge requests per project
                mrs_endpoint = f"projects/{pid}/merge_requests"
                flags.append(self.handle_check(
                    messages,
                    self.check_count_stats(
                        utils.check_num_mr, p, "merge_requests", "merge_requests_over", results),
                    "merge_requests",
                    limits.MERGE_REQUESTS_COUNT))

                # Get number of tags per project
                tags_endpoint = f"projects/{pid}/repository/tags"
                flags.append(self.handle_check(
                    messages,
                    self.check_x_total_value_update_dict(
                        utils.check_num_tags, p, host, token, tags_endpoint, "tags", "tags_over", results),
                    "tags",
                    limits.TAGS_COUNT))

                # Get list of package types
                self.handle_packages(p, pid,
                                     messages, flags, results)

                # Check repository size
                flags.append(self.handle_check(
                    messages,
                    self.check_x_total_value_update_dict(
                        utils.check_repository_size, p, host, token, None, "repository_size", "repository_size_over", results),
                    "repository_size",
                    limits.REPOSITORY_SIZE))

                # Check storage size
                flags.append(self.handle_check(
                    messages,
                    self.check_x_total_value_update_dict(
                        utils.check_storage_size, p, host, token, None, "storage_size", "storage_size_over", results),
                    "storage_size",
                    limits.STORAGE_SIZE))

                # Get total packages size
                flags.append(self.handle_check(
                    messages,
                    self.check_x_total_value_update_dict(
                        utils.check_packages_size, p, host, token, None, "packages_size", "packages_size_over", results),
                    "packages_size",
                    limits.PACKAGES_SIZE))

                # Get total containers size
                flags.append(self.handle_check(
                    messages,
                    self.check_container_image_tags(
                        host, token, p, results),
                    "container_registry_size",
                    limits.CONTAINERS_SIZE))
                self.insert_project_data(results)
                if True in flags:
                    # Write data to the flagged_projects and report database tables
                    self.insert_flagged_project_data(results)
                    self.insert_report_data(
                        results['project'], messages.generate_report_entry())
            except Exception:
                log.error(
                    f"Failed to get all project {pid} data: {print_exc()}")
            finally:
                return flags, messages, results
        else:
            return flags, messages, results

    def get_project_rest_stats(self, host, token, project, my_dict):
        project_path = project.get('fullPath')
        pid = project.get('id')
        try:
            if result := safe_json_response(self.gitlab_api.generate_get_request(host=host, api="", token=token, url=f"{host}/api/v4/projects/{pid}")):
                if kind := result.get("namespace"):
                    my_dict.update({"kind": kind.get("kind")})

                # Get Mirrors
                my_dict['mirror'] = result.get('mirror', False)
            else:
                log.error(
                    f"Could not retrieve project '{project_path}' (ID: {pid}) REST stats: {result}")
        except Exception:
            log.error(
                f"Failed to retrieve project '{project_path}' (ID: {pid}) REST stats: {print_exc()}")

    # Get extra project stats
    def get_extra_stats(self, stats, results):
        export_total = 0
        for k, v in stats.items():
            updated_dict_entry = {
                k: v, k + "_over": utils.check_size(k, v)}
            results.update(updated_dict_entry)

            # If 'k' is an item that would be part of the export, add to running total
            if k in [
                "repository_size",
                "wiki_size",
                "lfs_objects_size",
                "snippets_size",
                "uploads_size"
            ]:
                export_total += int(v)

        # Write running total to my_dict
        export_total_key = "estimated_export_size"
        results.update({f"{export_total_key}": export_total})

        # 5Gb
        results.update({f"{export_total_key}_over": utils.check_size(
            export_total_key, export_total)})

        # 10Gb
        results.update({f"{export_total_key}_s3_over": utils.check_size(
            f"{export_total_key}_s3", export_total)})

    def get_token_owner(self, host, token):
        return self.genericGet(host, token, "user")

    def handle_check(self, messages, flagged_asset, asset_type, flag_condition):
        if flagged_asset == True:
            messages.add_flag_message(asset_type, flag_condition)
        return flagged_asset

    def get_user_data(self, u):
        if u.get('email') is None:
            u['email'] = u.get('public_email')
        return from_dict(data_class=User, data=u)

    def get_result_value(self, results, value_column_name):
        key_mapping = {
            'Storage': 'storage_size',
            'Repository': 'repository_size',
            'Packages': 'packages_size',
            'Commits': 'commit_count',
            'Containers': 'container_registry_size'
        }

        # Get the actual key to use in results
        actual_key = key_mapping.get(value_column_name, value_column_name)

        # Return the value from results or 0 if not found
        return results.get(actual_key, 0)

    def handle_packages(self, project, pid, messages, flags, results):
        # Extract packages from the GraphQL response:
        packages_data = project.get('packages', {}).get('nodes', [])
        if not packages_data:
            # No packages found, so report "N/A"
            results['package_types_in_use'] = "N/A"
            return

        # If packages are present, collect their types
        packages_in_use = set()
        for package in packages_data:
            pkg_type = package.get("package_type", "")
            if pkg_type:
                packages_in_use.add(pkg_type)
            else:
                log.error(
                    f"Project {pid} package missing 'package_type' field: {package}")

            results['package_types_in_use'] = ", ".join(
                packages_in_use) if packages_in_use else "N/A"
            # If a package type is found that doesn't match the constant in the class, raise a flag
            any_unsupported_packages = any(
                p.lower() not in self.supported_package_types for p in packages_in_use)

            if packages_in_use and any_unsupported_packages:
                flags.append(True)
                self.handle_check(messages, True, "packages",
                                  copy(results['package_types_in_use']))

    def get_specific_group_stats_response(self, host, token, group_id):
        '''
            Gets stats of a specific group when using a non-admin token

            Some of the data we normally pull in as an admin cannot be retrieved because
            the nest API calls available to retrieve that data will add a significant
            amount of time to retrieve those counts
        '''
        if group := safe_json_response(self.gitlab_api.generate_get_request(host, token, f'groups/{group_id}')):
            group_path = group.get('full_path')
            query = generate_group_stats_query(group_path)
            return safe_json_response(self.gitlab_api.generate_post_request(host, token, None, data=json_dumps(query), graphql_query=True))


