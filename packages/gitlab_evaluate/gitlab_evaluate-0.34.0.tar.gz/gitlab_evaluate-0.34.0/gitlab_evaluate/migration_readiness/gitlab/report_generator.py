from sys import exit as sys_exit
import xlsxwriter
from dacite import from_dict
from gitlab_ps_utils.processes import MultiProcessing
from gitlab_ps_utils.misc_utils import is_error_message_present
from gitlab_ps_utils.dict_utils import dig
from gitlab_evaluate import log
from gitlab_evaluate.lib import utils, db_utils
from gitlab_evaluate.lib.api_models.application_stats import GitLabApplicationStats
from gitlab_evaluate.lib.api_models.user import User
from gitlab_evaluate.migration_readiness.gitlab.data_classes.project import Project
from gitlab_evaluate.migration_readiness.gitlab import evaluate as evaluateApi
from gitlab_evaluate.migration_readiness.gitlab import constants

class ReportGenerator():
    def __init__(self, host, token, filename=None, output_to_screen=False, evaluate_api=None, processes=None):
        self.host = host
        self.token = token
        self.evaluate_api = evaluate_api if evaluate_api else evaluateApi.EvaluateApi()
        self.validate_token()
        if filename:
            self.workbook = xlsxwriter.Workbook(f'{filename}.xlsx')
        else:
            self.workbook = xlsxwriter.Workbook('evaluate_report.xlsx')
        self.app_stats = self.workbook.add_worksheet('App Stats')
        self.align_left = self.workbook.add_format({'align': 'left'})
        # Create Header format with a black background
        self.header_format = self.workbook.add_format(
            {'bg_color': 'black', 'font_color': 'white', 'bold': True, 'font_size': 10})
        self.final_report = self.workbook.add_worksheet('Evaluate Report')
        self.workbook.add_format({'text_wrap': True, 'font_size': 10})
        self.flagged_projects = self.workbook.add_worksheet('Flagged Projects')
        self.using_admin_token = self.is_admin_token()
        self.users = self.workbook.add_worksheet('Users')
        self.raw_output = self.workbook.add_worksheet('Raw Project Data')
        self.output_to_screen = output_to_screen
        self.multi = MultiProcessing()
        self.processes = processes
        utils.write_headers(0, self.raw_output,
                            constants.COLUMNS, self.header_format)
        utils.write_headers(0, self.flagged_projects,
                            constants.COLUMNS, self.header_format)
        utils.write_headers(0, self.final_report,
                            constants.REPORT_HEADERS, self.header_format)
        utils.write_headers(
            0, self.users, constants.USER_HEADERS, self.header_format)
        # Merging the first two headers of account summary
        self.app_stats.merge_range(
            'A1:B1', constants.ACCOUNT_HEADERS[0], self.header_format)
        self.app_stats.merge_range(
            'C1:D1', constants.ACCOUNT_HEADERS[1], self.header_format)
        self.final_report.set_default_row(150)
        self.final_report.set_row(0, 20)

    def write_workbook(self):
        self.app_stats.autofit()
        self.final_report.autofit()
        self.flagged_projects.autofit()
        self.raw_output.autofit()
        self.users.autofit()
        self.workbook.close()

    def handle_getting_data(self, group_id):
        # Determine whether to list all instance or all group projects (including sub-groups)
        full_path = None
        if group_id:
            full_path = self.evaluate_api.gitlab_api.generate_get_request(
                self.host, self.token, f'groups/{group_id}').json()['full_path']
            log.info(
                f"Running Evaluate on GitLab group '{full_path}' (ID: {group_id})")
        else:
            log.info(f"Running Evaluate against all projects")
        self.multi.start_multi_process_stream_with_args(self.evaluate_api.get_all_project_data, self.evaluate_api.get_all_projects_by_graphql(
                self.host, self.token, full_path), self.host, self.token, processes=self.processes)
        self.write_output_to_files()

    def handle_getting_user_data(self, group_id=None):
        endpoint = f"groups/{group_id}/members" if group_id else "/users?exclude_internal=true&without_project_bots=true"
        for user in self.multi.start_multi_process_stream(self.evaluate_api.get_user_data, self.evaluate_api.gitlab_api.list_all(
                self.host, self.token, endpoint), processes=self.processes):
            self.evaluate_api.insert_user_data(user)

        self.write_users_to_report()

    def write_users_to_report(self):
        log.info("Writing users to report")
        connection, cursor = utils.sqlite_connection('gitlab.db', rows_as_dicts=True)
        for data in cursor.execute("SELECT * FROM users"):
            user = User(**data).to_dict()
            utils.append_to_workbook(
                self.users, [user], constants.USER_HEADERS)
        connection.close()

    def get_app_stats(self, source, token, group_id, admin=True):
        report_stats = []
        additional_info = []
        app_stats = {}
        archived_projects = ""
        if admin and not group_id:
            error, resp = is_error_message_present(
                self.evaluate_api.getApplicationInfo(source, token))
            if not error:
                app_stats = from_dict(data_class=GitLabApplicationStats, data=resp)
                archived_projects = self.evaluate_api.getArchivedProjectCount(
                    source, token)
                self.compare_projects_kind_sum(int(app_stats.projects.replace(',','')))
            else:
                log.warning(
                    f"Unable to pull application info from URL: {source}")
        elif group_id:
            app_stats = self.get_specific_group_stats(group_id)
        else:
            app_stats = GitLabApplicationStats(forks="N/A", issues="N/A", merge_requests="N/A", notes="N/A",
                                               snippets="N/A", ssh_keys="N/A", milestones="N/A", users="N/A",
                                               groups="N/A", projects="N/A", active_users="N/A")
            log.warning(
                    f"Unable to pull application info from URL: {source}")
        report_stats += [
            ('Basic information from source', source),
            ('Customer', '<CUSTOMERNAME>'),
            ('Date Run', utils.get_date_run()),
            ('Evaluate Version', utils.get_package_version()),
            ('Source', '<SOURCE>'),
            ('Total Users', app_stats.users),
            ('Total Active Users', app_stats.active_users),
            ('Total Groups', app_stats.groups),
            ('Total Projects', app_stats.projects),
            ('Total Merge Requests', app_stats.merge_requests),
            ('Total Forks', app_stats.forks),
            ('Total Issues', app_stats.issues),
            ('Total Group Projects', utils.get_countif(
                self.raw_output.get_name(), 'group', 'D')),
            ('Total User Projects', utils.get_countif(
                self.raw_output.get_name(), 'user', 'D')),
            ('Total Archived Projects', archived_projects)
        ]
        additional_info += [('Reading the Output',
                                utils.get_reading_the_output_link())]

        if resp := self.evaluate_api.getVersion(source, token):
            if len(report_stats) > 0:
                report_stats.insert(1, ('GitLab Version', resp.get('version')))
            else:
                report_stats.append(('GitLab Version', resp.get('version')))
            additional_info.append(
                ('Upgrade Path', utils.get_upgrade_path(resp.get('version'))))
            additional_info.append(
                ('What\'s new', utils.get_whats_changed(resp.get('version'))))
        else:
            log.warning(f"Unable to pull application info from URL: {source}")

        for row, stat in enumerate(report_stats):
            self.app_stats.write(row+1, 0, stat[0])
            if stat[0] == 'Total Group Projects' or stat[0] == 'Total User Projects':
                self.app_stats.write_formula(
                    row+1, 1, '='+stat[1], self.align_left)
            else:
                self.app_stats.write(row+1, 1, stat[1])

        for row, stat in enumerate(additional_info):
            self.app_stats.write(row+1, 2, stat[0])
            self.app_stats.write(row+1, 3, stat[1])

        project_summary_row_start_index = len(report_stats) + 2
        self.get_projects_summary(project_summary_row_start_index,
                                  app_stats, archived_projects, group_id, source, token)

    def compare_projects_kind_sum(self, projects):
        group_projects = self.get_project_count_from_db(project_type='group')
        user_projects = self.get_project_count_from_db(project_type='user')

        if projects != (user_projects + group_projects):
            if projects != (group_projects + user_projects):
                log.warning(f"Total Projects ({projects}) does not match the sum of Group ({group_projects}) and User ({user_projects}) Projects")

    def get_projects_summary(self, row_start_index, app_stats, archived_projects, group_id, source, token):
        projects_summary = []
        if not app_stats and len(archived_projects) > 0:
            projects_summary += [
                ('Total', app_stats.projects, utils.get_countif(
                    self.raw_output.get_name(), 'group', 'D')),
                ('Active', utils.get_countif(self.raw_output.get_name(), 'Fals*', 'H'),
                 utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Fals*', 'H')),
                ('Archived', archived_projects, utils.get_countifs(
                    self.raw_output.get_name(), 'group', 'D', 'Tru*', 'H')),
                ('Outliers', utils.get_if(utils.get_counta(self.flagged_projects.get_name(), 'A')+'=0', 0, utils.get_counta(self.flagged_projects.get_name(), 'A')+'-1'),
                 utils.get_if(utils.get_countif(self.flagged_projects.get_name(), 'group', 'D')+'=0', 0, utils.get_countif(self.flagged_projects.get_name(), 'group', 'D'))),
            ]
        elif group_id:
            projects_summary += [
                ('Total', self.evaluate_api.get_total_project_count(source, token,
                 group_id), utils.get_countif(self.raw_output.get_name(), 'group', 'D')),
                ('Active', utils.get_countif(self.raw_output.get_name(), 'Fals*', 'H'),
                 utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Fals*', 'H')),
                ('Archived', utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*',
                 'H'), utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'H')),
                ('Outliers', utils.get_if(utils.get_counta(self.flagged_projects.get_name(), 'A')+'=0', 0, utils.get_counta(self.flagged_projects.get_name(), 'A')+'-1'),
                 utils.get_if(utils.get_countif(self.flagged_projects.get_name(), 'group', 'D')+'=0', 0, utils.get_countif(self.flagged_projects.get_name(), 'group', 'D'))),
            ]
        utils.write_headers(row_start_index, self.app_stats,
                            constants.PROJECT_SUMMARY_HEADERS, self.header_format)
        for row_num, row_data in enumerate(projects_summary):
            for col_num, value in enumerate(row_data):
                if col_num == 0:
                    self.app_stats.write(
                        row_num+row_start_index+1, col_num, value)
                else:
                    self.app_stats.write_formula(
                        row_num+row_start_index+1, col_num, '=' + str(value) if value is not None else '')

        projects_to_review_row_start_index = row_start_index + \
            len(projects_summary) + 2
        self.get_projects_to_review(projects_to_review_row_start_index)

    def get_projects_to_review(self, row_start_index):
        projects_to_review = [
            ('Outlier Projects', utils.get_if(utils.get_counta(self.flagged_projects.get_name(), 'A')+'=0', 0, utils.get_counta(self.flagged_projects.get_name(), 'A')+'-1'),
             utils.get_if(utils.get_countif(self.flagged_projects.get_name(), 'group', 'D')+'=0', 0, utils.get_countif(self.flagged_projects.get_name(), 'group', 'D'))),
            ('Pipelines > 5,000', utils.get_countif(self.raw_output.get_name(), 'Tru*', 'J'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'J')),
            ('Issues > 5,000', utils.get_countif(self.raw_output.get_name(), 'Tru*', 'L'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'L')),
            ('Branches > 1,000', utils.get_countif(self.raw_output.get_name(), 'Tru*', 'N'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'N')),
            ('Commits > 50,000', utils.get_countif(self.raw_output.get_name(), 'Tru*', 'P'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'P')),
            ('Merge Requests > 5,000', utils.get_countif(self.raw_output.get_name(), 'Tru*',
             'R'), utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'R')),
            ('Storage Size > 20 GB', utils.get_countif(self.raw_output.get_name(), 'Tru*', 'T'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'T')),
            ('Repo Size > 5 GB', utils.get_countif(self.raw_output.get_name(), 'Tru*', 'V'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'V')),
            ('LFS Objects Size > 5GB', utils.get_countif(self.raw_output.get_name(), 'Tru*', 'Z'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'Z')),
            ('Build Artifacts Size > 5GB', utils.get_countif(self.raw_output.get_name(), 'Tru*', 'AB'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'AB')),
            ('Snippets > 1000', utils.get_countif(self.raw_output.get_name(), 'Tru*', 'AD'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'AD')),
            ('Uploads Size > 5GB', utils.get_countif(self.raw_output.get_name(), 'Tru*', 'AF'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'AF')),
            ('Tags > 5000', utils.get_countif(self.raw_output.get_name(), 'Tru*', 'AH'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'AH')),
            ('Packages Size > 20 GB', utils.get_countif(self.raw_output.get_name(), 'Tru*', 'AK'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'AK')),
            ('Containers Size > 20 GB', utils.get_countif(self.raw_output.get_name(), 'Tru*', 'AN'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'AN')),
            ('Export Size > 5 GB', utils.get_countif(self.raw_output.get_name(), 'Tru*', 'AP'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'AP')),
            ('Export Size > 10 GB', utils.get_countif(self.raw_output.get_name(), 'Tru*', 'AQ'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', 'Tru*', 'AQ')),
        ]
        utils.write_headers(row_start_index, self.app_stats,
                            constants.PROJECTS_TO_REVIEW_HEADERS, self.header_format)
        for row_num, row_data in enumerate(projects_to_review):
            for col_num, value in enumerate(row_data):
                if col_num == 0:
                    self.app_stats.write(
                        row_num+row_start_index+1, col_num, value)
                else:
                    self.app_stats.write_formula(
                        row_num+row_start_index+1, col_num, '=' + str(value) if value is not None else '')

        metrics_row_start_index = row_start_index + len(projects_to_review) + 2
        self.get_metrics(metrics_row_start_index)

    def get_metrics(self, row_start_index):
        metrics = [
            ('Pipelines', utils.get_sum(self.raw_output.get_name(), 'I'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'I', 'group')),
            ('Issues', utils.get_sum(self.raw_output.get_name(), 'K'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'K', 'group')),
            ('Branches', utils.get_sum(self.raw_output.get_name(), 'M'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'M', 'group')),
            ('Commits', utils.get_sum(self.raw_output.get_name(), 'O'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'O', 'group')),
            ('Merge Requests', utils.get_sum(self.raw_output.get_name(), 'Q'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'Q', 'group')),
            ('Storage Size', utils.get_sum(self.raw_output.get_name(), 'S'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'S', 'group')),
            ('Repos Size', utils.get_sum(self.raw_output.get_name(), 'U'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'U', 'group')),
             ('Wiki Size', utils.get_sum(self.raw_output.get_name(), 'W'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'W', 'group')),
            ('LFS Objects Size', utils.get_sum(self.raw_output.get_name(), 'X'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'X', 'group')),
            ('Build Artifacts Size', utils.get_sum(self.raw_output.get_name(), 'AA'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'AA', 'group')),
            ('Snippets', utils.get_sum(self.raw_output.get_name(), 'AC'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'AC', 'group')),
            ('Uploads Size', utils.get_sum(self.raw_output.get_name(), 'AE'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'AE', 'group')),
            ('Tags', utils.get_sum(self.raw_output.get_name(), 'AG'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'AG', 'group')),
            ('generic Packages', utils.get_countif(self.raw_output.get_name(), '*generic*', 'AI'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', '*generic*', 'AI')),
            ('maven Packages', utils.get_countif(self.raw_output.get_name(), '*maven*', 'AI'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', '*maven*', 'AI')),
            ('npm Packages', utils.get_countif(self.raw_output.get_name(), '*npm*', 'AI'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', '*npm*', 'AI')),
            ('pypi Packages', utils.get_countif(self.raw_output.get_name(), '*pypi*', 'AI'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', '*pypi*', 'AI')),
            ('helm Packages', utils.get_countif(self.raw_output.get_name(), '*helm*', 'AI'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', '*helm*', 'AI')),
            ('composer Packages', utils.get_countif(self.raw_output.get_name(), '*composer*', 'AI'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', '*composer*', 'AI')),
            ('nuget Packages', utils.get_countif(self.raw_output.get_name(), '*nuget*', 'AI'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', '*nuget*', 'AI')),
            ('conan Packages', utils.get_countif(self.raw_output.get_name(), '*conan*', 'AI'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', '*conan*', 'AI')),
            ('golang Packages', utils.get_countif(self.raw_output.get_name(), '*golang*', 'AI'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', '*golang*', 'AI')),
            ('terraform_module Packages', utils.get_countif(self.raw_output.get_name(), '*terraform_module*', 'IH'),
             utils.get_countifs(self.raw_output.get_name(), 'group', 'D', '*terraform_module*', 'AI')),
            ('Packages Size', utils.get_sum(self.raw_output.get_name(), 'AJ'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'AJ', 'group')),
            ('Container Tags', utils.get_sum(self.raw_output.get_name(), 'AL'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'AL', 'group')),
            ('Containers Size', utils.get_sum(self.raw_output.get_name(), 'AM'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'AM', 'group')),
            ('Exports Size', utils.get_sum(self.raw_output.get_name(), 'AO'),
             utils.get_sumif(self.raw_output.get_name(), 'D', 'AO', 'group'))
        ]
        utils.write_headers(row_start_index, self.app_stats,
                            constants.METRICS_HEADERS, self.header_format)
        for row_num, row_data in enumerate(metrics):
            for col_num, value in enumerate(row_data):
                if col_num == 0:
                    self.app_stats.write(
                        row_num+row_start_index+1, col_num, value)
                else:
                    self.app_stats.write_formula(
                        row_num+row_start_index+1, col_num, '=' + str(value) if value is not None else '')

    def write_output_to_files(self):
        connection, cursor = utils.sqlite_connection('gitlab.db', rows_as_dicts=True)
        log.info("Writing raw_project_data sheet")
        for data in cursor.execute("SELECT * FROM projects"):
            project = db_utils.convert_retain_bool(Project, data)
            utils.append_to_workbook(self.raw_output, [project.to_dict()], constants.COLUMNS)
        log.info("Writing flagged_projects sheet")
        for data in cursor.execute("SELECT * FROM flagged_projects"):
            project = db_utils.convert_retain_bool(Project, data)
            utils.append_to_workbook(self.flagged_projects, [project.to_dict()], constants.COLUMNS)
        log.info("Writing evaluate_report sheet")
        for data in cursor.execute("SELECT * FROM reports"):
            utils.append_to_workbook(self.final_report, [{'project': data['project'], 'reason': data['reason']}], constants.REPORT_HEADERS)
        connection.close()

    def validate_token(self):
        error, resp = is_error_message_present(
            self.evaluate_api.get_token_owner(self.host, self.token))
        if error:
            log.error(
                "\nToken appears to be invalid. See API response below. Exiting script")
            log.error(resp)
            sys_exit(1)

    def is_admin_token(self):
        user = self.evaluate_api.get_user_data(
            self.evaluate_api.get_token_owner(self.host, self.token))
        return user.is_admin

    def get_specific_group_stats(self, group_id):
        '''
            Gets stats of a specific group when using a non-admin token

            Some of the data we normally pull in as an admin canot be retrieved because
            the nest API calls available to retrieve that data will add a significant
            amount of time to retrieve those counts
        '''
        # Placeholder message for data we cannot currently retrieve with an owner token
        missing_msg = 'unable to retrieve total count'
        if group_stats := self.evaluate_api.get_specific_group_stats_response(self.host, self.token, group_id):
            # Return actual results
            return GitLabApplicationStats(
                users=dig(group_stats, 'data', 'group', 'groupMembersCount'),
                active_users=dig(group_stats, 'data', 'group', 'groupMembersCount'),
                groups=dig(group_stats, 'data', 'group', 'descendantGroups', 'count'),
                projects=dig(group_stats, 'data', 'group', 'projects', 'count'),
                issues=dig(group_stats, 'data', 'group', 'issues', 'count'),
                merge_requests=dig(group_stats, 'data', 'group', 'mergeRequests', 'count'),
                notes=missing_msg,
                milestones=missing_msg,
                forks=missing_msg,
                ssh_keys=missing_msg,
                snippets=missing_msg
            )
        # Return fallback results with missing message for data that we cannot retrieve
        log.error("Could not retrieve specific group stats from GitLab")
        return GitLabApplicationStats(
                users=missing_msg,
                active_users=missing_msg,
                groups=missing_msg,
                projects=missing_msg,
                issues=missing_msg,
                merge_requests=missing_msg,
                notes=missing_msg,
                milestones=missing_msg,
                forks=missing_msg,
                ssh_keys=missing_msg,
                snippets=missing_msg
            )

    def get_project_count_from_db(self, project_type=None):
        connection, cursor = utils.sqlite_connection('gitlab.db')
        where_clause = f"WHERE kind = '{project_type}'" if project_type else ""
        projects = cursor.execute(f"SELECT COUNT(*) FROM projects {where_clause}").fetchone()[-1]
        connection.close()
        if isinstance(projects, str):
            return int(projects.replace(',',''))
        return int(projects)

