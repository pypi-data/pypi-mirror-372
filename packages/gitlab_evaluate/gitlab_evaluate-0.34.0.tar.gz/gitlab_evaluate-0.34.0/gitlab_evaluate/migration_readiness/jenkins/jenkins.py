from time import sleep
from json import dumps, loads
from base64 import b64encode
from urllib.parse import unquote
from traceback import print_exc
from jenkins import DEFAULT_TIMEOUT, JOBS_QUERY_TREE, JOBS_QUERY, Jenkins
from dacite import from_dict
from gitlab_ps_utils.processes import MultiProcessing
from gitlab_ps_utils.logger import myLogger
from gitlab_ps_utils.misc_utils import strip_netloc
from gitlab_evaluate.migration_readiness.jenkins.data_classes.job import Job
from gitlab_evaluate.lib.utils import sqlite_connection


class MultiProcessJenkins(Jenkins):
    """
        Extended class to multiprocess retrieving job data
    """
    def __init__(self, url, username=None, password=None, timeout=DEFAULT_TIMEOUT, processes=None, ssl_verify=True):
        super().__init__(url, username, password, timeout)
        self._session.verify = ssl_verify
        self.processes = processes
        self.multi = MultiProcessing()
        self.logger = myLogger(__name__, '.', log_dir='.')
        self.num_jobs = 1

    def jobs_count(self):
        '''Get the number of jobs on the Jenkins server

        :returns: Total number of jobs, ``int``
        '''
        if self.num_jobs:
            return self.num_jobs
        # else:
        #     return len(self.get_all_jobs())

    def get_jobs(self, folder_depth=0, folder_depth_per_request=10, view_name=None):
        """Get list of jobs.

        Each job is a dictionary with 'name', 'url', 'color' and 'fullname'
        keys.

        If the ``view_name`` parameter is present, the list of
        jobs will be limited to only those configured in the
        specified view. In this case, the job dictionary 'fullname' key
        would be equal to the job name.

        :param folder_depth: Number of levels to search, ``int``. By default
            0, which will limit search to toplevel. None disables the limit.
        :param folder_depth_per_request: Number of levels to fetch at once,
            ``int``. See :func:`get_all_jobs`.
        :param view_name: Name of a Jenkins view for which to
            retrieve jobs, ``str``. By default, the job list is
            not limited to a specific view.
        :returns: list of jobs, ``[{str: str, str: str, str: str, str: str}]``

        Example::

            >>> jobs = server.get_jobs()
            >>> print(jobs)
            [{
                u'name': u'all_tests',
                u'url': u'http://your_url.here/job/all_tests/',
                u'color': u'blue',
                u'fullname': u'all_tests'
            }]

        """

        if view_name:
            return self._get_view_jobs(name=view_name)
        else:
            return self.get_all_jobs(folder_depth=folder_depth,
                                     folder_depth_per_request=folder_depth_per_request)

    def get_all_jobs(self, folder_depth=None, folder_depth_per_request=10):
        """Get list of all jobs recursively to the given folder depth.

        Each job is a dictionary with 'name', 'url', 'color' and 'fullname'
        keys.

        :param folder_depth: Number of levels to search, ``int``. By default
            None, which will search all levels. 0 limits to toplevel.
        :param folder_depth_per_request: Number of levels to fetch at once,
            ``int``. By default 10, which is usually enough to fetch all jobs
            using a single request and still easily fits into an HTTP request.
        :returns: list of jobs, ``[ { str: str} ]``

        .. note::

            On instances with many folders it would not be efficient to fetch
            each folder separately, hence `folder_depth_per_request` levels
            are fetched at once using the ``tree`` query parameter::

                ?tree=jobs[url,color,name,jobs[...,jobs[...,jobs[...,jobs]]]]

            If there are more folder levels than the query asks for, Jenkins
            returns empty [#]_ objects at the deepest level::

                {"name": "folder", "url": "...", "jobs": [{}, {}, ...]}

            This makes it possible to detect when additional requests are
            needed.

            .. [#] Actually recent Jenkins includes a ``_class`` field
                everywhere, but it's missing the requested fields.
        """
        _, cursor = sqlite_connection('jenkins.db')
        jobs_query = 'jobs'
        for _ in range(folder_depth_per_request):
            jobs_query = JOBS_QUERY_TREE % jobs_query
        jobs_query = JOBS_QUERY % jobs_query

        jobs_list = []
        job_types = []
        # Build out initial queue before starting multiprocessing
        for job in self.get_info(query=jobs_query)['jobs']:
            self.add_job_to_queue(job)

        # Start processing jobs through queue
        self.multi.start_multi_process_stream_with_args(self.handle_retrieving_job, self.check_job_queue(), jobs_query, processes=self.processes)
    
        # Get all jobs and job types after scanning the instance
        job_results = cursor.execute("SELECT * FROM jobs")
        for result in job_results.fetchall():
            jobs_list.append(Job(*result).to_dict())
        job_type_results = cursor.execute("SELECT * FROM job_types")
        for result in job_type_results.fetchall():
            job_types.append(result[0])
        self.num_jobs = len(jobs_list)
        return jobs_list, job_types

    def handle_retrieving_job(self, jobs_query, job):
        """
            Multiprocessing handler function for each job stored in the queue
        """
        try:
            data = self.get_full_job_data(loads(job[1]))
            # If an individual job is detected
            if 'jobs' not in data:
                self.insert_job_data((job[0], data))
            # If the job is a folder
            else:
                if 'jobs' in data and isinstance(data['jobs'], list):
                    # Iterate over each child item in the folder
                    for child in data['jobs']:
                        if child['_class'] != 'com.cloudbees.hudson.plugins.folder.Folder':
                            self.add_job_to_queue(child)
                        else:
                            folder_contents = self.get_full_job_data(child).get('jobs', [])
                            for folder_content in folder_contents:
                                self.add_job_to_queue(folder_content)
                # Once the folder has been processed, remove it from the queue
                job_id = b64encode(data['url'].encode()).decode('ascii')
                self.remove_job_from_queue(job_id)
        except Exception as e:
            print(e)
            print(print_exc())

    def insert_job_data(self, job):
        """
            Function to store the job and job type in SQLite 
            and then remove the processed job from the queue table
        """
        connection, cursor = sqlite_connection('jenkins.db')
        try:
            queue_id, job_data = job
            insert_query = f"INSERT or IGNORE INTO jobs VALUES {tuple(from_dict(Job, job_data).to_dict().values())}"
            cursor.execute(insert_query)
            connection.commit()
            check_query = "SELECT type FROM job_types WHERE type = ?"
            job_type_check = cursor.execute(check_query, (job_data['_class'],))
            if not job_type_check.fetchone():
                job_class = job_data['_class']
                insert_job_class_query = "INSERT INTO job_types VALUES (?)"
                cursor.execute(insert_job_class_query, (job_class,))
                connection.commit()
            self.remove_job_from_queue(queue_id)
        except Exception as e:
            print("\t\t***Exception saving job data")
            print(e)
            print(print_exc())
    
    def get_full_job_data(self, job):
        """
            Retrieves the full job data from the Jenkins API
        """
        if not isinstance(job, dict):
            job = loads(job)
        item = unquote(job['url']).split(strip_netloc(job['url']))[-1]
        return self.get_info(item)

    def add_job_to_queue(self, job):
        connection, cursor = sqlite_connection('jenkins.db')
        try:
            job_id = b64encode(job['url'].encode()).decode('ascii')
            job_to_process = (job_id, dumps(job))
            query = "INSERT or IGNORE INTO jobs_to_process VALUES (?,?)"
            cursor.execute(query, (job_to_process))
            connection.commit()
        except Exception as e:
            print("\t\t***Exception adding to queue")
            print(e)
    
    def remove_job_from_queue(self, job_id):
        connection, cursor = sqlite_connection('jenkins.db')
        try:
            query = "DELETE FROM jobs_to_process WHERE id = ?"
            cursor.execute(query, (job_id,))
            connection.commit()
        except Exception as e:
            print("\t\t***Exception deleting job queue data")
            print(e)

    def check_job_queue(self):
        try:
            _, cursor = sqlite_connection('jenkins.db')
            while self.get_job_queue_count() > 0:
                
                job_queue = cursor.execute("SELECT * FROM jobs_to_process")
                data = job_queue.fetchall()
                for result in data:
                    yield result
                sleep(2)
                job_count_query = cursor.execute("SELECT COUNT(*) FROM jobs")
                print(f"Total jobs scanned: {job_count_query.fetchone()[0]}")
        except Exception as e:
                print("\t\t***Exception checking job queue")
                print(e)
    
    def get_job_queue_count(self):
        _, cursor = sqlite_connection('jenkins.db')
        job_queue_count = cursor.execute("SELECT COUNT(*) FROM jobs_to_process")
        count = job_queue_count.fetchone()[0]
        return count

    
