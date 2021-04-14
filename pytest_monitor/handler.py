import sqlite3


class DBHandler:
    def __init__(self, db_path):
        self.__db = db_path
        self.__cnx = sqlite3.connect(self.__db) if db_path else None
        self.prepare()

    def query(self, what, bind_to, many=False):
        cursor = self.__cnx.cursor()
        cursor.execute(what, bind_to)
        return cursor.fetchall() if many else cursor.fetchone()

    def insert_session(self, h, run_date, scm_id, description):
        with self.__cnx:
            self.__cnx.execute('insert into TEST_SESSIONS(SESSION_H, RUN_DATE, SCM_ID, RUN_DESCRIPTION)'
                               ' values (?,?,?,?)',
                               (h, run_date, scm_id, description))

    def insert_metric(self, session_id, env_id, item_start_date, item, item_path, item_variant,
                      item_loc, kind, component, total_time, user_time, kernel_time, cpu_usage, mem_usage):
        with self.__cnx:
            self.__cnx.execute('insert into TEST_METRICS(SESSION_H,ENV_H,ITEM_START_TIME,ITEM,'
                               'ITEM_PATH,ITEM_VARIANT,ITEM_FS_LOC,KIND,COMPONENT,TOTAL_TIME,'
                               'USER_TIME,KERNEL_TIME,CPU_USAGE,MEM_USAGE) '
                               'values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                               (session_id, env_id, item_start_date, item, item_path,
                                item_variant, item_loc, kind, component, total_time, user_time,
                                kernel_time, cpu_usage, mem_usage))

    def insert_execution_context(self, exc_context):
        with self.__cnx:
            self.__cnx.execute('insert into EXECUTION_CONTEXTS(CPU_COUNT,CPU_FREQUENCY_MHZ,CPU_TYPE,CPU_VENDOR,'
                               'RAM_TOTAL_MB,MACHINE_NODE,MACHINE_TYPE,MACHINE_ARCH,SYSTEM_INFO,'
                               'PYTHON_INFO,ENV_H) values (?,?,?,?,?,?,?,?,?,?,?)',
                               (exc_context.cpu_count, exc_context.cpu_frequency, exc_context.cpu_type,
                                exc_context.cpu_vendor, exc_context.ram_total, exc_context.fqdn, exc_context.machine,
                                exc_context.architecture, exc_context.system_info, exc_context.python_info,
                                exc_context.hash()))

    def prepare(self):
        cursor = self.__cnx.cursor()
        cursor.execute('''
CREATE TABLE IF NOT EXISTS TEST_SESSIONS(
    SESSION_H varchar(64) primary key not null unique, -- Session identifier
    RUN_DATE varchar(64), -- Date of test run
    SCM_ID varchar(128), -- SCM change id
    RUN_DESCRIPTION json
);''')
        cursor.execute('''
CREATE TABLE IF NOT EXISTS TEST_METRICS (
    SESSION_H varchar(64), -- Session identifier
    ENV_H varchar(64), -- Environment description identifier
    ITEM_START_TIME varchar(64), -- Effective start time of the test
    ITEM_PATH varchar(4096), -- Path of the item, following Python import specification
    ITEM varchar(2048), -- Name of the item
    ITEM_VARIANT varchar(2048), -- Optional parametrization of an item.
    ITEM_FS_LOC varchar(2048), -- Relative path from pytest invocation directory to the item's module.
    KIND varchar(64), -- Package, Module or function
    COMPONENT varchar(512) NULL, -- Tested component if any
    TOTAL_TIME float, -- Total time spent running the item
    USER_TIME float, -- time spent in user space
    KERNEL_TIME float, -- time spent in kernel space
    CPU_USAGE float, -- cpu usage
    MEM_USAGE float, -- Max resident memory used.
    FOREIGN KEY (ENV_H) REFERENCES EXECUTION_CONTEXTS(ENV_H),
    FOREIGN KEY (SESSION_H) REFERENCES TEST_SESSIONS(SESSION_H)
);''')
        cursor.execute('''
CREATE TABLE IF NOT EXISTS EXECUTION_CONTEXTS (
   ENV_H varchar(64) primary key not null unique,
   CPU_COUNT integer,
   CPU_FREQUENCY_MHZ integer,
   CPU_TYPE varchar(64),
   CPU_VENDOR varchar(256),
   RAM_TOTAL_MB integer,
   MACHINE_NODE varchar(512),
   MACHINE_TYPE varchar(32),
   MACHINE_ARCH varchar(16),
   SYSTEM_INFO varchar(256),
   PYTHON_INFO varchar(512)
);
''')
        self.__cnx.commit()
