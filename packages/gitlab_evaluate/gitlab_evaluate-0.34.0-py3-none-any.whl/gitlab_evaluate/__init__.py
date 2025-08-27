from os import getcwd
from gitlab_ps_utils.logger import myLogger

log = myLogger(__name__, app_path=getcwd(), log_dir='.', log_name='evaluate')