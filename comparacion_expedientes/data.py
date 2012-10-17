#!/env/ipy
# -*- coding: utf-8 -*-

import clr
import sys

clr.AddReference('DAO')
from DAO.OKW import DAOokwDataContext
from DAO.SOMATOM import DAOSomatomDataContext

clr.AddReference('System.Configuration')
from System.Configuration import ConfigurationManager

_is_script = False

def _get_is_script(value):
    return _is_script

def _set_is_script(value):
    global _is_script
    _is_script = value

is_script = property(_get_is_script, _set_is_script)

def _mkconnstr(host):
    return 'Data Source=%s;Initial Catalog=OKW;Persist Security Info=True;User ID=super;Pwd=super' % host

_DEFAULT_CONNECTION_STRINGS = {
    'Source' : _mkconnstr('192.168.137.122'),
    'Target' : _mkconnstr('192.168.137.123'),
}

_DEFAULT_COMMAND_TIMEOUT = 300

def _get_connection_string(name):
    arg_pfx = '/%s:' % name.lower()
    found = [a for a in sys.argv if a.lower().startswith(arg_pfx)]
    if found:
        host_name = found[0][len(arg_pfx):]
        return _mkconnstr(host_name)
    elif _is_script:
        return _DEFAULT_CONNECTION_STRINGS[name]
    return str(ConfigurationManager.ConnectionStrings[name])

def _mkdatactx(class_, connstr):
    dc = class_(connstr)
    dc.CommandTimeout = _DEFAULT_COMMAND_TIMEOUT
    return dc

def okw_data_ctx(which):
    conn_str = _get_connection_string(which)
    return _mkdatactx(DAOokwDataContext, conn_str)

def smt_data_ctx(which):
    conn_str = _get_connection_string(which)
    return _mkdatactx(DAOSomatomDataContext, conn_str)

class RecordSource(object):
    def __init__(self, src_context, ref_context, folio_paciente):
        self.src_context = src_context
        self.ref_context = ref_context
        self.folio_paciente = folio_paciente

    def registros(self, entidad):
        src_records = entidad.cargaDatos(self.src_context, self.folio_paciente)
        ref_records = entidad.cargaDatos(self.ref_context, self.folio_paciente)
        return (src_records, ref_records)

    def son_comparables(self, src_records, ref_records):
        return len(src_records) == len(ref_records)

