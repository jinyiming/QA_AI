from __future__ import absolute_import

from .base import DMCompiler, DMDialect, DMExecutionContext
from . import base as dm
import sqlalchemy.engine.result as _result
from sqlalchemy import types as sqltypes, util, exc
from sqlalchemy import util
import random
import collections
import decimal
import re
import time
import datetime as dt
from .types import _DMBinary, _DMBoolean, _DMChar, _DMDate, _DMEnum, \
     _DMInteger, _DMInterval, _DMLongVarBinary, _DMLongVarchar, _DMNumeric, \
     _DMNVarChar, _DMRowid, _DMString, _DMText, _DMUnicodeText, INTERVAL, \
     LONGVARCHAR, ROWID, _DMBLOB, DMBINARY

class DMCompiler_dmPython(DMCompiler):
    def bindparam_string(self, name, **kw):
        self.dialect.trace_process('DMCompiler_dmPython', 'bindparam_string', name, **kw)
        
        quote = getattr(name, 'quote', None)
        if quote is True or quote is not False and \
                self.preparer._bindparam_requires_quotes(name):
            quoted_name = '"%s"' % name
            self._quoted_bind_names[name] = quoted_name
            return DMCompiler.bindparam_string(self, quoted_name, **kw)
        else:
            return DMCompiler.bindparam_string(self, name, **kw)
    
    '''
    def construct_params(self, params=None, _group_number=None, _check=True):
        self.dialect.trace_process('DMCompiler_dmPython', 'construct_params', params, _group_number, _check)
        """return a dictionary of bind parameter keys and values"""

        if params:
            pd = {}
            for bindparam in self.bind_names:
                name = self.bind_names[bindparam]
                
                # reserved word process
                if self.preparer._bindparam_requires_quotes(name):
                    name = self.preparer.quote(name)
                
                if bindparam.key in params:
                    pd[name] = params[bindparam.key]
                elif name in params:
                    pd[name] = params[name]

                elif _check and bindparam.required:
                    if _group_number:
                        raise exc.InvalidRequestError(
                            "A value is required for bind parameter %r, "
                            "in parameter group %d" %
                            (bindparam.key, _group_number))
                    else:
                        raise exc.InvalidRequestError(
                            "A value is required for bind parameter %r"
                            % bindparam.key)

                elif bindparam.callable:
                    pd[name] = bindparam.effective_value
                else:
                    pd[name] = bindparam.value
            return pd
        else:
            pd = {}
            for bindparam in self.bind_names:
                if _check and bindparam.required:
                    if _group_number:
                        raise exc.InvalidRequestError(
                            "A value is required for bind parameter %r, "
                            "in parameter group %d" %
                            (bindparam.key, _group_number))
                    else:
                        raise exc.InvalidRequestError(
                            "A value is required for bind parameter %r"
                            % bindparam.key)

                if bindparam.callable:
                    pd[self.bind_names[bindparam]] = bindparam.effective_value
                else:
                    pd[self.bind_names[bindparam]] = bindparam.value
            return pd
    '''
    
class DMExecutionContext_dmPython(DMExecutionContext):

    
    def pre_exec(self):
        self.dialect.trace_process('DMExecutionContext_dmPython', 'pre_exec')
        
        if not getattr(self.compiled, "_dm_sql_compiler", False):
            return

        self.out_parameters = {}

        self.include_set_input_sizes = self.dialect._include_setinputsizes

    def create_cursor(self):
        self.dialect.trace_process('DMExecutionContext_dmPython', 'create_cursor')
        
        c = self._dbapi_connection.cursor()
        if self.dialect.arraysize:
            c.arraysize = self.dialect.arraysize

        return c

'''
    def get_result_proxy(self):
        self.dialect.trace_process('DMExecutionContext_dmPython', 'get_result_proxy')
        
        if hasattr(self, 'out_parameters') and self.compiled.returning:
            returning_params = dict(
                (k, v.getvalue())
                for k, v in self.out_parameters.items()
            )
            return ReturningResultProxy(self, returning_params)

        result = None
        if self.cursor.description is not None:
            for column in self.cursor.description:
                type_code = column[1]
                if type_code in self.dialect._dmPython_binary_types:
                    result = _result.BufferedColumnResultProxy(self)

        if result is None:
            result = _result.ResultProxy(self)

        if hasattr(self, 'out_parameters'):
            if self.compiled_parameters is not None and \
                    len(self.compiled_parameters) == 1:
                result.out_parameters = out_parameters = {}

                for bind, name in self.compiled.bind_names.items():
                    if name in self.out_parameters:
                        type = bind.type
                        impl_type = type.dialect_impl(self.dialect)
                        dbapi_type = impl_type.get_dbapi_type(
                            self.dialect.dbapi)
                        result_processor = impl_type.\
                            result_processor(self.dialect,
                                             dbapi_type)
                        if result_processor is not None:
                            out_parameters[name] = \
                                result_processor(
                                    self.out_parameters[name].getvalue())
                        else:
                            out_parameters[name] = self.out_parameters[
                                name].getvalue()
            else:
                result.out_parameters = dict(
                                            (k, v.getvalue())
                    for k, v in self.out_parameters.items()
                )

        return result
'''

'''
class ReturningResultProxy(_result.FullyBufferedResultProxy):
    """Result proxy which stuffs the _returning clause + outparams
    into the fetch."""

    def __init__(self, context, returning_params):
        self._returning_params = returning_params
        super(ReturningResultProxy, self).__init__(context)

    def _cursor_description(self):
        self.dialect.trace_process('ReturningResultProxy', '_cursor_description')
        
        returning = self.context.compiled.returning
        return [
            ("ret_%d" % i, None)
            for i, col in enumerate(returning)
        ]

    def _buffer_rows(self):
        self.dialect.trace_process('ReturningResultProxy', '_buffer_rows')
        
        return collections.deque(
            [tuple(self._returning_params["ret_%d" % i]
                   for i, c in enumerate(self._returning_params))]
        )
'''

class DMDialect_dmPython(DMDialect):
    supports_statement_cache = True
    execution_ctx_cls = DMExecutionContext_dmPython
    statement_compiler = DMCompiler_dmPython
    
    supports_sane_rowcount = True
    supports_sane_multi_rowcount = False

    supports_unicode_statements = True
    supports_unicode_binds = True

    driver = "dmPython"

    colspecs = colspecs = {
        sqltypes.Numeric: _DMNumeric,
        # generic type, assume datetime.date is desired
        sqltypes.Date: _DMDate,
        #sqltypes.LargeBinary: _DMBinary,
        sqltypes._Binary: _DMBinary,
        #sqltypes._Binary: _DMBLOB,
        sqltypes.Boolean: _DMBoolean,
        sqltypes.BOOLEAN: _DMBoolean,
        sqltypes.Interval: _DMInterval,
        INTERVAL: _DMInterval,
        sqltypes.Text: _DMText,
        sqltypes.TEXT: _DMText,
        sqltypes.BLOB: _DMBLOB,
        #sqltypes.BLOB: _DMBinary,
        sqltypes.String: _DMString,
        sqltypes.UnicodeText: _DMUnicodeText,
        sqltypes.CHAR: _DMChar,
        sqltypes.Enum: _DMEnum,
        sqltypes.BINARY: DMBINARY,

        LONGVARCHAR: _DMLongVarchar,

        # this is only needed for OUT parameters.
        # it would be nice if we could not use it otherwise.
        sqltypes.Integer: _DMInteger,
        sqltypes.INTEGER: _DMInteger,

        sqltypes.Unicode: _DMNVarChar,
        sqltypes.NVARCHAR: _DMNVarChar,
        ROWID: _DMRowid,
    }

    execute_sequence_format = list

    def __init__(self,
                 #auto_setinputsizes=False,
                 #exclude_setinputsizes=("STRING", "UNICODE"),
                 auto_convert_lobs=True,
                 #threaded=True,
                 #allow_twophase=True,
                 coerce_to_decimal=True,
                 #coerce_to_unicode=False,
                 autocommit = False,
                 connection_timeout = 30,
                 arraysize=50,# _retry_on_12516=False,
                 **kwargs):
        DMDialect.__init__(self, **kwargs)
        #self.threaded = threaded
        self.arraysize = arraysize
        #self.allow_twophase = allow_twophase
        #self.supports_timestamp = self.dbapi is None or \
        #    hasattr(self.dbapi, 'TIMESTAMP')
        #self.auto_setinputsizes = auto_setinputsizes
        self.auto_convert_lobs = auto_convert_lobs
        #self._retry_on_12516 = _retry_on_12516
        self.autocommit = False
        self.connection_timeout = connection_timeout

        if hasattr(self.dbapi, 'version'):
            self.dmPython_ver = self._parse_dmPython_ver(self.dbapi.version)

        else:
            self.dmPython_ver = (0, 0)

        def types(*names):
            return set(
                getattr(self.dbapi, name, None) for name in names
            ).difference([None])

        #self.exclude_setinputsizes = types(*(exclude_setinputsizes or ()))
        self._dmPython_string_types = types("STRING", "UNICODE",
                                             "NCLOB", "CLOB")
        self._dmPython_unicode_types = types("UNICODE", "NCLOB")
        self._dmPython_binary_types = types("BFILE", "CLOB", "NCLOB", "BLOB")
        
        self.supports_native_decimal = coerce_to_decimal

        if self.dmPython_ver is None or \
           not self.auto_convert_lobs or \
           not hasattr(self.dbapi, 'CLOB'):
            self.dbapi_type_map = {}
        else:
            self.dbapi_type_map = {
                self.dbapi.CLOB: dm.CLOB(),
                #self.dbapi.NCLOB: dm.NCLOB(),
                self.dbapi.BLOB: dm.BLOB(),
            }        

    def _parse_dmPython_ver(self, version):
        m = re.match(r'(\d+)\.(\d+)(?:\.(\d+))?', version)
        if m:
            return tuple(
                int(x)
                for x in m.group(1, 2, 3)
                if x is not None)
        else:
            return (0, 0)

    @classmethod
    def import_dbapi(cls):
        import dmPython
        return dmPython

    def connect(self, *cargs, **cparams):
        self.trace_process('DMDialect_dmPython', 'connect', *cargs, **cparams)
        
        try:
            conn = self.dbapi.connect(*cargs, **cparams)
            
            self.encoding = self.get_conn_local_code(conn)
            
            self.case_sensitive = conn.str_case_sensitive
            if self.case_sensitive:
                self.requires_name_normalize = True
            else:
                self.requires_name_normalize = False
                        
            cursor = conn.cursor();
            cursor.execute('SET_SESSION_IDENTITY_CHECK(1);')
            return conn
        except self.dbapi.DatabaseError as err:
            raise
        
    def get_conn_local_code(self, conn):
        self.trace_process('DMDialect_dmPython', 'get_conn_local_code', conn)
        
        if conn.local_code == 1:
            return 'utf-8'
        elif conn.local_code == 2:
            return 'gbk'
        elif conn.local_code == 3:
            return 'big5'
        elif conn.local_code == 4:
            return 'iso_8859_9'
        elif conn.local_code == 5:
            return 'euc_jp'
        elif conn.local_code == 6:
            return 'euc_kr'
        elif conn.local_code == 8:
            return 'iso_8859_1'
        elif conn.local_code == 9:
            return 'ascii'
        elif conn.local_code == 10:
            return 'gb18030'
        elif conn.local_code == 11:
            return 'iso_8859_11'
    
    def initialize(self, connection):
        self.trace_process('DMDialect_dmPython', 'initialize', connection)
        super(DMDialect_dmPython, self).initialize(connection)
        self._detect_decimal_char(connection)

    def _detect_decimal_char(self, connection):
        self.trace_process('DMDialect_dmPython', '_detect_decimal_char', connection)
        return

    def _detect_decimal(self, value):
        self.trace_process('DMDialect_dmPython', '_detect_decimal', value)
        
        if "." in value:
            return decimal.Decimal(value)
        else:
            return int(value)

    _to_decimal = decimal.Decimal

    def on_connect(self):
        self.trace_process('DMDialect_dmPython', 'on_connect')
        return
        
    def create_connect_args(self, url):
        self.trace_process('DMDialect_dmPython', 'create_connect_args', url)
        
        opts = url.translate_connect_args(username='user')

        opts.update(url.query)
        
        util.coerce_kw_type(opts, 'access_mode', int) 
        util.coerce_kw_type(opts, 'autoCommit', bool)
        util.coerce_kw_type(opts, 'connection_timeout', int) 
        util.coerce_kw_type(opts, 'login_timeout', int)
        util.coerce_kw_type(opts, 'txn_isolation', int)
        util.coerce_kw_type(opts, 'compress_msg', bool)
        util.coerce_kw_type(opts, 'use_stmt_pool', bool)
        util.coerce_kw_type(opts, 'ssl_path', str)
        util.coerce_kw_type(opts, 'mpp_login', bool)
        util.coerce_kw_type(opts, 'rwseparate', bool)
        util.coerce_kw_type(opts, 'rwseparate_percent', int)
        util.coerce_kw_type(opts, 'lang_id', int)
        util.coerce_kw_type(opts, 'local_code', int)
        
        opts.setdefault('autoCommit', self.autocommit)
        opts.setdefault('connection_timeout', self.connection_timeout)
        opts.setdefault('host', 'localhost')
        opts.setdefault('port', 5236)
        
        dsn = opts['host'] + ':%d' %opts['port']

        if dsn is not None:
            opts['dsn'] = dsn
        
        return ([], opts)

    def _get_server_version_info(self, connection):
        self.trace_process('DMDialect_dmPython', '_get_server_version_info', connection)
        
        dbapi_con = connection.connection
        version = []
        r = re.compile(r'[.\-]')
        for n in r.split(dbapi_con.server_version):
            try:
                version.append(int(n))
            except ValueError:
                version.append(n)
        return tuple(version)

    def is_disconnect(self, e, connection, cursor):
        self.trace_process('DMDialect_dmPython', 'is_disconnect', e, connection, cursor)
        
        error, = e.args
        if isinstance(e, self.dbapi.InterfaceError):
            return "not connected" in str(e)
        elif hasattr(error, 'code'):
            return error.code in (-70025, -70028, -6010, -70019)
        else:
            return False

    def create_xid(self):
        self.trace_process('DMDialect_dmPython', 'create_xid')
        
        """create a two-phase transaction ID.

        this id will be passed to do_begin_twophase(), do_rollback_twophase(),
        do_commit_twophase().  its format is unspecified."""

        id = random.randint(0, 2 ** 128)
        return (0x1234, "%032x" % id, "%032x" % 9)

    def do_executemany(self, cursor, statement, parameters, context=None):
        self.trace_process('DMDialect_dmPython', 'do_executemany', cursor, statement, parameters, context)
        
        if isinstance(parameters, tuple):
            parameters = list(parameters)
        cursor.executemany(statement, parameters)

    def do_rollback_twophase(self, connection, xid, is_prepared=True,
                             recover=False):
        self.trace_process('DMDialect_dmPython', 'do_rollback_twophase', connection, xid, is_prepared, recover)
        
        self.do_rollback(connection.connection)

    def do_commit_twophase(self, connection, xid, is_prepared=True,
                           recover=False):
        self.trace_process('DMDialect_dmPython', 'do_commit_twophase', connection, xid, is_prepared, recover)
        
        self.do_commit(connection.connection)

dialect = DMDialect_dmPython