# -*- coding: utf-8 -*-

import clr
clr.AddReference('DAO')
clr.AddReference('Entities')

from DAO.OKW import DAOokwDataContext
from Entities import OKW

from utils import limpia
from erroresapp import ErrorIdentificadorNoEncontrado

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
        return list(contexto.ExecuteQuery[self.record_type](self.query, folio_paciente))

# end class EntidadInfo


def mkconnstr(host, db='OKW'):
    cstr = 'Data Source=%s;' \
           'Initial Catalog=%s;' \
           'Persist Security Info=True;' \
           'User ID=<USUARIO>;' \
           'Pwd=<PASSWORD>' % (host, db)
    return cstr


_DEFAULT_COMMAND_TIMEOUT = 300


def _get_connection_string(fl_plaza):
    return mkconnstr(_IP_PLAZA[fl_plaza])


def _mkdatactx(class_, connstr):
    dc = class_(connstr)
    dc.CommandTimeout = _DEFAULT_COMMAND_TIMEOUT
    return dc


def contexto_okw(conn_str):
    return _mkdatactx(DAOokwDataContext, conn_str)


_OBTEN_FOLIOS_PACIENTES_SQL = 'SELECT FL_PACIENTE FROM OKW.C_PACIENTE'


def obten_pacientes(contexto):
    return contexto.ExecuteQuery[int](_OBTEN_FOLIOS_PACIENTES_SQL)


_OBTEN_PLAZA_LOCAL_SQL = 'SELECT NO_VALOR FROM OKW.C_CONFIGURACION WHERE CL_CONFIGURACION = 16'


def obten_plaza_local(contexto):
    return list(contexto.ExecuteQuery[str](_OBTEN_PLAZA_LOCAL_SQL))[0]


C_PACIENTE = EntidadInfo(record_type=OKW.C_PACIENTE, query=OkwQueries.C_PACIENTE)

K_PACIENTE_IDENTIFICADOR = EntidadInfo(record_type=OKW.K_PACIENTE_IDENTIFICADOR,
                                        query=OkwQueries.K_PACIENTE_IDENTIFICADOR)


def primero(*args, **kwds):
    try:
        return next(*args, **kwds)
    except StopIteration:
        pass


def _carga_identificadores(contexto, fl_paciente):
    return K_PACIENTE_IDENTIFICADOR.cargaDatos(contexto, fl_paciente)


def carga_paciente(contexto, fl_paciente):
    found = primero(p for p in C_PACIENTE.cargaDatos(contexto, fl_paciente))
    if found:
        found = Paciente(found)
        found.identificadores = _carga_identificadores(contexto, fl_paciente)
    return found

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

    def tiene_menos_ids_que(self, otro_paciente):
        return self.ids != otro_paciente.ids and self.ids.issubset(otro_paciente.ids)

    def ids_que_te_faltan_de(self, otro_paciente):
        folios = otro_paciente.ids - self.ids
        objetos = (otro_paciente.busca_id(fl) for fl in folios)
        return '|'.join('FL_IDENTIFICADOR={0};DS_TEXTO={1}'.format(id.FL_IDENTIFICADOR, id.DS_TEXTO) for id in objetos if id)

#end class Paciente

