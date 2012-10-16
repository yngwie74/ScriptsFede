#!/env/ipy
# -*- coding: utf-8 -*-

import clr
import System

clr.AddReference('DAO')
from DAO.OKW import DAOokwDataContext
from DAO.SOMATOM import DAOSomatomDataContext

clr.AddReference('System.Configuration')
from System.Configuration import ConfigurationManager

from sys import argv
from comp import comp

_is_script = (__name__ == '__main__')

_DEFAULT_COMMAND_TIMEOUT = 300

def _mkconnstr(host):
    return 'Data Source=%s;Initial Catalog=OKW;Persist Security Info=True;User ID=super;Pwd=super' % host


_DEFAULT_CONNECTION_STRINGS = {
    'Source' : _mkconnstr('192.168.137.122'),
    'Target' : _mkconnstr('192.168.137.123'),
}


def _to_folios(args):
    return [int(arg) for arg in args if arg.isdigit()]

def _get_folios_paciente():
    return _to_folios(argv)


def _get_connection_string(name):
    arg_pfx = '/%s:' % name.lower()
    found = [a for a in argv if a.lower().startswith(arg_pfx)]
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


_cs_src = _get_connection_string('Source')
_cs_ref = _get_connection_string('Target')

pacientes = _get_folios_paciente()
if not pacientes:
    print 'No se proporcionó ningún folio de paciente. Por favor, digite los folios a comparar: ',
    pacientes = _to_folios(raw_input().split())

for _fl_paciente in pacientes:
    print 'Paciente %d...' % _fl_paciente

    are_equal = True

    with _mkdatactx(DAOokwDataContext, _cs_src) as src_context:
        with _mkdatactx(DAOokwDataContext, _cs_ref) as ref_context:
            are_equal = are_equal and comp(_fl_paciente, 'OKW', src_context, ref_context)

    with _mkdatactx(DAOSomatomDataContext, _cs_src) as src_context:
        with _mkdatactx(DAOSomatomDataContext, _cs_ref) as ref_context:
            are_equal = are_equal and comp(_fl_paciente, 'SOMATOM', src_context, ref_context)

    if are_equal:
        print 'Los expedientes son iguales'
    else:
        print ''

# done!
