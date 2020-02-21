import os
# -*- coding: utf-8 -*-
import memory_profiler
import psutil
import pytest
import time
import warnings

from pytest_monitor.sys_utils import ExecutionContext
from pytest_monitor.session import PyTestMonitorSession

PYTEST_MONITOR_SESSION = None
# These dictionaries are used to compute members set on each items.
# KEY is the marker set on a test function
# value is a tuple:
#  expect_args: boolean
#  internal marker attribute name: str
#  callable that set member's value
#  default value
PYTEST_MONITOR_VALID_MARKERS = {'monitor_skip_test': (False, 'monitor_skip_test', lambda x: True, False),
                                'monitor_skip_test_if': (True, 'monitor_skip_test', lambda x: bool(x), False),
                                'monitor_test': (False, 'monitor_force_test', lambda x: True, False),
                                'monitor_test_if': (True, 'monitor_force_test', lambda x: bool(x), False)}
PYTEST_MONITOR_DEPRECATED_MARKERS = {}


def pytest_addoption(parser):
    group = parser.getgroup('monitor')
    group.addoption('--restrict-scope-to', dest='mtr_scope', default='function,module',
                    help='Select the scope to monitor. By default, only function is monitored.'
                         'Values are function, class, module, session. You can set one or more of these'
                         'by listing them using a comma separated list')
    group.addoption('--parametrization-explicit', dest='want_explicit_ids', action='store_true',
                    help='Set this option to distinguish parametrized tests given their values.'
                         ' This requires the parameters to be stringifiable.')
    group.addoption('--no-monitor', action='store_true', dest='mtr_none', help='Disable all traces')
    group.addoption('--remote', action='store', dest='remote',
                    help='Remote server to send the results to. Format is <ADRESS>:<PORT>')
    group.addoption('--db', action='store', dest='mtr_db_out', default='.pymon',
                    help='Use the given sqlite database for storing results.')
    group.addoption('--no-db', action='store_true', help='Do not store results in local db.')
    group.addoption('--force-component', action='store',
                    help='Force the component to be set at the given value for the all tests run'
                         ' in this session.')
    group.addoption('--component-prefix', action='store',
                    help='Prefix each found components with the given value (applies to all tests'
                         ' run in this session).')


def pytest_configure(config):
    config.addinivalue_line("markers", "monitor_skip_test: mark test to be executed but not monitored.")
    config.addinivalue_line("markers", "monitor_skip_test_if(cond): mark test to be executed but "
                                       "not monitored if cond is verified.")
    config.addinivalue_line("markers", "monitor_test: mark test to be monitored (default behaviour)."
                                       " This can turn handy to whitelist some test when you have disabled"
                                       " monitoring on a whole module.")
    config.addinivalue_line("markers", "monitor_test_if(cond): mark test to be monitored if and only if cond"
                                       " is verified. This can help you in whitelisting tests to be monitored"
                                       " depending on some external conditions.")


def pytest_runtest_setup(item):
    """
    Validate marker setup and print warnings if usage of deprecated marker is identified.
    Setting marker attribute to the discovered item is done after the above described verification.
    :param item: Test item
    """
    item_markers = {mark.name: mark for mark in item.iter_markers() if mark and mark.name.startswith('monitor_')}
    mark_to_del = []
    for set_marker in item_markers.keys():
        if set_marker not in PYTEST_MONITOR_VALID_MARKERS:
            warnings.warn(f"Nothing known about marker {set_marker}. Marker will be dropped.")
            mark_to_del.append(set_marker)
        if set_marker in PYTEST_MONITOR_DEPRECATED_MARKERS:
            warnings.warn(f'Marker {set_marker} is deprecated. Consider upgrading your tests')

    for marker in mark_to_del:
        del item_markers[marker]

    all_valid_markers = PYTEST_MONITOR_VALID_MARKERS
    all_valid_markers.update(PYTEST_MONITOR_DEPRECATED_MARKERS)
    # Setting instantiated markers
    for marker, _ in item_markers.items():
        with_args, attr, fun_val, _ = all_valid_markers[marker]
        attr_val = fun_val(item_markers[marker].args[0]) if with_args else fun_val(None)
        setattr(item, attr, attr_val)

    # Setting other markers to default values
    for marker, marker_value in all_valid_markers.items():
        with_args, attr, _, default = marker_value
        if not hasattr(item, attr):
            setattr(item, attr, default)

    # Finalize marker processing by enforcing some marker's value
    if item.monitor_force_test:
        # This test has been explicitly flagged as 'to be monitored'.
        item.monitor_skip_test = False


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Used to identify the current call to add times.
    :param item: Test item
    :param call: call instance associated to the given item
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == 'call':
        setattr(item, 'test_run_duration', call.stop - call.start)
        setattr(item, 'test_effective_start_time', call.start)


def pytest_runtest_call(item):
    setattr(item, 'monitor_results', False)
    setattr(item, 'monitor_component', getattr(item.module, 'pytest_monitor_component', ''))


def pytest_pyfunc_call(pyfuncitem):
    """
    Core sniffer logic. We encapsulate the test function in a sniffer function to collect
    memory results.
    """
    testfunction = pyfuncitem.obj
    funcargs = pyfuncitem.funcargs
    testargs = {arg: funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}

    def prof():
        m = memory_profiler.memory_usage((testfunction, (), testargs), max_usage=True)
        setattr(pyfuncitem, 'mem_usage', m)
        setattr(pyfuncitem, 'monitor_results', True)
    prof()
    return True


def pytest_make_parametrize_id(config, val, argname):
    if config.option.want_explicit_ids:
        return f'{argname}_{val}'


@pytest.hookimpl(hookwrapper=True)
def pytest_sessionstart(session):
    """
    Instantiate a monitor session to save collected metrics.
    We yield at the end to let pytest pursue the execution.
    """
    global PYTEST_MONITOR_SESSION
    if session.config.option.force_component and session.config.option.component_prefix:
        raise pytest.UsageError('Invalid usage: --force-component and --component-prefix are incompatible options!')
    if session.config.option.no_db and not session.config.option.remote and not session.config.option.mtr_none:
        warnings.warn('pytest-monitor: No storage specified but monitoring is requested. Disabling monitoring.')
        session.config.option.mtr_none = True
    component = session.config.option.force_component or session.config.option.component_prefix 
    if session.config.option.component_prefix:
        component += '.{user_component}'
    if not component:
        component = '{user_component}'
    db = None if (session.config.option.mtr_none or session.config.option.no_db) else session.config.option.mtr_db_out
    remote = None if session.config.option.mtr_none else session.config.option.remote
    PYTEST_MONITOR_SESSION = PyTestMonitorSession(db=db, remote=remote, component=component)
    PYTEST_MONITOR_SESSION.set_environment_info(ExecutionContext())
    yield


def scoper(scope, monitor_skip_flag, set_scope):
    should_skip = monitor_skip_flag
    if scope in set_scope and not should_skip:
        global PYTEST_MONITOR_SESSION
        return PYTEST_MONITOR_SESSION
    return None


@pytest.fixture(autouse=True, scope='module')
def prf_module_tracer(request):
    t_a = time.time()
    yield
    wrt = scoper('module', False, request.config.option.mtr_scope)
    if wrt is not None:
        t_z = time.time()
        process = psutil.Process(os.getpid())
        rss = process.memory_info().rss / 1024 ** 2
        ptimes = process.cpu_times()
        component = getattr(request.module, 'pytest_monitor_component', '')
        wrt.add_test_info(request.module.__name__, 'module', component,
                          t_a, t_z - t_a, ptimes.user, ptimes.system,
                          rss)


@pytest.fixture(autouse=True)
def prf_tracer(request):
    yield
    wrt = scoper('function', request.node.monitor_skip_test, request.config.option.mtr_scope)
    if wrt is not None:
        process = psutil.Process(os.getpid())
        ptimes = process.cpu_times()
        if request.node.monitor_results:
            full_item_name = f'{request.module.__name__}/{request.node.name}'
            wrt.add_test_info(full_item_name, 'function', request.node.monitor_component,
                              request.node.test_effective_start_time,
                              request.node.test_run_duration,
                              ptimes.user, ptimes.system, request.node.mem_usage)
