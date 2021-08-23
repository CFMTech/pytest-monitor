# -*- coding: utf-8 -*-
import gc
import memory_profiler
import pytest
import time
import warnings

from pytest_monitor.session import PyTestMonitorSession

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
PYTEST_MONITOR_ITEM_LOC_MEMBER = '_location' if tuple(pytest.__version__.split('.')) < ('5', '3') else 'location'

PYTEST_MONITORING_ENABLED = True


def pytest_addoption(parser):
    group = parser.getgroup('monitor')
    group.addoption('--restrict-scope-to', dest='mtr_scope', default='function',
                    help='Select the scope to monitor. By default, only function is monitored.'
                         'Values are function, class, module, session. You can set one or more of these'
                         'by listing them using a comma separated list')
    group.addoption('--parametrization-explicit', dest='mtr_want_explicit_ids', action='store_true',
                    help='Set this option to distinguish parametrized tests given their values.'
                         ' This requires the parameters to be stringifiable.')
    group.addoption('--no-monitor', action='store_true', dest='mtr_none', help='Disable all traces')
    group.addoption('--remote-server', action='store', dest='mtr_remote',
                    help='Remote server to send the results to. Format is <ADRESS>:<PORT>')
    group.addoption('--db', action='store', dest='mtr_db_out', default='.pymon',
                    help='Use the given sqlite database for storing results.')
    group.addoption('--no-db', action='store_true', dest='mtr_no_db', help='Do not store results in local db.')
    group.addoption('--force-component', action='store', dest='mtr_force_component',
                    help='Force the component to be set at the given value for the all tests run'
                         ' in this session.')
    group.addoption('--component-prefix', action='store', dest='mtr_component_prefix',
                    help='Prefix each found components with the given value (applies to all tests'
                         ' run in this session).')
    group.addoption('--no-gc', action="store_true", dest="mtr_no_gc", 
                    help='Disable garbage collection between tests (may leads to non reliable measures)')
    group.addoption('--description', action='store', default='', dest='mtr_description',
                    help='Use this option to provide a small summary about this run.')
    group.addoption('--tag', action='append', dest='mtr_tags', default=[],
                    help='Provide meaningfull flags to your run. This can help you in your analysis.')


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
    if not PYTEST_MONITORING_ENABLED:
        return
    item_markers = {mark.name: mark for mark in item.iter_markers() if mark and mark.name.startswith('monitor_')}
    mark_to_del = []
    for set_marker in item_markers.keys():
        if set_marker not in PYTEST_MONITOR_VALID_MARKERS:
            warnings.warn("Nothing known about marker {}. Marker will be dropped.".format(set_marker))
            mark_to_del.append(set_marker)
        if set_marker in PYTEST_MONITOR_DEPRECATED_MARKERS:
            warnings.warn('Marker {} is deprecated. Consider upgrading your tests'.format(set_marker))

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
    if not PYTEST_MONITORING_ENABLED:
        return
    setattr(item, 'monitor_results', False)
    if hasattr(item, 'module'):
        setattr(item, 'monitor_component', getattr(item.module, 'pytest_monitor_component', ''))
    else:
        setattr(item, 'monitor_skip_test', True)


@pytest.hookimpl
def pytest_pyfunc_call(pyfuncitem):
    """
    Core sniffer logic. We encapsulate the test function in a sniffer function to collect
    memory results.
    """
    def wrapped_function():
        try:
            funcargs = pyfuncitem.funcargs
            testargs = {arg: funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}
            pyfuncitem.obj(**testargs)
        except Exception:
            raise
        except BaseException as e:
            return e

    def prof():
        m = memory_profiler.memory_usage((wrapped_function, ()),
                                         max_iterations=1, max_usage=True, retval=True)
        if isinstance(m[1], BaseException):  # Do we have any outcome?
            raise m[1]
        memuse = m[0][0] if type(m[0]) is list else m[0]
        setattr(pyfuncitem, 'mem_usage', memuse)
        setattr(pyfuncitem, 'monitor_results', True)
    if not PYTEST_MONITORING_ENABLED:
        wrapped_function()
    else:
        if pyfuncitem.session.config.option.mtr_no_gc:
            gc.collect()
        prof()
    return True


def pytest_make_parametrize_id(config, val, argname):
    if config.option.mtr_want_explicit_ids:
        return '{}={}'.format(argname, val)


@pytest.hookimpl(hookwrapper=True)
def pytest_sessionstart(session):
    """
    Instantiate a monitor session to save collected metrics.
    We yield at the end to let pytest pursue the execution.
    """
    if session.config.option.mtr_force_component and session.config.option.mtr_component_prefix:
        raise pytest.UsageError('Invalid usage: --force-component and --component-prefix are incompatible options!')
    if session.config.option.mtr_no_db and not session.config.option.mtr_remote and not session.config.option.mtr_none:
        warnings.warn('pytest-monitor: No storage specified but monitoring is requested. Disabling monitoring.')
        session.config.option.mtr_none = True
    component = session.config.option.mtr_force_component or session.config.option.mtr_component_prefix
    if session.config.option.mtr_component_prefix:
        component += '.{user_component}'
    if not component:
        component = '{user_component}'
    db = None if (session.config.option.mtr_none or session.config.option.mtr_no_db) else session.config.option.mtr_db_out
    remote = None if session.config.option.mtr_none else session.config.option.mtr_remote
    session.pytest_monitor = PyTestMonitorSession(db=db, remote=remote,
                                                  component=component,
                                                  scope=session.config.option.mtr_scope)
    global PYTEST_MONITORING_ENABLED
    PYTEST_MONITORING_ENABLED = not session.config.option.mtr_none
    session.pytest_monitor.compute_info(session.config.option.mtr_description,
                                        session.config.option.mtr_tags)
    yield


@pytest.fixture(autouse=True, scope='module')
def prf_module_tracer(request):
    if not PYTEST_MONITORING_ENABLED:
        yield
    else:
        t_a = time.time()
        ptimes_a = request.session.pytest_monitor.process.cpu_times()
        yield
        ptimes_b = request.session.pytest_monitor.process.cpu_times()
        t_z = time.time()
        rss = request.session.pytest_monitor.process.memory_info().rss / 1024 ** 2
        component = getattr(request.module, 'pytest_monitor_component', '')
        item = request.node.name[:-3]
        pypath = request.module.__name__[:-len(item)-1]
        request.session.pytest_monitor.add_test_info(item, pypath, '',
                                                     request.node._nodeid,
                                                     'module',
                                                     component, t_a, t_z - t_a,
                                                     ptimes_b.user - ptimes_a.user,
                                                     ptimes_b.system - ptimes_a.system,
                                                     rss)


@pytest.fixture(autouse=True)
def prf_tracer(request):
    if not PYTEST_MONITORING_ENABLED:
        yield
    else:
        ptimes_a = request.session.pytest_monitor.process.cpu_times()
        yield
        ptimes_b = request.session.pytest_monitor.process.cpu_times()
        if not request.node.monitor_skip_test and request.node.monitor_results:
            item_name = request.node.originalname or request.node.name
            item_loc = getattr(request.node, PYTEST_MONITOR_ITEM_LOC_MEMBER)[0]
            request.session.pytest_monitor.add_test_info(item_name, request.module.__name__,
                                                         request.node.name, item_loc,
                                                         'function',
                                                         request.node.monitor_component,
                                                         request.node.test_effective_start_time,
                                                         request.node.test_run_duration,
                                                         ptimes_b.user - ptimes_a.user,
                                                         ptimes_b.system - ptimes_a.system,
                                                         request.node.mem_usage)
