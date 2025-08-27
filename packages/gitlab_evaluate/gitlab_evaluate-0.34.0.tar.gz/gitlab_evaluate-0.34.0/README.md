# Evaluate

Evaluate is a script that can be run to gather information from a number of source code management and CI/CD orchestration systems to help prepare for migration or platform consolidation efforts. Currently Evaluate supports gathering data from

 - GitLab
 - Bitbucket Server/Data Center
 - GitHub Enterprise
 - Jenkins
 - Azure DevOps.

This information is useful to the GitLab Professional Services (PS) team to accurately scope migration services. It is also helpful for customers and partners who are embarking on migration journeys.

[TOC]

## Contributions / Support

This tool is maintained by the Professional Services team and is not included in your GitLab Support if you have a license. For support questions please create [an issue](https://gitlab.com/gitlab-org/professional-services-automation/tools/utilities/evaluate/-/issues/new?issuable_template=evaluate-support) using our [Evaluate support issue template](./.gitlab/issue_templates/evaluate-support.md).

## Use Case

GitLab Professional Serivces shares this script with Customers to run against their GitLab instance or group. Then the customer can send back the output files to enable GitLab engagement managers to scope engagements accurately. There is a [single file generated](reading-the-output.md).

## Install Method

### Versioning

- For GitLab versions < 16.0. use Evaluate version <= 0.24.0. Evaluate switched to using GraphQL queries instead of REST API requests, which can cause some issues retrieving data from older GitLab instances
- For GitLab versions >= 16.0 use Evaluate version > 0.24.0, ideally the latest

### Docker Container

[Docker containers with evaluate installed](https://gitlab.com/gitlab-org/professional-services-automation/tools/utilities/evaluate/container_registry) are available to use.

```bash
# For GitLab versions older than 16.0. Evaluate versions newer than 0.24.0 switched to using GraphQL queries instead of REST API requests which can cause some issues retrieving data from older GitLab instances
docker pull registry.gitlab.com/gitlab-org/professional-services-automation/tools/utilities/evaluate:0.24.0

# For GitLab versions newer than 16.0
docker pull registry.gitlab.com/gitlab-org/professional-services-automation/tools/utilities/evaluate:latest

# Spin up container
docker run --name evaluate -it registry.gitlab.com/gitlab-org/professional-services-automation/tools/utilities/evaluate:latest /bin/bash

# In docker shell
evaluate-gitlab -t <access-token-with-api-scope> -s https://gitlab.example.com
evaluate-jenkins -s https://jenkins.example.com -u <jenkins-admin-user> -t <access-token-or-password>
evaluate-bitbucket -s https://bitbucket.example.com -t <access-token> # BETA
evaluate-ado -s https://dev.azure.com/<your-org> -t <personal-access-token> # BETA
```

### Pipeline schedule

To schedule Evaluate to run on a regular basis we recommend using the following pipeline:

```yml
image: registry.gitlab.com/gitlab-org/professional-services-automation/tools/utilities/evaluate:latest

stages:
    - evaluate

run-evaluate:
    stage: evaluate
    # variables:
    #   REQUESTS_CA_BUNDLE: "/custom/certs/my-cert.crt"  # If you need a custom Root-ca-certificate
    timeout: 4h
    script:
        - evaluate-gitlab -t $API_TOKEN -s https://<gitlab-hostname> -p <number-of-processes>
    artifacts:
        name: Report
        paths:
            - evaluate_report.xlsx
        expire_in: 1 week
```

**NOTES:**

- Configure `API_TOKEN` as CI variable with Admin personal access token and `read_api` or `api` scope
- Add Runner `tags` for using a `docker` executor and **Linux** Runner
- Adjust the number of processes based on [recommendation](#recommended-processes-per-project-count)
- Adjust `timeout` after the 1st run
- Create pipeline schedule under _Build -> Pipeline schedules_

### Local (development / troubleshooting)

Requires Python 3.8 through 3.12 (Python 3.13 is not yet supported).

```bash
git clone https://gitlab.com/gitlab-org/professional-services-automation/tools/utilities/evaluate.git   # or SSH
cd evaluate
pip install gitlab-evaluate

# In local terminal
evaluate-gitlab -t <access-token-with-api-scope> -s https://gitlab.example.com
evaluate-jenkins -s https://jenkins.example.com -u <jenkins-admin-user> -t <access-token-or-password>
evaluate-bitbucket -s https://bitbucket.example.com -t <access-token> # BETA
evaluate-ado -s https://dev.azure.com/<your-org> -t <personal-access-token> # BETA
```

To test latest branch commits, remove your local install of `site-packages/gitlab_evaluate*`, e.g.

```sh
rm -rf /opt/homebrew/lib/python3.8/site-packages/gitlab_evaluate*
```

and from the local branch run:

```sh
pip install git+https://gitlab.com/gitlab-org/professional-services-automation/tools/utilities/evaluate.git@<branch-name>
```

## Usage

### GitLab

Evaluate is meant to be run by an **OWNER** (ideally system **ADMINISTRATOR**) of a GitLab instance to gather data about every project on the instance or group (including sub-groups).

1. A GitLab **OWNER** (ideally system **ADMINISTRATOR**) should provision an access token with `api` or `read_api` scope:
   - [Personal access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#create-a-personal-access-token) for instance
   - [Group access token](https://docs.gitlab.com/ee/user/group/settings/group_access_tokens.html#create-a-group-access-token-using-ui) for group
2. Install `gitlab-evaluate` from the [Install](#install-method) section above,
3. Run :point_down:

    For evaluating a GitLab instance

    ```bash
    evaluate-gitlab -t <access-token-with-api-scope> -s https://gitlab.example.com
    ```

    For evaluating a GitLab group (including sub-groups)

    ```bash
    evaluate-gitlab -t <access-token-with-api-scope> -s https://gitlab.example.com -g 42
    ```

    See [Recommended Processes per Project Count](#recommended-processes-per-project-count) to specify the number of processes to use.

    **NOTE:** If you have configured rate limits on your instance to be more strict than the default settings, start with one process (`-p 1`) and adjust accordingly up to the recommended number of processes for your sized instance

    **NOTE:** In the event Evaluate freezes or doesn't finish running while scanning a GitLab instance, re-run your evaluate command with an additional `-r` or `--generate-report` flag to generate a report based on the data retrieved so far

4. This should create a file called `evaluate_report.xlsx`

   For more information on these files, see [reading the output](reading-the-output.md)
5. If you're coordinating a GitLab PS engagement, email these files to the GitLab account team.

#### Recommended Processes per Project Count

Evaluate uses 4 processes by default, which is sufficient for smaller GitLab instances, but may result in a slower scan time for larger instances. Below is a table covering recommended processes based on the overall number of projects on an instance:

| Number of Projects | Recommended Processes |
| ------------------ | --------------------- |
| < 100              | 4 (default)           |
| < 1000             | 8                     |
| < 10000            | 16                    |
| < 100000           | 32                    |
| > 100000           | 64-128                |

The number of processes is limited by a few factors:

- API rate limits on the GitLab instance itself
- Overall stability of the GitLab instance
- Not as critical as the first two, but overall available memory on the machine running Evaluate is another factor to consider

You can ramp up the number of processes on a smaller instance to speed up the scans, but the performance gains for a large number of processes on a smaller instance will eventually plateau.

#### Command help screen

```text
Usage: evaluate-gitlab [OPTIONS]

Options:
  -s, --source TEXT      Source URL: REQ'd
  -t, --token TEXT       Personal Access Token: REQ'd
  -o, --output           Output Per Project Stats to screen
  -i, --insecure         Set to ignore SSL warnings.
  -g, --group-id TEXT    Group ID. Evaluate all group projects (including sub-
                         groups)
  -f, --filename TEXT    XLSX Output File Name. If not set, will default to
                         'evaluate_output.xlsx'
  -p, --processes TEXT   Number of processes. Defaults to number of CPU cores
  -v, --verbose          Set logging level to Debug and output everything to
                         the screen and log file
  -r, --generate-report  Generate full XLSX report from sqlite database.
                         Source and Token are still required for the report to
                         generate
  --help                 Show this message and exit.
```

### Jenkins

Evaluate supports scanning a Jenkins instance to retrieve basic metrics about the instance.

Evaluate is meant to be run by an admin of a Jenkins instance to gather data about jenkins jobs and any plugins installed on the instance. If the Jenkins jobs config are stored on a SCM repo like Github or Gitlab, you will need a token with read repository access to the SCM repo for a deeper analysis.

1. A Jenkins **ADMINISTRATOR** should provision an API token for Evaluate to use during the scan.
2. Install `gitlab-evaluate` from the [Install](#install-method) section above,
3. Run :point_down:

    ```bash
    evaluate-jenkins -s https://jenkins.example.com -u <jenkins-admin-user> -t <access-token-or-password>
    ```

4. This should create a file called `evaluate_jenkins.xlsx`
5. If you're coordinating a GitLab PS engagement, email these files to the GitLab account team.

#### Command help screen

```sh
Usage: evaluate-jenkins [OPTIONS]

Options:
  -s, --source TEXT  Source URL: REQ'd
  -u, --user TEXT    Username associated with the Jenkins API token: REQ'd
  -t, --token TEXT   Jenkins API Token: REQ'd
  -i, --insecure     Set to ignore SSL warnings
  --gitlab-token TEXT Optional GitLab token for fetching Jenkinsfile from GitLab repos
  --github-token TEXT Optional GitHub token for fetching Jenkinsfile from GitHub repos
  --help             Show this message and exit.
```

### [BETA] BitBucket

Evaluate supports scanning a Bitbucket Server/Data Center to retrieve relevant metadata about the server.

You can use either a admin or a non-admin token to do the evaluation but non-admin tokens can't pull users information.

1. A user should provision an access token for Evaluate to use during the scan.
2. Install `gitlab-evaluate` from the [Install](#install-method) section above,
3. Run :point_down:

    ```bash
    evaluate-bitbucket -s https://bitbucket.example.com -t <access-token>
    ```

4. This should create a file called `evaluate_bitbucket.xlsx`
5. If you're coordinating a GitLab PS engagement, email these files to the GitLab account team.

#### Command help screen

```sh
Usage: evaluate-bitbucket [OPTIONS]

Options:
  -s, --source TEXT  Source URL: REQ'd
REQ'd
  -t, --token TEXT   Bitbucket access Token: REQ'd
  --help             Show this message and exit.
```

### [BETA] Azure DevOps

Evaluate supports scanning an Azure DevOps to retrieve relevant metadata about the organization.

<details><summary>

You need to use [Personal Access Token](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows) with [Read scope](https://learn.microsoft.com/en-us/azure/devops/integrate/get-started/authentication/oauth?view=azure-devops#scopes) to most of the services.

</summary>

When running Evaluate for Azure DevOps, the tool retrieves information from the endpoints listed below. To ensure the tool functions correctly, create a personal access token with the required scopes as shown in the image below.

```txt
Get Descriptor
Endpoint: /_apis/graph/descriptors/{project_id}
Sub-API: vssps
Scope: Graph (Read)

Get Project Administrators Group
Endpoint: /_apis/graph/groups?scopeDescriptor={scopeDescriptor}
Sub-API: vssps
Scope: Graph (Read)

Get Project Administrators
Endpoint: /_apis/GroupEntitlements/{project_group_id}/members
Sub-API: vsaex
Scope: MemberEntitlementManagement (Read)

Get Work Items
Endpoint: /{project_id}/_apis/wit/wiql
Scope: Work Items (Read)

Get Release Definitions
Endpoint: /{project_id}/_apis/release/definitions
Sub-API: vsrm
Scope: Release (Read)

Get Build Definitions
Endpoint: /{project_id}/_apis/build/definitions
Scope: Build (Read)

Get Commits
Endpoint: /{project_id}/_apis/git/repositories/{repository_id}/commits
Scope: Code (Read)

Get Pull Requests
Endpoint: /{project_id}/_apis/git/repositories/{repository_id}/pullrequests
Scope: Code (Read)

Get Branches
Endpoint: /{project_id}/_apis/git/repositories/{repository_id}/refs
Scope: Code (Read)

Get Repositories
Endpoint: /{project_id}/_apis/git/repositories
Scope: Code (Read)

Get Project
Endpoint: /_apis/project/{project_id}
Scope: Project and Team (Read)

Get Projects
Endpoint: /_apis/projects
Scope: Project and Team (Read)

Get Users
Endpoint: /_apis/graph/users
Sub-API: vssps
Scope: Graph (Read)

Get Agent Pools
Endpoint: /_apis/distributedtask/pools
Scope: Agent Pools (Read)

Variable Groups
Endpoint: /_apis/distributedtask/variablegroups
Scope: Variable Groups (Read)

Test Connection
Endpoint: /_apis/ConnectionData
Scope: Service Connections (Read)
```

</details>

1. A user should provision an access token for Evaluate to use during the scan.
2. Install `gitlab-evaluate` from the [Install](#install-method) section above,
3. Run :point_down:

- For Azure DevOps Service (Cloud):

  ```bash
  evaluate-ado -s https://dev.azure.com/<your-org> -t <personal-access-token>
  ```

- For Azure DevOps Server:

  ```bash
  evaluate-ado -s {instance_url}/{collection} -t <personal-access-token> --api-version=7.0
  ```

- For Team Foundation Server (TFS):

  ```bash
  evaluate-ado -s {server_url:port}/tfs/{collection} -t <personal-access-token> --api-version=4.1
  ```

> **Note:**
> When running Evaluate against **Azure DevOps Server** or **Team Foundation Server (TFS)**, you must specify the correct API version.
>
> To determine the required API version:
> 1. Click your user icon and select **Help > About** to view your server information.
> 2. Refer to the [API and TFS version mapping documentation](https://learn.microsoft.com/en-us/rest/api/azure/devops/?view=azure-devops-rest-7.2#api-and-tfs-version-mapping) to identify the appropriate API version for your server.

4. Unless the user provides a custom `--filename`, the report file is named `evaluate_ado` by default.
5. If you're coordinating a GitLab PS engagement, email these files to the GitLab account team.

#### Command help screen

```sh
Usage: evaluate-ado [OPTIONS]

Options:
  -s, --source TEXT     Source URL  [required]
  -t, --token TEXT      Personal Access Token  [required]
  -p, --processes TEXT  Number of processes. Defaults to number of CPU cores
  --skip-details        Skips details
  --project TEXT        Project ID. Evaluate all data within a given Azure
                        DevOps project (Project ID should be in UUID format)
  --api-version TEXT    API version to use (default: 7.2-preview)
  -f, --filename TEXT   XLSX Output File Name (default: evaluate_ado)
  --help                Show this message and exit.
```

### [BETA] Github Enterprise

Evaluate supports scanning a Github Enterprise Server (GHES) to retrieve relevant metadata about the server.

You have to use an admin personal access token ([other token types](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github#githubs-token-formats) potentially supported) to do the evaluation.

1. A user should provision an admin access token for Evaluate to use during the scan.
1. Install `github-evaluate` from the [Install](#install-method) section above,
1. OPTIONAL: If you are using custom CA, export the CA bundle: `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt`
1. Run :point_down:

    ```bash
    evaluate-github-enterprise -s https://github.dev -t <access-token>
    ```

1. This should create a file called `evaluate_github.xlsx`
1. If you're coordinating a GitLab PS engagement, email these files to the GitLab account team.

#### Command help screen

```sh
Usage: evaluate-github-enterprise [OPTIONS]

Options:
  -s, --source TEXT  Source URL: REQ'd
REQ'd
  -t, --token TEXT   Github access Token: REQ'd
  --help             Show this message and exit.
```

## GitLab Project Thresholds

_Below are the thresholds we will use to determine whether a project can be considered for normal migration or needs to have special steps taken in order to migrate_

### Project Data

- Project Size - 20GB
- Pipelines - 5,000 max
- Issues - 5,000 total (not just open)
- Merge Requests - 5,000 total (not just merged)
- Container images - 20GB per project
- Packages - Any packages present

### Repository Data

- Repository Size - 5GB
- Commits - 50K
- Branches - 1K
- Tags - 5K
