#!/bin/env ipy
# -*- coding: utf-8 -*-

from System import Console
from System.IO import Path
from System.Reflection import Assembly

import sys

is_script = __name__ == '__main__'
if is_script:
    sys.path.append(r'C:\Users\alfredo.chavez\Proyectos\IronPython\Federado\fix_paciente_identificador\bin\Debug')

import dataaccess
import scriptgen
import logmanager

from erroresapp import *
from utils import es_diacritico, sin_acentos, primero

_LOCAL = 'localhost'
_FEDERADO = '<Instancia Federado>'

log4py = None


def log_n_continue(f):

    def wrap(*args, **kwds):
        try:
            return f(*args, **kwds)
        except ErrorEsperado, e:
            log4py.error(e)

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
            self.generador.addSynch(identificador.FL_PACIENTE_IDENTICADOR, fede)
            return False
        return True

    @log_n_continue
    def _valida_identificadores_comunes(self):
        for identificador in self.local.ids_comunes(self.fede):
            sys.stdout.write(self._valida_identificador(identificador) and '.' or 'x')

    def _valida_identificadores_faltantes(self):
        faltantes = self.local.ids_que_te_faltan_de(self.fede)
        if faltantes:
            self.generador.addInserts(faltantes)
            sys.stdout.write('+')

    @log_n_continue
    def _valida_identificadores_sobrantes(self):
        sobrantes = self.local.ids_que_le_faltan_a(self.fede)
        if sobrantes:
            raise ErrorIdentificadoresFaltantes(self.folio, sobrantes)

    def _valida_identificadores(self):
        self._valida_identificadores_comunes()
        self._valida_identificadores_faltantes()
        self._valida_identificadores_sobrantes()

    @log_n_continue
    def procesa(self):
        self._carga_paciente_local()
        self._carga_paciente_desde_federado()
        self._valida_nombres()
        self._valida_identificadores()

#end class CorrectorPacId


def _find_arg(arg):
    pred = (arg if callable(arg) else lambda a: a == arg)
    return primero(a for a in sys.argv if pred(a))


def _mostrar_ayuda():
    main_module = Assembly.GetEntryAssembly().Location
    exe_name = Path.GetFileNameWithoutExtension(main_module)

    print sin_acentos('''%s [-sl:<servidor_local>] [-dl:<base_datos_local>]
\t[-sr:<servidor_remoto>] [-dr:<base_datos_remoto>]
\t[-|<folio>[ folio[ folio[ ...]]] [-?]

Donde:
-sl y -sr:
\tson los servidores de SQL Server a usar, incluyendo el nombre de
\tinstancia de ser necesario (p.e. "localhost\\SqlProd"). Por default se
\tusa "localhost" como local y federado como remoto.

-dl y -dr:
\tson los nombres de las bases de datos a usar. Por default se usará OKW
\ten ambos casos.

folio [...] | -
\tson los folios de los pacientes a procesar.
\tSi en su lugar se especifica el parámetro "-", se tomarán los folios
\tdesde la consola. Por default se leen todos los pacientes de la tabla
\tOKW.C_PACIENTE del servidor local.

-?:
\tMuestra esta pantalla.''' \
        % (sys.argv[0] if is_script else exe_name), es_diacritico)


def _parse_arg(argname, default):
    arg_pfx = '-%s:' % argname.lower()
    found = _find_arg(lambda a: a.lower().startswith(arg_pfx))
    if found:
        return found[len(arg_pfx):].strip('"')
    return default


def _pide_folios():
    is_first = True
    while 1:
        prompt = 'Digite el folio del%s expediente a comparar: ' % ((''
                 if is_first else ' siguiente'))
        print prompt,
        try:
            yield Console.ReadLine().strip()
        except:
            break
        is_first = False


def _parse_ints(seq):
    return (int(item) for item in seq if item.isdigit())


def folios(src_context):
    if _find_arg('-'):
        return _parse_ints(_pide_folios())

    found = list(_parse_ints(sys.argv))
    if not found:
        found = dataaccess.obten_pacientes(src_context)
    return found


def _get_connstr(sarg, darg, sdefault, ddefault='OKW'):
    return dataaccess.mkconnstr(
        host=_parse_arg(sarg, sdefault),
        db=_parse_arg(darg, ddefault),
        )

@with_logging
def main():
    con_str = _get_connstr('sl', 'dl', _LOCAL)

    with dataaccess.contexto_okw(con_str) as src_context:

        plaza_local = int(dataaccess.obten_plaza_local(src_context))
        nombre_script = 'fix_k_paciente_identificador_%02d' % plaza_local
        gen = scriptgen.ScriptGen(nombre_script, slice_size=100)

        con_str = _get_connstr('sr', 'dr', _FEDERADO)
        with dataaccess.contexto_okw(con_str) as ref_context:
            for fl_paciente in folios(src_context):
                CorrectorPacId(src_context, ref_context, fl_paciente, gen).procesa()

        gen.done()
    print 'ok'

#~ Main script

if _find_arg('-?'):
    _mostrar_ayuda()
    sys.exit(0)

with logmanager.LogManager() as log4py:
    main()

#~ done!
