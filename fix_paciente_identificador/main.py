#!/bin/env ipy
# -*- coding: utf-8 -*-

import sys

is_script = __name__ == '__main__'
if is_script:
    sys.path.append(r'C:\Users\alfredo.chavez\Proyectos\IronPython\Federado\fix_paciente_identificador\bin\Debug')

import dataaccess
import scriptgen
import logmanager

from erroresapp import *
from utils import sin_acentos

_LOCAL = 'localhost'
_FEDERADO = '<Instancia Federado>'

log4py = None

def log_n_continue(f):
    def wrap(*args, **kwds):
        try:
            return f(*args, **kwds)
        except ErrorEsperado, e:
            log4py.error(e)
        except Exception, e:
            log4py.error(e)
            raise
    return wrap

def with_logging(f):
    def wrap(*args, **kwds):
        try:
            return f(*args, **kwds)
        except Exception, e:
            log4py.error(e)
            raise
    return wrap

class CorrectorPacId(object):

    def __init__(self, ctx_local, ctx_fede, fl_paciente, generador):
        self.ctx_local = ctx_local
        self.ctx_fede = ctx_fede
        self.folio = fl_paciente
        self.generador = generador

    def _carga_paciente(self, desde_federado):
        contexto = (self.ctx_fede if desde_federado else self.ctx_local)
        paciente = dataaccess.carga_paciente(contexto, self.folio)
        if not paciente:
            raise ErrorPacienteNoEncontrado(self.folio, en_federado=desde_federado)
        return paciente

    def _carga_paciente_local(self):
        self.local = self._carga_paciente(False)

    def _carga_paciente_desde_federado(self):
        self.fede = self._carga_paciente(True)

    def _valida_nombres(self):
        nombre = lambda p: sin_acentos(p.nombre_comp)
        if nombre(self.local) != nombre(self.fede):
            raise ErrorNombrePacienteNoCoincide(self.local, self.fede)

    @log_n_continue
    def _valida_identificador(self, identificador):
        fede = self.fede.busca_id(identificador.FL_IDENTIFICADOR)

        if not fede:
            raise ErrorIdentificadorNoEncontrado(self.folio, identificador.FL_IDENTIFICADOR)
        elif identificador.DS_TEXTO != fede.DS_TEXTO:
            raise ErrorIdentificadorNoCoincide(identificador, fede)
        elif identificador.FL_PACIENTE_IDENTICADOR != fede.FL_PACIENTE_IDENTICADOR:
            self.generador.addChange(identificador.FL_PACIENTE_IDENTICADOR, fede)
            return False
        return True

    def _valida_identificadores(self):
        for identificador in self.local.identificadores:
            sys.stdout.write(self._valida_identificador(identificador) and '.' or 'x')

        if self.local.tiene_menos_ids_que(self.fede):
            raise ErrorIdentificadoresFaltantes(self.local, self.fede)

    @log_n_continue
    def procesa(self):
        self._carga_paciente_local()
        self._carga_paciente_desde_federado()
        self._valida_nombres()
        self._valida_identificadores()


def folios(src_context, plaza_local):
    found = [int(a) for a in sys.argv[1:] if a.isdigit()]
    if not found:
        found = dataaccess.obten_pacientes(src_context)
    return found


@with_logging
def main():
    con_str = dataaccess.mkconnstr(_LOCAL) #, 'AdeM')
    with dataaccess.contexto_okw(con_str) as src_context:

        plaza_local = int(dataaccess.obten_plaza_local(src_context))
        nombre_script = 'fix_k_paciente_identificador_%02d' % plaza_local
        gen = scriptgen.ScriptGen(nombre_script, slice_size=100)

        todos_los_pacientes = folios(src_context, plaza_local)

        with dataaccess.contexto_okw(dataaccess.mkconnstr(_FEDERADO)) as ref_context:
            for fl_paciente in todos_los_pacientes:
                CorrectorPacId(src_context, ref_context, fl_paciente, gen).procesa()

        gen.done()
    print 'ok'

with logmanager.LogManager() as log4py:
    main()

# done!
