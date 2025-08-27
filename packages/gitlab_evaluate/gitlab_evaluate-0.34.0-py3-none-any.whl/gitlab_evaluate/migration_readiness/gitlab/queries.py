def generate_group_project_query(full_path, after):
    return {
        'query': """
        query {
            group(fullPath:\"%s\") {
                    projects(after:\"%s\", includeSubgroups:true) {
                    nodes {
                        id,
                        name,
                        fullPath,
                        archived,
                        lastActivityAt,
                        webUrl,
                        namespace {
                            fullPath
                        }
                        statistics {
                            packagesSize,
                            containerRegistrySize,
                            repositorySize,
                            wikiSize,
                            lfsObjectsSize,
                            snippetsSize,
                            uploadsSize,
                            commitCount,
                            buildArtifactsSize,
                            storageSize
                        }
                        packages {
                            nodes {
                                packageType
                            }
                        }
                        issues {
                            count
                        }
                        mergeRequests {
                            count
                        },
                        pipelines {
                            count
                        }
                    }
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                }
            }
        }
        """ % (full_path, after)
    }


def generate_all_projects_query(after):
    return {
        'query': """
            query {
                projects(after:\"%s\") {
                    nodes {
                        id,
                        name,
                        fullPath,
                        archived,
                        lastActivityAt,
                        webUrl,
                        namespace {
                            fullPath
                        }
                        statistics {
                            packagesSize,
                            containerRegistrySize,
                            repositorySize,
                            wikiSize,
                            lfsObjectsSize,
                            snippetsSize,
                            uploadsSize,
                            commitCount,
                            buildArtifactsSize,
                            storageSize
                        }
                        packages {
                            nodes {
                                packageType
                            }
                        }
                        issues {
                            count
                        }
                        mergeRequests {
                            count
                        },
                        pipelines {
                            count
                        }
                    }
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                }
            }
            """ % after
    }

def generate_container_registry_tag_count(full_path):
    return {
        'query': """
            query {
                project(fullPath: \"%s\") {
                    name,
                    containerRepositories {
                        nodes {
                            tagsCount
                        }
                    }
                }
        }
        """ % full_path
    }

def generate_group_stats_query(full_path):
    return {
        'query': """
            query {
                group(fullPath: \"%s\") {
                    projects {
                        count
                    }
                    issues {
                        count
                    }
                    descendantGroups {
                        count
                    }
                    groupMembersCount
                    mergeRequests {
                        count
                    }
                }
            }
        """ % full_path
    }