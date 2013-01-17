#!/bin/env ipy
# -*- coding: utf-8 -*-

import clr
import sys

clr.AddReference('DAO')
from DAO.OKW import DAOokwDataContext
from DAO.SOMATOM import DAOSomatomDataContext

clr.AddReference('System.Configuration')
from System.Configuration import ConfigurationManager

def _mkconnstr(host):
    return 'Data Source=%s;Initial Catalog=OKW;Persist Security Info=True;User ID=super;Pwd=super' % host

_DEFAULT_CONNECTION_STRINGS = {
    'Source' : _mkconnstr('192.168.137.122'),
    'Target' : _mkconnstr('192.168.137.123'),
}

_DEFAULT_COMMAND_TIMEOUT = 300

def _get_connection_string(name):
    arg_pfx = '-%s:' % name.lower()
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

    def carga_registros(self, entidad):
        self.src_records = entidad.cargaDatos(self.src_context, self.folio_paciente)
        self.ref_records = entidad.cargaDatos(self.ref_context, self.folio_paciente)
        return (self.src_records, self.ref_records)

    def _get_keys(self, entity, regs):
        return frozenset(entity.obten_llave(r) for r in regs)

    def _find_rec_by_key(self, entity, regs, key):
        try:
            return next(r for r in regs if entity.obten_llave(r) == key)
        except StopIteration:
            pass

    def _get_all_by_keys(self, entity, regs, keys):
        return [self._find_rec_by_key(entity, regs, k) for k in keys]

    def registros_comunes(self, entity):
        src_keys = self._get_keys(entity, self.src_records)
        ref_keys = self._get_keys(entity, self.ref_records)
        comunes = src_keys.intersection(ref_keys)

        src_records = self._get_all_by_keys(entity, self.src_records, comunes)
        ref_records = self._get_all_by_keys(entity, self.ref_records, comunes)

        return (src_records, ref_records)

    def _get_diff(self, desc, entity, a, b):
        a_keys = self._get_keys(entity, a)
        b_keys = self._get_keys(entity, b)
        diff = a_keys.difference(b_keys)
        if len(diff) == 1:
            lista_llaves = ''.join(str(k) for k in diff)
            return '\n\t1 registro solo existe en la unidad de %s, con %s = %s' % (desc, entity.pk, lista_llaves)
        elif len(diff) > 1:
            lista_llaves = ', '.join(str(k) for k in diff)
            return '\n\t%d registros solo existen en la unidad de %s, con %s in (%s)' % (len(diff), desc, entity.pk, lista_llaves)

    def solo_origen(self, entity):
        return self._get_diff('origen', entity, self.src_records, self.ref_records)

    def solo_referencia(self, entity):
        return self._get_diff('referencia', entity, self.ref_records, self.src_records)

    @property
    def tiene_datos(self):
        return (len(self.src_records) + len(self.ref_records)) > 0

    @property
    def source_name(self):
        return self.src_context.Connection.DataSource
# end class
