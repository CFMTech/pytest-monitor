import datetime
import hashlib
import json
import memory_profiler
import os
import psutil
import requests
import warnings

from pytest_monitor.handler import DBHandler
from pytest_monitor.sys_utils import ExecutionContext, determine_scm_revision


class PyTestMonitorSession(object):
    def __init__(self, db=None, remote=None, component='', scope=None):
        self.__db = None
        if db:
            self.__db = DBHandler(db)
        self.__remote = remote
        self.__component = component
        self.__session = ''
        self.__scope = scope or []
        self.__eid = (None, None)
        self.__mem_usage_base = None
        self.__process = psutil.Process(os.getpid())

    @property
    def remote_env_id(self):
        return self.__eid[1]

    @property
    def db_env_id(self):
        return self.__eid[0]

    @property
    def process(self):
        return self.__process

    def get_env_id(self, env):
        db, remote = None, None
        if self.__db:
            row = self.__db.query('SELECT ENV_H FROM EXECUTION_CONTEXTS WHERE ENV_H= ?', (env.hash(),))
            db = row[0] if row else None
        if self.__remote:
            r = requests.get(f'{self.__remote}/contexts/{env.hash()}')
            remote = None
            if r.status_code == 200:
                remote = json.loads(r.text)
                if remote['contexts']:
                    remote = remote['contexts'][0]['h']
                else:
                    remote = None
        return db, remote

    def compute_info(self, description):
        run_date = datetime.datetime.now().isoformat()
        scm = determine_scm_revision()
        h = hashlib.md5()
        h.update(scm.encode())
        h.update(run_date.encode())
        h.update(description.encode())
        self.__session = h.hexdigest()
        # Now get memory usage base and create the database
        self.prepare()
        self.set_environment_info(ExecutionContext())
        if self.__db:
            self.__db.insert_session(self.__session, run_date, scm, description)
        if self.__remote:
            r = requests.post(f'{self.__remote}/sessions/',
                              json=dict(session_h=self.__session,
                                        run_date=run_date,
                                        scm_ref=scm,
                                        description=description))
            if r.status_code != 200:
                self.__remote = ''
                msg = f"Cannot insert session in remote monitor server ({r.status_code})! Deactivating...')"
                warnings.warn(msg)

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

    def prepare(self):
        def dummy():
            return True

        self.__mem_usage_base = memory_profiler.memory_usage((dummy,), max_usage=True)

    def add_test_info(self, item, item_path, item_variant, item_loc, kind, component,
                      item_start_time, total_time, user_time, kernel_time, mem_usage):
        if kind not in self.__scope:
            return
        mem_usage = float(mem_usage) - self.__mem_usage_base
        cpu_usage = (user_time + kernel_time) / total_time
        item_start_time = datetime.datetime.fromtimestamp(item_start_time).isoformat()
        final_component = self.__component.format(user_component=component)
        if final_component.endswith('.'):
            final_component = final_component[:-1]
        item_variant = item_variant.replace('-', ', ')  # No choice
        if self.__db and self.db_env_id is not None:
            self.__db.insert_metric(self.__session, self.db_env_id, item_start_time, item,
                                    item_path, item_variant, item_loc, kind, final_component, total_time, user_time,
                                    kernel_time, cpu_usage, mem_usage)
        if self.__remote and self.remote_env_id is not None:
            r = requests.post(f'{self.__remote}/metrics/',
                              json=dict(session_h=self.__session,
                                        context_h=self.remote_env_id,
                                        item_start_time=item_start_time,
                                        item_path=item_path,
                                        item=item,
                                        item_variant=item_variant,
                                        item_fs_loc=item_loc,
                                        kind=kind,
                                        component=final_component,
                                        total_time=total_time,
                                        user_time=user_time,
                                        kernel_time=kernel_time,
                                        cpu_usage=cpu_usage,
                                        mem_usage=mem_usage))
            if r.status_code != 200:
                self.__remote = ''
                msg = f"Cannot insert values in remote monitor server ({r.status_code})! Deactivating...')"
                warnings.warn(msg)
