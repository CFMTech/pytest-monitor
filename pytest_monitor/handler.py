import sqlite3


class DBHandler:
    def __init__(self, db_path):
        self.__db = db_path
        self.__cnx = sqlite3.connect(self.__db) if db_path else None

    def query(self, what, bind_to, many=False):
        cursor = self.__cnx.cursor()
        cursor.execute(what, bind_to)
        return cursor.fetchall() if many else cursor.fetchone()

    def insert_metric(self, run_date, item_start_date, env_id, scm_id, item, kind, component,
                      total_time, user_time, kernel_time, cpu_usage, mem_usage):
        with self.__cnx:
            self.__cnx.execute(f'insert into TEST_METRICS(RUN_DATE,ITEM_START_TIME,ENV_H,SCM_ID,ITEM,KIND,'
                               f'COMPONENT,TOTAL_TIME,USER_TIME,KERNEL_TIME,CPU_USAGE,MEM_USAGE) '
                               f'values (?,?,?,?,?,?,?,?,?,?,?,?)',
                               (run_date, item_start_date, env_id, scm_id, item, kind, component,
                                total_time, user_time, kernel_time, cpu_usage, mem_usage))

    def insert_execution_context(self, exc_context):
        with self.__cnx:
            self.__cnx.execute(f'insert into EXECUTION_CONTEXTS(CPU_COUNT,CPU_FREQUENCY_MHZ,CPU_TYPE,CPU_VENDOR,'
                               f'RAM_TOTAL_MB,MACHINE_NODE,MACHINE_TYPE,MACHINE_ARCH,SYSTEM_INFO,'
                               f'PYTHON_INFO,ENV_H) values (?,?,?,?,?,?,?,?,?,?,?)',
                               (exc_context.cpu_count, exc_context.cpu_frequency, exc_context.cpu_type,
                                exc_context.cpu_vendor, exc_context.ram_total, exc_context.fqdn, exc_context.machine,
                                exc_context.architecture, exc_context.system_info, exc_context.python_info,
                                exc_context.hash()))

    def prepare(self):
        cursor = self.__cnx.cursor()
        cursor.execute('''
CREATE TABLE IF NOT EXISTS TEST_METRICS (
    RUN_DATE varchar(64), -- Date of test run
    ENV_H varchar(64), -- Environment description identifier
    SCM_ID varchar(128),
    ITEM_START_TIME varchar(64), -- Effective start time of the test
    ITEM varchar(4096), -- Name of the item
    KIND varchar(64), -- Package, Module or function
    COMPONENT varchar(512) NULL, -- Tested component if any
    TOTAL_TIME float, -- Total time spent running the item
    USER_TIME float, -- time spent in user space
    KERNEL_TIME float, -- time spent in kernel space
    CPU_USAGE float, -- cpu usage
    MEM_USAGE float, -- Max resident memory used.
    FOREIGN KEY (ENV_H) REFERENCES EXECUTION_CONTEXTS(ENV_H)
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
