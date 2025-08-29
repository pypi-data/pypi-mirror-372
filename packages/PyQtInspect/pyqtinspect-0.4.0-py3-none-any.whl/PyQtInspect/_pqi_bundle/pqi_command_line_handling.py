# -*- encoding:utf-8 -*-
# ==============================================
# Author: Jeza Chen
# Time: 2023/8/18 15:00
# Description: 
# ==============================================
from PyQtInspect._pqi_common.pqi_setup_holder import SetupHolder


class ArgHandlerWithParam:
    '''
    Handler for some arguments which needs a value
    '''

    def __init__(self, arg_name, convert_val=None, default_val=None):
        self.arg_name = arg_name
        self.arg_v_rep = '--%s' % (arg_name,)
        self.convert_val = convert_val
        self.default_val = default_val

    def to_argv(self, lst, setup):
        v = setup.get(self.arg_name)
        if v is not None and v != self.default_val:
            lst.append(self.arg_v_rep)
            lst.append('%s' % (v,))

    def handle_argv(self, argv, i, setup):
        assert argv[i] == self.arg_v_rep
        del argv[i]

        val = argv[i]
        if self.convert_val:
            val = self.convert_val(val)

        setup[self.arg_name] = val
        del argv[i]


# to_argv输出带等号的,"--arg_name=arg_value"
class ArgHandlerWithParamAndEqualSign(ArgHandlerWithParam):
    def to_argv(self, lst, setup):
        v = setup.get(self.arg_name)
        if v is not None and v != self.default_val:
            lst.append('%s=%s' % (self.arg_v_rep, v))


class ArgHandlerBool:
    '''
    If a given flag is received, mark it as 'True' in setup.
    '''

    def __init__(self, arg_name, default_val=False):
        self.arg_name = arg_name
        self.arg_v_rep = '--%s' % (arg_name,)
        self.default_val = default_val

    def to_argv(self, lst, setup):
        v = setup.get(self.arg_name)
        if v:
            lst.append(self.arg_v_rep)

    def handle_argv(self, argv, i, setup):
        assert argv[i] == self.arg_v_rep
        del argv[i]
        setup[self.arg_name] = True


ACCEPTED_ARG_HANDLERS = [
    ArgHandlerWithParam('port', int, 19394),
    ArgHandlerWithParam('client', default_val='127.0.0.1'),
    ArgHandlerWithParam('stack-max-depth', int, 0),

    ArgHandlerBool('server'),
    ArgHandlerBool('direct'),
    ArgHandlerBool('DEBUG_RECORD_SOCKET_READS'),
    ArgHandlerBool('multiprocess'),  # Used by PyDev (creates new connection to ide)
    ArgHandlerBool('module'),
    ArgHandlerBool('help'),
    ArgHandlerBool('show-pqi-stack'),
    ArgHandlerWithParamAndEqualSign('qt-support', default_val='pyqt5'),  # 原来的pydevd不支持子进程带qt参数, 这里加一下
]

ARGV_REP_TO_HANDLER = {}
for handler in ACCEPTED_ARG_HANDLERS:
    ARGV_REP_TO_HANDLER[handler.arg_v_rep] = handler


def get_pydevd_file(executable_path):
    import PyQtInspect.pqi

    f = PyQtInspect.pqi.__file__
    if f.endswith('.pyc'):
        f = f[:-1]
    elif f.endswith('$py.class'):
        f = f[:-len('$py.class')] + '.py'

    return f


def setup_to_argv(executable_path, setup):
    '''
    :param dict setup:
        A dict previously gotten from process_command_line.

    :note: does not handle --file nor --DEBUG.
    '''

    filtered = {
        # Bug fixed 20250302
        # We don't pass this parameter to the subprocess, otherwise, when a new process is created,
        #   it'd try to launch a new debugger, which is not what we want.
        'direct',
    }

    ret = [get_pydevd_file(executable_path)]

    for handler in ACCEPTED_ARG_HANDLERS:
        if handler.arg_name in setup and handler.arg_name not in filtered:
            handler.to_argv(ret, setup)
    return ret


def process_command_line(argv):
    """ parses the arguments.
        removes our arguments from the command line """
    setup = {}
    for handler in ACCEPTED_ARG_HANDLERS:
        setup[handler.arg_name] = handler.default_val
    setup[SetupHolder.KEY_FILE] = ''
    setup[SetupHolder.KEY_SHOW_PQI_STACK] = False

    i = 0
    del argv[0]
    while i < len(argv):
        handler = ARGV_REP_TO_HANDLER.get(argv[i])
        if handler is not None:
            handler.handle_argv(argv, i, setup)

        elif argv[i].startswith('--qt-support'):
            # The --qt-support is special because we want to keep backward compatibility:
            # Previously, just passing '--qt-support' meant that we should use the auto-discovery mode
            # whereas now, if --qt-support is passed, it should be passed as --qt-support=<mode>, where
            # mode can be one of 'auto', 'none', 'pyqt5', 'pyqt4', 'pyside', 'pyside2'.
            if argv[i] == '--qt-support':
                setup[SetupHolder.KEY_QT_SUPPORT] = 'auto'

            elif argv[i].startswith('--qt-support='):
                qt_support = argv[i][len('--qt-support='):]
                qt_support = qt_support.lower()
                valid_modes = ('pyqt5', 'pyqt6', 'pyside2', 'pyside6')  # TODO ONLY SUPPORTS PYQT5/6 AND PYSIDE2/6
                if qt_support not in valid_modes:
                    raise ValueError("qt-support mode invalid: " + qt_support)
                if qt_support == 'none':
                    # On none, actually set an empty string to evaluate to False.
                    setup[SetupHolder.KEY_QT_SUPPORT] = ''
                else:
                    setup[SetupHolder.KEY_QT_SUPPORT] = qt_support
            else:
                raise ValueError("Unexpected definition for qt-support flag: " + argv[i])

            del argv[i]

        elif argv[i] == '--file':
            # --file is special because it's the last one (so, no handler for it).
            del argv[i]
            setup[SetupHolder.KEY_FILE] = argv[i]
            i = len(argv)  # pop out, file is our last argument

        elif argv[i] == '--DEBUG':
            from PyQtInspect.pqi import set_debug
            del argv[i]
            set_debug(setup)

        else:
            raise ValueError("Unexpected option: " + argv[i])
    return setup
