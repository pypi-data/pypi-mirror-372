from os import getcwd
from gitlab_ps_utils.api import GitLabApi

glapi = GitLabApi(app_path=getcwd(), log_name='evaluate', timeout=120)
