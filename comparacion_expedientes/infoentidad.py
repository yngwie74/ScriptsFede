#!/env/ipy
# -*- coding: utf-8 -*-

import clr

clr.AddReference('Entities')
from Entities import OKW, SOMATOM

class OkwQueries:
    C_PACIENTE = 'select * from OKW.C_PACIENTE where FL_PACIENTE = {0} order by FL_PACIENTE'
    K_EXPEDIENTE = 'select * from OKW.K_EXPEDIENTE where FL_PACIENTE = {0} order by FL_EXPEDIENTE'
    K_PACIENTE_IDENTIFICADOR = 'select * from OKW.K_PACIENTE_IDENTIFICADOR where FL_PACIENTE = {0} order by FL_IDENTIFICADOR'
    K_ALERGIA_PACIENTE = 'select * from OKW.K_ALERGIA_PACIENTE where FL_PACIENTE = {0} order by FL_ALERGIA_PACIENTE'
    K_ANTECEDENTESGO = 'select * from OKW.K_ANTECEDENTESGO where FL_PACIENTE = {0} order by FL_ANTECEDENTESGO'
    K_ANTECEDENTESHF = 'select * from OKW.K_ANTECEDENTESHF where FL_PACIENTE = {0} order by FL_ANTECEDENTEHF'
    K_ANTECEDENTESNP = 'select * from OKW.K_ANTECEDENTESNP where FL_PACIENTE = {0} order by ID_ANTECEDENTESNP'
    K_ANTECEDENTESPP = 'select * from OKW.K_ANTECEDENTESPP where FL_PACIENTE = {0} order by FL_ANTECEDENTEPP'
    K_ANTECEDENTES_ESTRABOLOGICO = 'select * from OKW.K_ANTECEDENTES_ESTRABOLOGICOS where FL_PACIENTE = {0} order by FL_ANTECEDENTES_ESTRABOLOGICOS'
    K_ANTECEDENTES_PERINATALE = 'select * from OKW.K_ANTECEDENTES_PERINATALES where FL_PACIENTE = {0} order by FL_ANTECEDENTES_PERINATALES'
    K_DIAGNOSTICO_PACIENTE = 'select * from OKW.K_DIAGNOSTICO_PACIENTE where FL_PACIENTE = {0} order by FL_DIAGNOSTICO_PACIENTE'
    K_BITACORA_DIAGNOSTICO = 'select * from OKW.K_BITACORA_DIAGNOSTICO where FL_DIAGNOSTICO_PACIENTE in (select FL_DIAGNOSTICO_PACIENTE from OKW.K_DIAGNOSTICO_PACIENTE where FL_PACIENTE = {0}) order by FL_BITACORA'
    K_DETALLE_EXPEDIENTE = 'select * from OKW.K_DETALLE_EXPEDIENTE where FL_PACIENTE = {0} order by FL_DETALLE_EXPEDIENTE'
    K_DETALLE_EXPEDIENTE_HIST = 'select * from OKW.K_DETALLE_EXPEDIENTE_HIST where FL_DETALLE_EXPEDIENTE in (select FL_DETALLE_EXPEDIENTE from OKW.K_DETALLE_EXPEDIENTE where FL_PACIENTE = {0}) order by FL_DETALLE_EXPEDIENTE ,FE_CAMBIO'
    K_PRESCRIPCION = 'select * from OKW.K_PRESCRIPCION where FL_PACIENTE = {0} order by FL_PRESCRIPCION'
    K_ESTUDIO_CLINICO_PRESCRIPCION = 'select * from OKW.K_ESTUDIO_CLINICO_PRESCRIPCION where FL_PRESCRIPCION in (select FL_PRESCRIPCION from OKW.K_PRESCRIPCION where FL_PACIENTE = {0}) order by FL_PRESCRIPCION ,FL_PAQUETE_ESTUDIOS ,FL_ESTUDIO_CLINICO'
    K_ESTUDIO_CLINICO_RESULTADO = 'select * from OKW.K_ESTUDIO_CLINICO_RESULTADO where FL_PRESCRIPCION in (select FL_PRESCRIPCION from OKW.K_PRESCRIPCION where FL_PACIENTE = {0}) order by FL_PRESCRIPCION ,FL_ESTUDIO_CLINICO_RESULTADO'
    K_RESULTADO_ESTUDIO = 'select * from OKW.K_RESULTADO_ESTUDIO where FL_ESTUDIO_CLINICO_RESULTADO in (select FL_ESTUDIO_CLINICO_RESULTADO from OKW.K_ESTUDIO_CLINICO_RESULTADO where FL_PRESCRIPCION in (select FL_PRESCRIPCION from OKW.K_PRESCRIPCION where FL_PACIENTE = {0})) order by FL_ESTUDIO_CLINICO_RESULTADO ,FL_RESULTADO_ESTUDIO'
    K_EVENTO_PRESCRIPCION = 'select * from OKW.K_EVENTO_PRESCRIPCION where FL_PACIENTE = {0} order by FL_EVENTO_PRESCRIPCION'
    K_EXPLORACION_FISICA = 'select * from OKW.K_EXPLORACION_FISICA where FL_PACIENTE = {0} order by FL_EXPLORACION_FISICA'
    K_GALERIA = 'select * from OKW.K_GALERIA where FL_PACIENTE = {0} order by FL_GALERIA'
    K_HOJA_FAMILIAR = 'select * from OKW.K_HOJA_FAMILIAR where FL_PACIENTE = {0} order by FL_HOJA_FAMILIAR'
    K_LINEA_VIDA_REGISTRO_ACCION = 'select * from OKW.K_LINEA_VIDA_REGISTRO_ACCION where FL_PACIENTE = {0} order by FL_ACCION ,FL_REGISTRO'
    K_MEDICACION = 'select * from OKW.K_MEDICACION where FL_PACIENTE = {0} order by FL_MEDICACION'
    K_MEDICAMENTO_FC = 'select * from OKW.K_MEDICAMENTO_FC where FL_MEDICACION in (select FL_MEDICACION from OKW.K_MEDICACION where FL_PACIENTE = {0}) order by FL_MEDICACION'
    K_MEDICION_ANESTESIA = 'select * from OKW.K_MEDICION_ANESTESIA where FL_PACIENTE = {0} order by FL_MEDICION_ANESTESIA'
    K_MEDICION_PACIENTE = 'select * from OKW.K_MEDICION_PACIENTE where FL_PACIENTE = {0} order by FL_MEDICION_PACIENTE'
    K_MEDICION_SENSIBILIDAD_PACIENTE = 'select * from OKW.K_MEDICION_SENSIBILIDAD_PACIENTE where FL_PACIENTE = {0} order by FL_MEDICION_SENSIBILIDAD_PACIENTE'
    K_OPERACION_QUIRURGICA = 'select * from OKW.K_OPERACION_QUIRURGICA where FL_PACIENTE = {0} order by FL_OPERACION_QUIRURGICA'
    K_PACIENTE_INCAPACIDAD = 'select * from OKW.K_PACIENTE_INCAPACIDAD where FL_PACIENTE = {0} order by FL_PACIENTE_INCAPACIDAD'
    K_PACIENTE_VULNERABILIDAD = 'select * from OKW.K_PACIENTE_VULNERABILIDAD where FL_PACIENTE = {0} order by FL_PACIENTE_VULNERABILIDAD'
    K_PROCEDIMIENTO_PACIENTE = 'select * from OKW.K_PROCEDIMIENTO_PACIENTE where FL_PACIENTE = {0} order by FL_PROCEDIMIENTO_PACIENTE'
    K_VACUNA_PACIENTE = 'select * from OKW.K_VACUNA_PACIENTE where FL_PACIENTE = {0} order by FL_VACUNA_PACIENTE'

class SomatQueries:
    K_SOMATOMETRIA = 'select * from SOMATOMT.K_SOMATOMETRIA where FL_PACIENTE = {0} order by FL_SOMATOMETRIA'
    K_SOMATOMETRIA_DETALLE = 'select * from SOMATOMT.K_SOMATOMETRIA_DETALLE where FL_SOMATOMETRIA in (select FL_SOMATOMETRIA from SOMATOMT.K_SOMATOMETRIA where FL_PACIENTE = {0}) order by FL_SOMATOMETRIA ,FL_SOMATOMETRIA_DETALLE'

def _mk_key(key_name):
    return lambda data: '%s = %r' % (key_name, getattr(data, key_name))

def _mk_multikey(key_names):
    keys = map(_mk_key, key_names)
    return lambda data: '(%s)' % ', '.join(k(data) for k in keys)

_ignore_by_default = ['FG_REPLICADO', 'FE_ULTMOD', 'FL_PACIENTE_CITA']

class EntidadInfo(object):

    def __init__(self, record_type, query, keys, ignored_cols=_ignore_by_default):
        (self.record_type, self.query) = (record_type, query)
        self.key = (_mk_key(keys[0]) if len(keys) == 1 else _mk_multikey(keys))
        self.ignored = set(ignored_cols) | set(_ignore_by_default)

    @property
    def type_name(self):
        return self.record_type.__name__

    def cargaDatos(self, contexto, folio_paciente):
        return list(contexto.ExecuteQuery[self.record_type](self.query, folio_paciente))

    def llave(self, registro):
        return self.key(registro)

    def debe_comparar(self, prop_name):
        return prop_name.isupper() \
           and ('_' in prop_name) \
           and not (
               prop_name.startswith('C_') or
               prop_name.startswith('K_') or
               prop_name in self.ignored
               )
# end class EntidadInfo

INFO_ENTIDADES = {
    'OKW' : (
        EntidadInfo(OKW.C_PACIENTE, OkwQueries.C_PACIENTE, keys=['FL_PACIENTE'], ignored_cols=['FE_SYNC_EXPEDIENTE', 'FE_RECEP_EXPEDIENTE']),
        EntidadInfo(OKW.K_EXPEDIENTE, OkwQueries.K_EXPEDIENTE, keys=['FL_EXPEDIENTE']),
        EntidadInfo(OKW.K_PACIENTE_IDENTIFICADOR, OkwQueries.K_PACIENTE_IDENTIFICADOR, keys=['FL_IDENTIFICADOR']),

        EntidadInfo(OKW.K_ALERGIA_PACIENTE, OkwQueries.K_ALERGIA_PACIENTE, keys=['FL_ALERGIA_PACIENTE']),
        EntidadInfo(OKW.K_ANTECEDENTESGO, OkwQueries.K_ANTECEDENTESGO, keys=['FL_ANTECEDENTESGO']),
        EntidadInfo(OKW.K_ANTECEDENTESHF, OkwQueries.K_ANTECEDENTESHF, keys=['FL_ANTECEDENTEHF']),
        EntidadInfo(OKW.K_ANTECEDENTESNP, OkwQueries.K_ANTECEDENTESNP, keys=['ID_ANTECEDENTESNP']),
        EntidadInfo(OKW.K_ANTECEDENTESPP, OkwQueries.K_ANTECEDENTESPP, keys=['FL_ANTECEDENTEPP']),
        EntidadInfo(OKW.K_ANTECEDENTES_ESTRABOLOGICO, OkwQueries.K_ANTECEDENTES_ESTRABOLOGICO, keys=['FL_ANTECEDENTES_ESTRABOLOGICOS']),
        EntidadInfo(OKW.K_ANTECEDENTES_PERINATALE, OkwQueries.K_ANTECEDENTES_PERINATALE, keys=['FL_ANTECEDENTES_PERINATALES']),

        EntidadInfo(OKW.K_DIAGNOSTICO_PACIENTE, OkwQueries.K_DIAGNOSTICO_PACIENTE, keys=['FL_DIAGNOSTICO_PACIENTE']),
        EntidadInfo(OKW.K_BITACORA_DIAGNOSTICO, OkwQueries.K_BITACORA_DIAGNOSTICO, keys=['FL_BITACORA']),

        EntidadInfo(OKW.K_DETALLE_EXPEDIENTE, OkwQueries.K_DETALLE_EXPEDIENTE, keys=['FL_DETALLE_EXPEDIENTE']),
        EntidadInfo(OKW.K_DETALLE_EXPEDIENTE_HIST, OkwQueries.K_DETALLE_EXPEDIENTE_HIST, keys=('FL_DETALLE_EXPEDIENTE', 'FE_CAMBIO')),

        EntidadInfo(OKW.K_PRESCRIPCION, OkwQueries.K_PRESCRIPCION, keys=['FL_PRESCRIPCION']),
        EntidadInfo(OKW.K_ESTUDIO_CLINICO_PRESCRIPCION, OkwQueries.K_ESTUDIO_CLINICO_PRESCRIPCION, keys=('FL_PRESCRIPCION', 'FL_ESTUDIO_CLINICO')),

        EntidadInfo(OKW.K_ESTUDIO_CLINICO_RESULTADO, OkwQueries.K_ESTUDIO_CLINICO_RESULTADO, keys=['FL_ESTUDIO_CLINICO_RESULTADO']),
        EntidadInfo(OKW.K_RESULTADO_ESTUDIO, OkwQueries.K_RESULTADO_ESTUDIO, keys=['FL_RESULTADO_ESTUDIO']),

        EntidadInfo(OKW.K_EVENTO_PRESCRIPCION, OkwQueries.K_EVENTO_PRESCRIPCION, keys=['FL_EVENTO_PRESCRIPCION']),
        EntidadInfo(OKW.K_EXPLORACION_FISICA, OkwQueries.K_EXPLORACION_FISICA, keys=['FL_EXPLORACION_FISICA']),
        EntidadInfo(OKW.K_GALERIA, OkwQueries.K_GALERIA, keys=['FL_GALERIA']),
        EntidadInfo(OKW.K_HOJA_FAMILIAR, OkwQueries.K_HOJA_FAMILIAR, keys=['FL_HOJA_FAMILIAR']),
        EntidadInfo(OKW.K_LINEA_VIDA_REGISTRO_ACCION, OkwQueries.K_LINEA_VIDA_REGISTRO_ACCION, keys=['FL_REGISTRO']),

        EntidadInfo(OKW.K_MEDICACION, OkwQueries.K_MEDICACION, keys=['FL_MEDICACION']),
        EntidadInfo(OKW.K_MEDICAMENTO_FC, OkwQueries.K_MEDICAMENTO_FC, keys=['FL_MEDICACION']),

        EntidadInfo(OKW.K_MEDICION_ANESTESIA, OkwQueries.K_MEDICION_ANESTESIA, keys=['FL_MEDICION_ANESTESIA']),
        EntidadInfo(OKW.K_MEDICION_PACIENTE, OkwQueries.K_MEDICION_PACIENTE, keys=['FL_MEDICION_PACIENTE']),
        EntidadInfo(OKW.K_MEDICION_SENSIBILIDAD_PACIENTE, OkwQueries.K_MEDICION_SENSIBILIDAD_PACIENTE, keys=['FL_MEDICION_SENSIBILIDAD_PACIENTE']),
        EntidadInfo(OKW.K_OPERACION_QUIRURGICA, OkwQueries.K_OPERACION_QUIRURGICA, keys=['FL_OPERACION_QUIRURGICA']),
        EntidadInfo(OKW.K_PACIENTE_INCAPACIDAD, OkwQueries.K_PACIENTE_INCAPACIDAD, keys=['FL_PACIENTE_INCAPACIDAD']),
        EntidadInfo(OKW.K_PACIENTE_VULNERABILIDAD, OkwQueries.K_PACIENTE_VULNERABILIDAD, keys=['FL_PACIENTE_VULNERABILIDAD']),
        EntidadInfo(OKW.K_PROCEDIMIENTO_PACIENTE, OkwQueries.K_PROCEDIMIENTO_PACIENTE, keys=['FL_PROCEDIMIENTO_PACIENTE']),
        EntidadInfo(OKW.K_VACUNA_PACIENTE, OkwQueries.K_VACUNA_PACIENTE, keys=['FL_VACUNA_PACIENTE']),
    ),
    'SOMATOM' : (
        EntidadInfo(SOMATOM.K_SOMATOMETRIA, SomatQueries.K_SOMATOMETRIA, keys=['FL_SOMATOMETRIA']),
        EntidadInfo(SOMATOM.K_SOMATOMETRIA_DETALLE, SomatQueries.K_SOMATOMETRIA_DETALLE, keys=['FL_SOMATOMETRIA_DETALLE']),
    ),
}
