import hashlib
import multiprocessing
import os
import platform
import socket
import subprocess
import sys
import warnings

import psutil


def collect_ci_info():
    # Test for jenkins
    if "BUILD_NUMBER" in os.environ and ("BRANCH_NAME" in os.environ or "JOB_NAME" in os.environ):
        br = os.environ["BRANCH_NAME"] if "BRANCH_NAME" in os.environ else os.environ["JOB_NAME"]
        return {
            "pipeline_branch": br,
            "pipeline_build_no": os.environ["BUILD_NUMBER"],
            "__ci__": "jenkinsci",
        }
    # Test for CircleCI
    if "CIRCLE_JOB" in os.environ and "CIRCLE_BUILD_NUM" in os.environ:
        return {
            "pipeline_branch": os.environ["CIRCLE_JOB"],
            "pipeline_build_no": os.environ["CIRCLE_BUILD_NUM"],
            "__ci__": "circleci",
        }
    # Test for TravisCI
    if "TRAVIS_BUILD_NUMBER" in os.environ and "TRAVIS_BUILD_ID" in os.environ:
        return {
            "pipeline_branch": os.environ["TRAVIS_BUILD_ID"],
            "pipeline_build_no": os.environ["TRAVIS_BUILD_NUMBER"],
            "__ci__": "travisci",
        }
    # Test for DroneCI
    if "DRONE_REPO_BRANCH" in os.environ and "DRONE_BUILD_NUMBER" in os.environ:
        return {
            "pipeline_branch": os.environ["DRONE_REPO_BRANCH"],
            "pipeline_build_no": os.environ["DRONE_BUILD_NUMBER"],
            "__ci__": "droneci",
        }
    # Test for Gitlab CI
    if "CI_JOB_NAME" in os.environ and "CI_PIPELINE_ID" in os.environ:
        return {
            "pipeline_branch": os.environ["CI_JOB_NAME"],
            "pipeline_build_no": os.environ["CI_PIPELINE_ID"],
            "__ci__": "gitlabci",
        }
    # Test for Bitbucket CI
    if "BITBUCKET_BRANCH" in os.environ and "BITBUCKET_BUILD_NUMBER" in os.environ:
        return {
            "pipeline_branch": os.environ["BITBUCKET_BRANCH"],
            "pipeline_build_no": os.environ["BITBUCKET_BUILD_NUMBER"],
            "__ci__": "bitbucketci",
        }
    return {}


def determine_scm_revision():
    for scm, cmd in (("git", r"git rev-parse HEAD"), ("p4", r"p4 changes -m1 \#have")):
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p_out, _ = p.communicate()
        if p.returncode == 0:
            scm_ref = p_out.decode(errors="ignore").split("\n", maxsplit=1)[0]
            if scm == "p4":
                scm_ref = scm_ref.split()[1]
            return scm_ref
    return ""


def _get_cpu_string():
    if platform.system().lower() == "darwin":
        old_path = os.environ["PATH"]
        os.environ["PATH"] = old_path + ":" + "/usr/sbin"
        ret = subprocess.check_output("sysctl -n machdep.cpu.brand_string", shell=True)
        os.environ["PATH"] = old_path
        return ret.decode().strip()
    if platform.system().lower() == "linux":
        with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
            lines = [i for i in f if i.startswith("model name")]
        if lines:
            return lines[0].split(":")[1].strip()
    return platform.processor()


class ExecutionContext:
    def __init__(self):
        self.__cpu_count = multiprocessing.cpu_count()
        self.__cpu_vendor = _get_cpu_string()
        if int(os.environ.get("PYTEST_MONITOR_FORCE_CPU_FREQ", "0")):
            self._read_cpu_freq_from_env()
        else:
            try:
                self.__cpu_freq_base = psutil.cpu_freq().current
            except (AttributeError, NotImplementedError, FileNotFoundError):
                warnings.warn("Unable to fetch CPU frequency. Trying to read it from environment..")
                self._read_cpu_freq_from_env()
        self.__proc_typ = platform.processor()
        self.__tot_mem = int(psutil.virtual_memory().total / 1024**2)
        self.__fqdn = socket.getfqdn()
        self.__machine = platform.machine()
        self.__arch = platform.architecture()[0]
        self.__system = f"{platform.system()} - {platform.release()}"
        self.__py_ver = sys.version

    def _read_cpu_freq_from_env(self):
        try:
            self.__cpu_freq_base = float(os.environ.get("PYTEST_MONITOR_CPU_FREQ", "0."))
        except (ValueError, TypeError):
            warnings.warn("Wrong type/value while reading cpu frequency from environment. Forcing to 0.0.")
            self.__cpu_freq_base = 0.0

    def to_dict(self):
        return {
            "cpu_count": self.cpu_count,
            "cpu_frequency": self.cpu_frequency,
            "cpu_type": self.cpu_type,
            "cpu_vendor": self.cpu_vendor,
            "ram_total": self.ram_total,
            "machine_node": self.fqdn,
            "machine_type": self.machine,
            "machine_arch": self.architecture,
            "system_info": self.system_info,
            "python_info": self.python_info,
            "h": self.compute_hash(),
        }

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

    def compute_hash(self):
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
