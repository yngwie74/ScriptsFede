# -*- coding: utf-8 -*-

import clr
clr.AddReference('DAO')
clr.AddReference('Entities')

from DAO.OKW import DAOokwDataContext
from Entities import OKW

from utils import limpia, primero


class OkwQueries:

    C_PACIENTE = 'select * from OKW.C_PACIENTE where FL_PACIENTE = {0} order by FL_PACIENTE'
    K_PACIENTE_IDENTIFICADOR = \
        'select * from OKW.K_PACIENTE_IDENTIFICADOR where FL_PACIENTE = {0} order by FL_IDENTIFICADOR'

#end class OkwQueries


class EntidadInfo(object):

    def __init__(self, record_type, query):
        self.record_type = record_type
        self.query = query

    @property
    def type_name(self):
        return self.record_type.__name__

    def cargaDatos(self, contexto, folio_paciente):
        return contexto.ExecuteQuery[self.record_type](self.query, folio_paciente)

# end class EntidadInfo

_DEFAULT_COMMAND_TIMEOUT = 300
_DEFAULT_CONNECTION_TIMEOUT = 60


def mkconnstr(host, db='OKW'):
    cstr = 'Data Source=%s;' \
           'Initial Catalog=%s;' \
           'Persist Security Info=True;' \
           'Connect Timeout=%d;' \
           'User ID=<USUARIO>;' \
           'Pwd=<PASSWORD>' \
           % (host, db, _DEFAULT_CONNECTION_TIMEOUT)
    return cstr


def _get_connection_string(fl_plaza):
    return mkconnstr(_IP_PLAZA[fl_plaza])


def _mkdatactx(class_, connstr):
    dc = class_(connstr)
    dc.CommandTimeout = _DEFAULT_COMMAND_TIMEOUT
    dc.ObjectTrackingEnabled = False
    return dc


def contexto_okw(conn_str):
    return _mkdatactx(DAOokwDataContext, conn_str)


_OBTEN_FOLIOS_PACIENTES_SQL = 'SELECT FL_PACIENTE FROM OKW.C_PACIENTE'


def obten_pacientes(contexto):
    return contexto.ExecuteQuery[int](_OBTEN_FOLIOS_PACIENTES_SQL)


_OBTEN_PLAZA_LOCAL_SQL = 'SELECT NO_VALOR FROM OKW.C_CONFIGURACION WHERE CL_CONFIGURACION = 16'


def obten_plaza_local(contexto):
    return primero(contexto.ExecuteQuery[str](_OBTEN_PLAZA_LOCAL_SQL))


C_PACIENTE = EntidadInfo(record_type=OKW.C_PACIENTE, query=OkwQueries.C_PACIENTE)

K_PACIENTE_IDENTIFICADOR = EntidadInfo(record_type=OKW.K_PACIENTE_IDENTIFICADOR,
                                       query=OkwQueries.K_PACIENTE_IDENTIFICADOR)


def _carga_identificadores(contexto, fl_paciente):
    return K_PACIENTE_IDENTIFICADOR.cargaDatos(contexto, fl_paciente)


def carga_paciente(contexto, fl_paciente):
    found = primero(C_PACIENTE.cargaDatos(contexto, fl_paciente))
    if found:
        found = Paciente(found)
        found.identificadores = list(_carga_identificadores(contexto, fl_paciente))
    return found


def _diff_idents(paciente_origen, paciente_destino):
    folios = paciente_origen.ids.difference(paciente_destino.ids)
    return (paciente_origen._ids_por_folios(folios) if len(folios) else [])


class Paciente(object):

    def __init__(self, paciente):
        self.paciente = paciente
        self.identificadores = []

    def __getattr__(self, name):
        return getattr(self.paciente, name)

    def busca_id(self, fl_identificador):
        return primero(id for id in self.identificadores
                       if id.FL_IDENTIFICADOR == fl_identificador)

    @property
    def nombre_comp(self):
        return ' '.join(limpia(s) for s in [self.NB_PACIENTE, self.NB_PATERNO, self.NB_MATERNO])

    @property
    def ids(self):
        return frozenset(i.FL_IDENTIFICADOR for i in self.identificadores)

    def _ids_por_folios(self, folios):
        idents = (self.busca_id(fl) for fl in folios)
        return (id for id in idents if id)

    def ids_comunes(self, otro_paciente):
        folios = self.ids.intersection(otro_paciente.ids)
        return self._ids_por_folios(folios)

    def ids_que_le_faltan_a(self, otro_paciente):
        return _diff_idents(self, otro_paciente)

    def ids_que_te_faltan_de(self, otro_paciente):
        return _diff_idents(otro_paciente, self)

#end class Paciente

