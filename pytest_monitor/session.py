import datetime
import json
import memory_profiler
import requests
import subprocess
import warnings

from pytest_monitor.handler import DBHandler


class PyTestMonitorSession(object):
    def __init__(self, db=None, remote=None, component=''):
        self.__run_date = datetime.datetime.now().isoformat()
        self.__db = DBHandler(db) if db else None
        self.__remote = remote
        self.__component = component
        self.__scm = ''
        self.__eid = (None, None)
        self.__mem_usage_base = None

        self.prepare()

    @property
    def remote_env_id(self):
        return self.__eid[1]

    @property
    def db_env_id(self):
        return self.__eid[0]

    def get_env_id(self, env):
        db, remote = None, None
        if self.__db:
            row = self.__db.query('SELECT ENV_H FROM EXECUTION_CONTEXTS WHERE ENV_H= ?', (env.hash(),))
            db = row[0] if row else None
        if self.__remote:
            r = requests.get(f'{self.__remote}/contexts', params=dict(environ_hash=env.hash()))
            remote = None
            if r.status_code == 200:
                remote = json.loads(r.text)
                if remote['contexts']:
                    remote = remote['contexts'][0]['h']
                else:
                    remote = None
        return db, remote

    def determine_scm_revision(self):
        for cmd in [r'git rev-parse HEAD', r'p4 changes -m1 \#have']:
            p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            p_out, _ = p.communicate()
            if p.returncode == 0:
                self.__scm = p_out.decode().split('\n')[0]
                return

    def set_environment_info(self, env):
        self.__eid = self.get_env_id(env)
        db_id, remote_id = self.__eid
        if self.__db and db_id is None:
            self.__db.insert_execution_context(env)
            db_id = self.__db.query('select ENV_H from EXECUTION_CONTEXTS where ENV_H = ?', (env.hash(),))[0]
        if self.__remote and remote_id is None:
            # We must postpone that to be run at the end of the pytest session.
            r = requests.post(f'{self.__remote}/contexts/', json=env.to_dict())
            if r.status_code != 200:
                warnings.warn(f'Cannot insert execution context in remote server (rc={r.status_code}! Deactivating...')
                self.__remote = ''
            else:
                remote_id = json.loads(r.text)['h']
        self.__eid = db_id, remote_id
        self.determine_scm_revision()

    def prepare(self):
        def dummy():
            return True

        self.__mem_usage_base = memory_profiler.memory_usage((dummy,), max_usage=True)
        if self.__db:
            self.__db.prepare()

    def add_test_info(self, item, kind, component, item_start_time, total_time, user_time, kernel_time, mem_usage):
        mem_usage = float(mem_usage) - self.__mem_usage_base
        cpu_usage = (user_time + kernel_time) / total_time
        item_start_time = datetime.datetime.fromtimestamp(item_start_time).isoformat()
        final_component = self.__component.format(user_component=component)
        if final_component.endswith('.'):
            final_component = final_component[:-1]
        if self.__db and self.db_env_id is not None:
            self.__db.insert_metric(self.__run_date, item_start_time, self.db_env_id, self.__scm, item, kind,
                                    final_component, total_time, user_time, kernel_time, cpu_usage, mem_usage)
        if self.__remote and self.remote_env_id is not None:
            r = requests.post(f'{self.__remote}/metrics/',
                              json=dict(run_date=self.__run_date, context_h=self.remote_env_id, scm_ref=self.__scm,
                                        item=item, kind=kind, component=final_component, total_time=total_time,
                                        item_start_time=item_start_time, user_time=user_time,
                                        kernel_time=kernel_time,
                                        cpu_usage=cpu_usage, mem_usage=mem_usage))
            if r.status_code != 200:
                print(r.text)
                self.__remote = ''
                msg = f"Cannot insert values in remote monitor server ({r.status_code})! Deactivating...')"
                warnings.warn(msg)
