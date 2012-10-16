#!/env/ipy
# -*- coding: utf-8 -*-

import clr
clr.AddReference('System.Core')

import System
clr.ImportExtensions(System.Linq)
from System import *
from System.Linq import Enumerable

clr.AddReference('Entities')
from Entities import OKW, SOMATOM

clr.AddReference('Newtonsoft.Json')
from Newtonsoft.Json import JsonConvert

from itertools import cycle, islice, izip, takewhile
from utils import (
    clona,
    getdate,
    get_huge_exp,
    LargestList,
    rand,
    safe_set_prop,
    trace,
    )


_FE_SYNC_DEFAULT            = DateTime(1900, 1, 1)

_MAX_EVENTOS_PRESCIPCION    = 182
_MAX_EXPEDIENTES            = 7
_MAX_PACIENTES              = 15
_MAX_PACIENTE_IDENTIFICADOR = 8
_MAX_RESULTADO_ESTUDIOS     = 14

_PROGRAMA                   = 'load_test'

_KB                         = 1024
_MB                         = _KB * _KB

_HUGE_EXP_SIZE              = 13 * _MB


def with_defaults(func):

    def wrapped_f(self, *args, **kwds):
        result = func(self, *args, **kwds)
        return self._set_defaults(result)

    return wrapped_f


class Script(object):
    def __init__(self, okw, somatom, max=1.0):
        self.okw = okw
        self.somatom = somatom
        (self._icount, self._iusr) = (0, 0)

        self._ratio = (max or 1.0) * 1.0
        self._carga_datos()

    def _carga_datos(self):
        self._usuarios = [(u.FL_USUARIO, u.CL_LOGIN) for u in
                              self.okw.C_USUARIOs.Take(10) .Where(lambda u: u.CL_LOGIN != 'super')]

        MAXP = self._get_max(_MAX_PACIENTES)
        self._pacientes = [p.FL_PACIENTE for p in
                               self.okw.C_PACIENTEs.Take(MAXP) .Where(lambda p: p.CL_ESTATUS == 'A')]

        self._pacientes_cycler = cycle(self._pacientes)
        self._sig_paso()

    @property
    def fl_usuario(self):
        return self._usuarios[self._iusr][0]

    @property
    def cl_login(self):
        return self._usuarios[self._iusr][1]

    @property
    def fl_paciente(self):
        return self._ipac

    def procesa(self):
        if get_huge_exp():
            self.gen_notas_expediente_gigante()
        else:
            self.gen_prescripciones()
            self.gen_medicaciones()
            self.gen_diagnosticos()
            self.gen_notas_carga_normal()

            self.gen_pacientes()

            self.gen_somatometrias()

        self.okw.SubmitChanges()
        self.somatom.SubmitChanges()

    @trace
    def gen_prescripciones(self):
        resultados = self._get_muestra_estudio_clinico_resultado()

        for contador_eventos in self._max_range(_MAX_EVENTOS_PRESCIPCION):
            evento = self._gen_evento_prescripcion()

            cuantas = 1 + (self._icount % 6 == 0 and 1 or 0)
            prescripciones = [self._gen_prescripcion() for i in xrange(cuantas)]
            evento.K_PRESCRIPCIONs.AddRange(prescripciones)

            self._agrega_estudios_clinicos_prescripciones(prescripciones)
            generados = self._agrega_estudios_clinicos_resultados(prescripciones, resultados)
            self._agrega_resultados_estudios(generados)

            self.okw.K_EVENTO_PRESCRIPCIONs.InsertOnSubmit(evento)
            self._sig_paso()

    def _get_muestra_estudio_clinico_resultado(self):
        MAX_RESULTADOS = self._get_max(_MAX_RESULTADO_ESTUDIOS)
        muestra_resultados = list(self.okw.K_ESTUDIO_CLINICO_RESULTADOs.Take(10))
        return islice(cycle(muestra_resultados), MAX_RESULTADOS)

    def _agrega_estudios_clinicos_resultados(self, prescripciones, resultados):
        generados = []
        for (prescripcion, resultado) in izip(prescripciones, resultados):
            nuevo_resultado = self._clona_resultado(resultado)
            prescripcion.K_ESTUDIO_CLINICO_RESULTADOs.Add(nuevo_resultado)
            generados.append(nuevo_resultado)
        return generados

    def _clona_resultado(self, resultado):
        nueva = self._set_defaults(clona(resultado))
        nueva.UI_RESULTADO = Guid.NewGuid()
        nueva.FE_AGREGADO = getdate().AddMinutes(self._icount)
        return nueva

    def _agrega_resultados_estudios(self, estudio_clinico_resultados):
        for ecr in estudio_clinico_resultados:
            resultado_estudio = self._gen_resultado_estudio(ecr)
            self.okw.K_RESULTADO_ESTUDIOs.InsertOnSubmit(resultado_estudio)

    @with_defaults
    def _gen_resultado_estudio(self, estudio_clinico_resultado):
        return OKW.K_RESULTADO_ESTUDIO(
            FE_REALIZACION=getdate(),
            DS_DESCRIPCION='DS_DESCRIPCION %d' % self._icount,
            DS_ORIGEN='DS_ORIGEN %d' % self._icount,
            K_ESTUDIO_CLINICO_RESULTADO = estudio_clinico_resultado,
            )

    def _agrega_estudios_clinicos_prescripciones(self, prescripciones):
        tipo_estudio = 1
        for prescripcion in prescripciones:
            cuantos = 2 + (self._icount % 9 == 0 and 1 or 0)
            estudios = [self._gen_estudio_clinico_prescripcion(tipo_estudio + i) for i in
                        xrange(cuantos)]
            prescripcion.K_ESTUDIO_CLINICO_PRESCRIPCIONs.AddRange(estudios)
            tipo_estudio += len(estudios)

    @with_defaults
    def _gen_evento_prescripcion(self):
        return OKW.K_EVENTO_PRESCRIPCION(
            DS_EVENTO='DS_EVENTO prueba %d' % self._icount,
            FE_PRESCRIPCION=getdate(),
            )

    @with_defaults
    def _gen_prescripcion(self):
        return OKW.K_PRESCRIPCION(
            FL_SERVICIO=123,
            CL_ESTATUS_PRESCRIPCION=1,
            NO_SESIONES=1,
            NO_SESIONES_AGENDADAS=0,
            FG_PACIENTE=1,
            FG_POST_HOSPITALARIA=False,
            FG_QUIROFANO=False,
            FL_PRESCRIPCION_QX=False,
            )

    @with_defaults
    def _gen_estudio_clinico_prescripcion(self, fl_estudio):
        return OKW.K_ESTUDIO_CLINICO_PRESCRIPCION(FL_ESTUDIO_CLINICO=fl_estudio)

    @trace
    def gen_medicaciones(self):
        for i in self._max_range(111):
            self.okw.K_MEDICACIONs.InsertOnSubmit(self._gen_medicacion())
            self._sig_paso()

    @with_defaults
    def _gen_medicacion(self):

        # Evitamos el límite de 13 argumentos x función en ipy

        m = OKW.K_MEDICACION()
        m.FL_PRESENTACION               = 379
        m.NO_CANTIDAD                   = 1
        m.NO_FRECUENCIA                 = 24
        m.NO_DURACION                   = 60
        m.DS_OBSERVACIONES              = 'DS_OBSERVACIONES %d' % self._icount
        m.FG_SUSPENDIDO                 = False
        m.FE_INICIAR                    = getdate()
        m.FG_HOSPITALIZADO              = False
        m.FG_FUERA_CUADRO               = False
        m.FG_DOSIS                      = False
        m.FL_USUARIO                    = self.fl_usuario
        m.FL_UNIDAD_TIEMPO_FRECUENCIA   = 4
        m.FL_UNIDAD_TIEMPO_DURACION     = 2
        m.FG_CONTRAREFERENCIA           = False
        m.FE_HASTA                      = getdate().AddDays(60)
        m.FG_POST_HOSPITALARIA          = False
        return m

    @trace
    def gen_diagnosticos(self):
        MAX = self._get_max(19)

        folios = (36675, 28895, 36671, 26766, 36685)
        diags = (self._sig_paso() or self._gen_diagnostico(folio) for folio in cycle(folios))

        for diag in islice(diags, MAX):
            self.okw.K_DIAGNOSTICO_PACIENTEs.InsertOnSubmit(diag)

    @with_defaults
    def _gen_diagnostico(self, diag):
        return OKW.K_DIAGNOSTICO_PACIENTE(
            FL_DIAGNOSTICO=diag,
            FL_SEVERIDAD_DIAGNOSTICO=1,
            FL_ESTATUS_DIAGNOSTICO=2,
            FE_DIAGNOSTICO=getdate(),
            FL_PACIENTE_CITA=0,
            FG_ACCION_QX=False,
            FG_ACCION_INCAPACIDAD=False,
            FG_ACCION_REFERENCIA=False,
            FG_ACCION_CONTRARREFERENCIA=False,
            FG_REPLICADO=False,
            )

    @trace
    def gen_notas_carga_normal(self):
        max_notas_cnt = self._get_max(121)

        notas = list(n for n in self.okw.K_DETALLE_EXPEDIENTEs.Take(10))

        for nota in islice(cycle(notas), max_notas_cnt):
            nueva = self._clona_nota(nota)
            self.okw.K_DETALLE_EXPEDIENTEs.InsertOnSubmit(nueva)

    @trace
    def gen_notas_expediente_gigante(self):
        tamano_max = self._get_max(_HUGE_EXP_SIZE)

        query = \
            'select FL_PACIENTE from (select top 1 FL_PACIENTE, COUNT(*) as Cuantos from okw.K_DETALLE_EXPEDIENTE group by FL_PACIENTE order by COUNT(*) desc) as t'
        fl_paciente = self.okw.ExecuteQuery[System.Int32](query).First()

        print '\tCargando notas del paciente %d...' % fl_paciente
        query = 'SELECT * FROM [OKW].[K_DETALLE_EXPEDIENTE] WHERE FL_PACIENTE = {0}'
        notas = self.okw.ExecuteQuery[OKW.K_DETALLE_EXPEDIENTE](query, fl_paciente)

        max_largest = 4
        largest = LargestList(max_largest)

        (n, longitud_total) = (0, 0)
        for nota in takewhile(lambda x: longitud_total < tamano_max, notas):
            json = JsonConvert.SerializeObject(nota)
            longitud = len(json)

            largest << (longitud, nota)

            longitud_total += longitud
            n += 1

        if longitud_total < tamano_max:
            print '\tAgregando notas hasta %dMB...' % (tamano_max / _MB)
            for (longitud, nota) in takewhile(lambda x: longitud_total < tamano_max,
                                              cycle(largest)):
                nueva = self._clona_nota(nota)
                self.okw.K_DETALLE_EXPEDIENTEs.InsertOnSubmit(nueva)

                longitud_total += longitud
                n += 1

        print str.Format('\tPaciente {0}: {1} notas = {2:#,###.00}MB', fl_paciente, n,
                         longitud_total * 1.0 / _MB)

    def _clona_nota(self, nota):
        nueva = self._set_defaults(clona(nota), False)
        nueva.FL_DETALLE_EXPEDIENTE = 0
        nueva.FL_USUARIO = nota.FL_USUARIO
        nueva.CL_USUARIO = nota.CL_USUARIO
        nueva.UI_EXPEDIENTE = Guid.NewGuid()
        nueva.FE_CAPTURA = getdate().AddMinutes(self._icount)
        return nueva

    @trace
    def gen_pacientes(self):
        self._update_registros(self._pacientes)
        self._gen_expedientes()
        self._gen_paciente_identificadores()

    @trace
    def _gen_expedientes(self):
        self._actualiza_para_pacientes(_MAX_EXPEDIENTES, self.okw.K_EXPEDIENTEs)

    @trace
    def _gen_paciente_identificadores(self):
        self._actualiza_para_pacientes(_MAX_PACIENTE_IDENTIFICADOR,
                                       self.okw.K_PACIENTE_IDENTIFICADORs)

    def _actualiza_para_pacientes(self, max_registros, tabla):
        max_pacientes = self._get_max(max_registros)
        for fl_paciente in islice(self._pacientes, max_pacientes):
            registros = list(tabla.Where(lambda r: r.FL_PACIENTE == fl_paciente))
            if registros:
                self._update_registros(registros)

    def _update_registros(self, entidades):
        for entidad in entidades:
            self._update_registro(entidad)

    def _update_registro(self, entidad):
        safe_set_prop(entidad, 'FE_ULTMOD', getdate())
        safe_set_prop(entidad, 'FG_REPLICADO', False)

    @trace
    def gen_somatometrias(self):
        mediciones = (1, 2, 6, 7, 8, 9, 11)

        for i in self._max_range(67):
            som = self._gen_somatometria()
            self.somatom.K_SOMATOMETRIAs.InsertOnSubmit(som)

            detalle = [self._gen_somatometria_detalle(medicion) for medicion in mediciones]
            som.K_SOMATOMETRIA_DETALLEs.AddRange(detalle)

            self._sig_paso()

    @with_defaults
    def _gen_somatometria(self):
        return SOMATOM.K_SOMATOMETRIA(
            FE_MEDICION=getdate(),
            OBSERVACIONES='OBSERVACIONES %d' % self._icount,
            )

    @with_defaults
    def _gen_somatometria_detalle(self, medicion):
        return SOMATOM.K_SOMATOMETRIA_DETALLE(
            FL_SOMATOMETRIA_MEDICION=medicion,
            VALOR_MEDICION1=1,
            VALOR_MEDICION2=1 if medicion == 8 else None,
            CL_ORIGEN_MEDICION=None,
            )

    def _set_defaults(self, entidad, with_fl_paciente=True):
        now = getdate()
        defaults = dict(
            FE_CREACION=now,
            FE_ULTMOD=now,
            FL_PACIENTE=self.fl_paciente,
            FL_USUARIO=self.fl_usuario,
            CL_USUARIO=self.cl_login,
            NB_PROGRAMA=_PROGRAMA,
            FG_REPLICADO=False,
            FE_SYNC_EXPEDIENTE=_FE_SYNC_DEFAULT,
            )

        for (p, v) in defaults.iteritems():
            if p == 'FL_PACIENTE' and with_fl_paciente == False:
                continue
            safe_set_prop(entidad, p, v)

        return entidad

    def _get_max(self, max):
        return int(max * self._ratio) or 1

    def _max_range(self, max):
        return xrange(self._get_max(max))

    def _sig_paso(self):
        self._sig_paciente()
        self._sig_usuario()
        self._icount += 1

    def _sig_paciente(self):
        self._ipac = self._pacientes_cycler.next()

    def _sig_usuario(self):
        self._iusr += 1
        if self._iusr >= len(self._usuarios):
            self._iusr = 0

