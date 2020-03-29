import hashlib
import multiprocessing
import os
import platform
import psutil
import socket
import subprocess
import sys


def determine_scm_revision():
    for cmd in [r'git rev-parse HEAD', r'p4 changes -m1 \#have']:
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p_out, _ = p.communicate()
        if p.returncode == 0:
            return p_out.decode().split('\n')[0]
    return ''


def _get_cpu_string():
    if platform.system().lower() == "darwin":
        old_path = os.environ['PATH']
        os.environ['PATH'] = old_path + ':' + '/usr/sbin'
        ret = subprocess.check_output('sysctl -n machdep.cpu.brand_string', shell=True).decode().strip()
        os.environ['PATH'] = old_path
        return ret
    elif platform.system().lower() == 'linux':
        with open('/proc/cpuinfo', 'r', encoding='utf-8') as f:
            lines = [i for i in f if i.startswith('model name')]
        if lines:
            return lines[0].split(':')[1].strip()
    return platform.processor()


class ExecutionContext:
    def __init__(self):
        self.__cpu_count = multiprocessing.cpu_count()
        self.__cpu_vendor = _get_cpu_string()
        self.__cpu_freq_base = psutil.cpu_freq().current
        self.__proc_typ = platform.processor()
        self.__tot_mem = int(psutil.virtual_memory().total / 1024**2)
        self.__fqdn = socket.getfqdn()
        self.__machine = platform.machine()
        self.__arch = platform.architecture()[0]
        self.__system = f'{platform.system()} - {platform.release()}'
        self.__py_ver = sys.version

    def to_dict(self):
        return dict(cpu_count=self.cpu_count,
                    cpu_frequency=self.cpu_frequency,
                    cpu_type=self.cpu_type,
                    cpu_vendor=self.cpu_vendor,
                    ram_total=self.ram_total,
                    machine_node=self.fqdn,
                    machine_type=self.machine,
                    machine_arch=self.architecture,
                    system_info=self.system_info,
                    python_info=self.python_info,
                    h=self.hash())

    @property
    def cpu_count(self):
        return self.__cpu_count

    @property
    def cpu_frequency(self):
        return self.__cpu_freq_base

    @property
    def cpu_type(self):
        return self.__proc_typ

    @property
    def cpu_vendor(self):
        return self.__cpu_vendor

    @property
    def ram_total(self):
        return self.__tot_mem

    @property
    def fqdn(self):
        return self.__fqdn

    @property
    def machine(self):
        return self.__machine

    @property
    def architecture(self):
        return self.__arch

    @property
    def system_info(self):
        return self.__system

    @property
    def python_info(self):
        return self.__py_ver

    def hash(self):
        hr = hashlib.md5()
        hr.update(str(self.__cpu_count).encode())
        hr.update(str(self.__cpu_freq_base).encode())
        hr.update(str(self.__proc_typ).encode())
        hr.update(str(self.__tot_mem).encode())
        hr.update(str(self.__fqdn).encode())
        hr.update(str(self.__machine).encode())
        hr.update(str(self.__arch).encode())
        hr.update(str(self.__system).encode())
        hr.update(str(self.__py_ver).encode())
        return hr.hexdigest()
