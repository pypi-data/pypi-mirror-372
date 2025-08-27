from logging import DEBUG

import click
import time

from gitlab_evaluate import log
from gitlab_evaluate.migration_readiness.gitlab.report_generator import ReportGenerator as GLReportGenerator
from gitlab_evaluate.migration_readiness.gitlab import evaluate as evaluate_api
from gitlab_evaluate.migration_readiness.jenkins.report_generator import ReportGenerator as JKReportGenerator
from gitlab_evaluate.migration_readiness.bitbucket.report_generator import BitbucketReportGenerator
from gitlab_evaluate.migration_readiness.ado.report_generator import AdoReportGenerator
from gitlab_evaluate.migration_readiness.github_enterprise.report_generator import GithubReportGenerator

@click.command
@click.option("-s", "--source", help="Source URL: REQ'd")
@click.option("-t", "--token", help="Personal Access Token: REQ'd")
@click.option("-o", "--output", is_flag=True, help="Output Per Project Stats to screen")
@click.option("-i", "--insecure", is_flag=True, help="Set to ignore SSL warnings.")
@click.option("-g", "--group-id", help="Group ID. Evaluate all group projects (including sub-groups)")
@click.option("-f", "--filename", help="XLSX Output File Name. If not set, will default to 'evaluate_output.xlsx'")
@click.option("-p", "--processes", help="Number of processes. Defaults to number of CPU cores")
@click.option("-v", "--verbose", is_flag=True, help="Set logging level to Debug and output everything to the screen and log file")
@click.option("-r", "--generate-report", is_flag=True, help="Generate full XLSX report from sqlite database. Source and Token are still required for the report to generate")
def evaluate_gitlab(source, token, output, insecure, group_id, filename, processes, verbose, generate_report):
    if None not in (token, source):
        if verbose:
            log.setLevel(DEBUG)
        args = {}
        if insecure:
            args['ssl_verify'] = False
        if generate_report:
            args['retain_db'] = True
        evaluateApi = evaluate_api.EvaluateApi(**args)

        rg = GLReportGenerator(source, token, filename=filename,
                               output_to_screen=output, evaluate_api=evaluateApi, processes=processes)
        # Generates a fallback report directly from the previous run's sqlite3 database
        if generate_report:
            click.echo(f"Pulling app stats from {source} and generating report from previous Evaluate run")
            if rg.using_admin_token:
                log.info("GitLab instance stats and project metadata retrieval")
                rg.get_app_stats(source, token, group_id)
            else:
                rg.get_app_stats(source, token, group_id, admin=False)
            rg.write_output_to_files()
            rg.write_users_to_report()
            rg.write_workbook()
        # Execute a full scan
        else:
            rg.handle_getting_data(group_id)
            if rg.using_admin_token:
                log.info("GitLab instance stats and project metadata retrieval")
                rg.get_app_stats(source, token, group_id)
            else:
                rg.get_app_stats(source, token, group_id, admin=False)
            log.info("GitLab users metadata retrieval")
            rg.handle_getting_user_data(group_id)
            log.info(f"Data retrieval complete. Writing content to file")
            rg.write_workbook()
        


@click.command
@click.option("-s", "--source", help="Source URL: REQ'd")
@click.option("-u", "--user", help="Username associated with the Jenkins API token: REQ'd")
@click.option("-t", "--token", help="Jenkins API Token: REQ'd")
@click.option("-p", "--processes", help="Number of processes. Defaults to number of CPU cores")
@click.option("-i", "--insecure", is_flag=True, help="Set to ignore SSL warnings.")
@click.option("--gitlab-token", help="Optional GitLab token for fetching Jenkinsfile from GitLab repos")
@click.option("--github-token", help="Optional GitHub token for fetching Jenkinsfile from GitHub repos")
def evaluate_jenkins(source, user, token, processes, insecure, gitlab_token, github_token):
    print(f"Connecting to Jenkins instance at {source}")

    scm = {}
    if gitlab_token:
        scm['gitlab'] = {'token': gitlab_token}
    if github_token:
        scm['github'] = {'token': github_token}
        
    if insecure:
        r = JKReportGenerator(
            source, user, token, filename='evaluate_jenkins', processes=processes, ssl_verify=False, scm=scm or None)
    else:
        r = JKReportGenerator(source, user, token,
                              filename='evaluate_jenkins', processes=processes, ssl_verify=True, scm=scm or None)
    print("Retrieving list of Jenkins plugins")
    r.get_plugins()
    print("Retrieving list of Jenkins jobs and performing analysis")
    r.get_raw_data()
    print("Retrieving Jenkins instance statistics")
    stats = r.get_app_stats()
    print("Finalizing report")
    r.get_app_stat_extras(stats)
    r.write_workbook()
    print("Report generated. Please review evaluate_jenkins.xlsx")
    r.jenkins_client.drop_tables()


@click.command
@click.option('-s', '--source', required=True, help='Source URL')
@click.option('-t', '--token', required=True, help='Personal Access Token')
def evaluate_bitbucket(source, token):
    print("NOTE: BitBucket Evaluation is in a BETA state")
    print(f"Connecting to Bitbucket instance at {source}")

    # Record the start time
    start_time = time.time()

    rg = BitbucketReportGenerator(source, token, filename='evaluate_bitbucket')
    print("Retrieving Bitbucket instance statistics")
    rg.get_app_stats()
    rg.handle_getting_data()
    if rg.using_admin_token:
        print("Project data retrieval complete. Moving on to User metadata retrieval")
        rg.handle_getting_user_data()
    else:
        print("Non-admin token used. Skipping user retrieval")
    rg.write_workbook()

    # Record the end time
    end_time = time.time()

    # Calculate the duration in minutes
    duration_minutes = (end_time - start_time) / 60

    print(f"Report generated. Please review evaluate_bitbucket.xlsx")
    print(f"Process completed in {duration_minutes:.2f} minutes.")


@click.command
@click.option('-s', '--source', required=True, help='Source URL')
@click.option('-t', '--token', required=True, help='Personal Access Token')
@click.option("-p", "--processes", help="Number of processes. Defaults to number of CPU cores")
@click.option('--skip-details', is_flag=True, help='Skips details')
@click.option('--project', help='Project ID. Evaluate all data within a given Azure DevOps project')
# https://learn.microsoft.com/en-us/rest/api/azure/devops/?view=azure-devops-rest-7.2&viewFallbackFrom=azure-devops-rest-4.1#api-and-tfs-version-mapping
@click.option('--api-version', default='7.2-preview', help='API version to use (default: 7.2-preview)')
@click.option('-f', '--filename', default='evaluate_ado', help='XLSX Output File Name')
@click.option("-i", "--insecure", is_flag=True, help="Set to ignore SSL warnings.")
def evaluate_ado(source, token, skip_details, project, processes, api_version, filename, insecure):
    print("NOTE: Azure DevOps Evaluation is in a BETA state")
    print(f"Connecting to Azure DevOps instance at {source} using API version {api_version}")
    if project:
        print(f"Evaluating data for project: {project}")

    # Record the start time
    start_time = time.time()

    filename = filename if filename.endswith('.xlsx') else f"{filename}.xlsx"
    
    rg = AdoReportGenerator(source, token, filename, project=project, processes=processes, api_version=api_version, verify=(not insecure))
    print("Retrieving Azure DevOps projects and repository data ... ")
    rg.handle_getting_data(skip_details)

    if "dev.azure.com" in source:
        print("Retrieving Azure DevOps instance users data ... ")
        rg.handle_getting_user_data()
    else:
        print("TFS and Azure DevOps Server do not support user retrieval via API. Skipping user retrieval data ...")

    print("Retrieving Azure DevOps projects pipelines data ... ")
    rg.handle_getting_agent_pool_data()

    print("Retrieving Azure DevOps project variable groups data ... ")
    rg.handle_getting_variable_groups_data()
    
    print("Retrieving Azure DevOps projects pipelines data ... ")
    rg.handle_getting_pipelines_data()

    print("Retrieving Azure DevOps instance statistics ... ")
    rg.get_app_stats()

    print("Retrieving Azure DevOps feeds data ... ")
    rg.handle_getting_feeds_data()

    rg.write_workbook()

    # Record the end time
    end_time = time.time()

    # Calculate the duration in minutes
    duration_minutes = (end_time - start_time) / 60

    print(f"Report generated. Please review file '{filename}'")
    print(f"Process completed in {duration_minutes:.2f} minutes.")

@click.command
@click.option('-s', '--source', required=True, help='Source URL')
@click.option('-t', '--token', required=True, help='Personal Access Token')
def evaluate_github_enterprise(source, token):
    print("NOTE: Github Evaluation is in a BETA state")
    print(f"Connecting to Github instance at {source}")

    # Record the start time
    start_time = time.time()

    rg = GithubReportGenerator(source, token, filename='evaluate_github_enterprise')
    print("Retrieving Github instance statistics")
    rg.get_app_stats()
    rg.handle_getting_data()
    if rg.using_admin_token:
        print("Project data retrieval complete. Moving on to User metadata retrieval")
        rg.handle_getting_user_data()
    else:
        print("Non-admin token used. Skipping user retrieval")
    rg.write_workbook()

    # Record the end time
    end_time = time.time()

    # Calculate the duration in minutes
    duration_minutes = (end_time - start_time) / 60

    print(f"Report generated. Please review evaluate_github_enterprise.xlsx")
    print(f"Process completed in {duration_minutes:.2f} minutes.")
