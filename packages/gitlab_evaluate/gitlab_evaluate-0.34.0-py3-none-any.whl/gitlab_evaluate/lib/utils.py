import datetime
import importlib.metadata
import toml
import sqlite3
from os.path import exists
from re import sub
from gitlab_evaluate.migration_readiness.gitlab import limits
from gitlab_ps_utils.dict_utils import dig


def write_headers(row_index, worksheet, headers, cell_format):
    for i in range(0, len(headers)):
        worksheet.write(row_index, i, headers[i], cell_format)


def write_to_workbook(worksheet, data, headers):
    for row, r in enumerate(data, start=1):
        for col, h in enumerate(headers):
            worksheet.write(row, col, r.get(h, ''))


def append_to_workbook(worksheet, data, headers):
    row = len(worksheet.table)
    for d in data:
        for col, h in enumerate(headers):
            write_to_worksheet(worksheet, row, col, d.get(h, d.get(h.lower(), '')))


def write_to_worksheet(worksheet, row, col, item):
    if isinstance(item, bool):
        worksheet.write(row, col, str(item))
    elif isinstance(item, str):
        worksheet.write(row, col, item)
    elif isinstance(item, (int, float)):
        worksheet.write_number(row, col, item)


def check_size(k, v):
    # TODO: Dictionary of function pointers
    if k in ["storage_size", "lfs_objects_size", "uploads_size", "build_artifacts_size", "wiki_size"]:
        return check_storage_size(v)
    if k == "snippets_size":
        return check_num_snippets(v)
    if k == "commit_count":
        return check_num_commits(v)
    if k == "repository_size":
        return check_file_size(v)
    if k == "estimated_export_size":
        return check_export_size_5(v)
    if k == "estimated_export_size_s3":
        return check_export_size_10(v)


def check_num_pl(i):
    return i > limits.PIPELINES_COUNT


def check_num_br(i):
    return i > limits.BRANCHES_COUNT


def check_num_commits(i):
    return i > limits.COMMITS_COUNT


def check_num_snippets(i):
    return i > limits.SNIPPETS_COUNT


def check_repository_size(i):
    return i > limits.REPOSITORY_SIZE


def check_storage_size(i):
    '''Includes artifacts, repositories, wiki, and other items.'''
    return i > limits.STORAGE_SIZE


def check_packages_size(i):
    return i > limits.PACKAGES_SIZE


def check_registry_size(i):
    return i > limits.CONTAINERS_SIZE


def check_file_size(i):
    # File size limit is 5GB
    return i > limits.FILE_SIZE


def check_export_size_5(i):
    # File import limit is 5Gb
    return i > limits.IMPORT_SIZE


def check_export_size_10(i):
    # File import limit via S3 is 10Gb
    return i > limits.IMPORT_SIZE_S3


def check_num_issues(i):
    return i > limits.ISSUES_COUNT


def check_num_mr(i):
    return i > limits.MERGE_REQUESTS_COUNT


def check_num_tags(i):
    return i > limits.TAGS_COUNT


def check_proj_type(i):
    return i


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def to_camel_case(s):
    """
        Shameless copy from https://www.w3resource.com/python-exercises/string/python-data-type-string-exercise-96.php
    """
    s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
    return ''.join([s[0].lower(), s[1:]])

def to_snake_case(s):
    """
        Shameless copy from https://www.w3resource.com/python-exercises/string/python-data-type-string-exercise-98.php
    """
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
            sub('([A-Z]+)', r' \1',
                s.replace('-', ' '))).split()).lower()

def nested_snake_case(dict_obj):

    """
    Recursively converts all keys in a nested dictionary from camelCase to snake_case.
    
    Args:
        dict_obj: Dictionary object to convert keys for
        
    Returns:
        Dictionary with all keys converted to snake_case
    """
    if not isinstance(dict_obj, dict):
        return dict_obj
    
    result = {}
    for key, value in dict_obj.items():
        # Convert the key to snake_case
        snake_key = to_snake_case(key)
        
        # Recursively process nested dictionaries
        if isinstance(value, dict):
            result[snake_key] = nested_snake_case(value)
        elif isinstance(value, list):
            # Handle lists that might contain dictionaries
            result[snake_key] = [nested_snake_case(item) if isinstance(item, dict) else item for item in value]
        else:
            result[snake_key] = value
    
    return result


def get_date_run():
    return datetime.datetime.now().date().strftime("%Y-%m-%d")


def get_countif(sheet_name, search_string, column_letter):
    return f'COUNTIF(\'{sheet_name}\'!{column_letter}:{column_letter}, "{search_string}")'


def get_countifs(sheet_name, search_string_1, column_letter_1, search_string_2, column_letter_2):
    return f'COUNTIFS(\'{sheet_name}\'!{column_letter_1}:{column_letter_1}, "{search_string_1}", \'{sheet_name}\'!{column_letter_2}:{column_letter_2}, "{search_string_2}")'


def get_counta(sheet_name, column_letter):
    return f'COUNTA(\'{sheet_name}\'!{column_letter}:{column_letter})'


def get_if(logical_expression, value_if_true, value_if_false):
    return f'IF({logical_expression}, {value_if_true}, {value_if_false})'


def get_sum(sheet_name, column_letter):
    return f'SUM(\'{sheet_name}\'!{column_letter}:{column_letter})'


def get_sumif(sheet_name, column_letter_1, column_letter_2, search_string):
    return f'SUMIF(\'{sheet_name}\'!{column_letter_1}:{column_letter_1}, "{search_string}", \'{sheet_name}\'!{column_letter_2}:{column_letter_2})'


def get_reading_the_output_link():
    return 'https://gitlab.com/gitlab-org/professional-services-automation/tools/utilities/evaluate/-/blob/main/reading-the-output.md?ref_type=heads'


def get_upgrade_path(gitlab_version):
    return 'https://gitlab-com.gitlab.io/support/toolbox/upgrade-path/?current='+gitlab_version


def get_whats_changed(gitlab_version):
    # Ex: formats 16.8.2-ee to 16_8
    fmt_version = ''
    split = gitlab_version.split('.')[:2]
    for i, _ in enumerate(split):
        if len(split[i]) == 1:
            split[i] = f"0{split[i]}"
    fmt_version = "_".join(split)
    return f'https://gitlab-com.gitlab.io/cs-tools/gitlab-cs-tools/what-is-new-since/?tab=features&minVersion={fmt_version}&selectedSaaS=self-managed+available'


def get_package_version():
    '''
        Returns current version of Evaluate
    '''
    # Local dev check
    if exists('pyproject.toml'):
        pproj = {}
        with open('pyproject.toml', 'r') as f:
            pproj = toml.load(f)
        if (version := dig(pproj, 'tool', 'poetry', 'version')) and dig(pproj, 'tool', 'poetry', 'name', default='') == 'gitlab_evaluate':
            return version
    # Built package check
    return importlib.metadata.version("gitlab-evaluate")


def sqlite_connection(db, rows_as_dicts=False):
    con = sqlite3.connect(db)
    if rows_as_dicts:
        con.row_factory = sqlite3.Row
    cur = con.cursor()
    return con, cur
