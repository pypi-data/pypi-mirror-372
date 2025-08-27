from copy import deepcopy as copy
from re import sub


class FlagRemediationMessages():
    def __init__(self, project_name):
        self.starting_string = f"\nProject {project_name} has been flagged due to "
        self.cannot_guarantee_string = "\nWe cannot guarantee this project will automatically be migrated."
        self.project_messages = []

    def generate_report_entry(self):
        report_string = f"{self.starting_string}"
        remediation_string = f"{self.cannot_guarantee_string} We recommend the following next steps:"
        for item in self.project_messages:
            next_steps = sub(' {2,}', '\t  ', item['next_steps'].strip())
            report_string += f"\n\t- {item['message']}"
            remediation_string += f"\n\t- {next_steps}"
        return f"{report_string}{remediation_string}"

    def add_flag_message(self, asset, flag_condition):
        self.project_messages.append(
            self.get_flag_message(asset, flag_condition))

    def get_flag_message(self, asset, flag_condition):
        flag_condition = str(flag_condition)
        flag_remediation = {
            "repository_size": {
                "message": f"repo size exceeding {flag_condition}",
                "next_steps": """
                    Clean up repository using these tips: https://docs.gitlab.com/ee/user/project/repository/reducing_the_repo_size_using_git.html"
                    Clean up the repo to get is as close to under 10GB as possible.
                    For repos between 5-10GB you can use S3 for migrations to GitLab.com.
                    Otherwise, either only migrate the git repo and leave all the GitLab data behind or update settings in admin panel in GitLab to support importing a larger project (only available in self-managed or dedicated)
                """
            },
            "storage_size": {
                "message": f"storage size exceeding {flag_condition}",
                "next_steps": """
                    Clean up repository using these tips: https://docs.gitlab.com/ee/user/project/repository/reducing_the_repo_size_using_git.html.
                    Examine any job artifacts that may be present in the project. Job artifacts do not migrate, but will contribute to the overall storage size of the project
                """
            },
            "packages": {
                "message": f"built packages were detected: [{flag_condition}]",
                "next_steps": "Plan for a manual migration of this project's packages or investigate using the pkgs_importer tool to migrate packages: https://gitlab.com/gitlab-org/ci-cd/package-stage/pkgs_importer"
            },
            "packages_size": {
                "message": f"Total packages size exceeding {flag_condition}",
                "next_steps": """
                    The total size of packages in this project exceeds 20 GB, which may impact migration and storage costs.
                    Consider cleaning up unused or old packages to reduce the total size.
                    You can use the GitLab API or user interface to delete packages that are no longer needed.
                    Refer to the documentation on package cleanup: https://docs.gitlab.com/ee/user/packages/package_registry/reduce_storage_usage.html
                """
            },
            "container_registry_size": {
                "message": f"Total containers size exceeding {flag_condition}",
                "next_steps": "Clean up any unused container registry repositories, images, and tags"
            },
            "issues": {
                "message": f"issue count exceeding {flag_condition}",
                "next_steps": """
                    Review the existing issues in the project to see if any can be deleted.
                    Unfortunately given the large number of issues, this project has a higher chance of failing compared to other projects with a lower issue count.
                    The only way to improve the chance of a successful import in this case is to decrease the number of issues in the project.
                """
            },
            "pipelines": {
                "message": f"number of executed pipelines exceeding {flag_condition}",
                "next_steps": """
                    Clean up the pipelines with our pipeline-cleaner utility: https://gitlab.com/gitlab-org/professional-services-automation/tools/utilities/pipeline-cleaner
                    Or
                    Trim or remove older CI pipelines using these steps: https://gitlab.com/gitlab-org/professional-services-automation/tools/migration/congregate/-/blob/master/runbooks/migrations-to-dot-com.md#trim-or-remove-project-ci-pipelines
                """
            },
            "merge_requests": {
                "message": f"number of merge requests exceeding {flag_condition}",
                "next_steps": """
                    Review the existing merge requests in the project to see if any can be deleted.
                    Unfortunately given the large number of merge requests, this project has a higher chance of failing compared to other projects with a lower merge request count.
                    We can try importing the project through the rails console instead of the API to improve the chances of a successful import,
                    but this will require terminal level access to your destination GitLab instance and we still cannot guarantee this will be successful.
                """
            },
            "branches": {
                "message": f"number of branches exceeding {flag_condition}",
                "next_steps": "Remove any stale or merged branches"
            },
            "commits": {
                "message": f"Commit count exceeding {flag_condition}",
                "next_steps": """
                    Large numbers of commits can impact migration performance.
                    Consider squashing commits where possible to reduce the total commit count.
                    Ensure that important history is preserved during this process.
                """
            },
            "tags": {
                "message": f"number of tags exceeding {flag_condition}",
                "next_steps": """
                    Review repository for any tags that can be removed.
                    Before a migration starts, plan to remove all the tags in the remote repository.
                    Keep all of the tags in a local, up-to-date copy of the repository so you can push the tags back up to the remote after the migration completes
                """
            }
        }
        return copy(flag_remediation.get(asset))
