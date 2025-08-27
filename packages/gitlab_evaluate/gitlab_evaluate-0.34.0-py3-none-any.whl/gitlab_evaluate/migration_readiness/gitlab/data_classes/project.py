from dataclasses import dataclass, asdict

@dataclass
class Project:
    project: str
    id: str
    url: str
    kind: str
    namespace: str
    last_activity_at: str
    mirror: bool = False
    archived: bool = False
    pipelines: float = 0.0
    pipelines_over: bool = False
    issues: float = 0.0
    issues_over: bool = False
    branches: float = 0.0
    branches_over: bool = False
    commit_count: float = 0.0
    commit_count_over: bool = False
    merge_requests: float = 0.0
    merge_requests_over: bool = False
    storage_size: float = 0.0
    storage_size_over: bool = False
    repository_size: float = 0.0
    repository_size_over: bool = False
    wiki_size: float = 0.0
    wiki_size_over: bool = False
    lfs_objects_size: float = 0.0
    lfs_objects_size_over: bool = False
    build_artifacts_size: float = 0.0
    build_artifacts_size_over: bool = False
    snippets_size: float = 0.0
    snippets_size_over: bool = False
    uploads_size: float = 0.0
    uploads_size_over: bool = False
    tags: float = 0.0
    tags_over: bool = False
    package_types_in_use: str = ''
    packages_size: float = 0.0
    packages_size_over: bool = False
    container_tag_count: int = 0
    container_registry_size: float = 0.0
    container_registry_size_over: bool = False
    estimated_export_size: float = 0.0
    estimated_export_size_over: bool = False
    estimated_export_size_s3_over: bool = False

    def to_dict(self):
        return asdict(self)