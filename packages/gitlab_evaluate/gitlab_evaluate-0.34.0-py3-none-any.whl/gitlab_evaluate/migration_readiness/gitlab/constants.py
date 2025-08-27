COLUMNS = [
    'project',
    'id',
    'url',
    'kind',
    'namespace',
    'last_activity_at',
    'mirror',
    'archived',
    'pipelines',
    'pipelines_over',
    'issues',
    'issues_over',
    'branches',
    'branches_over',
    'commit_count',
    'commit_count_over',
    'merge_requests',
    'merge_requests_over',
    'storage_size',
    'storage_size_over',
    'repository_size',
    'repository_size_over',
    'wiki_size',
    'wiki_size_over',
    "lfs_objects_size",
    "lfs_objects_size_over",
    "build_artifacts_size",
    "build_artifacts_size_over",
    "snippets_size",
    "snippets_size_over",
    "uploads_size",
    "uploads_size_over",
    'tags',
    'tags_over',
    'package_types_in_use',
    'packages_size',
    'packages_size_over',
    'container_tag_count',
    'container_registry_size',
    'container_registry_size_over',
    'estimated_export_size',
    'estimated_export_size_over',
    'estimated_export_size_s3_over'
]

REPORT_HEADERS = [
    'project',
    'reason'
]
USER_HEADERS = [
    'username',
    'email',
    'state',
    'using_license_seat',
    'is_admin'
]
ACCOUNT_HEADERS = [
    'Account',
    'Comments'
]
PROJECT_SUMMARY_HEADERS = [
    'Projects',
    'ALL PROJECTS',
    'ONLY GROUP PROJECTS',
    'Comments'
]
PROJECTS_TO_REVIEW_HEADERS = [
    'Projects To Review',
    'ALL PROJECTS',
    'ONLY GROUP PROJECTS',
    'Comments'
]
METRICS_HEADERS = [
    'Metrics',
    'ALL PROJECTS',
    'ONLY GROUP PROJECTS',
    'Comments'
]