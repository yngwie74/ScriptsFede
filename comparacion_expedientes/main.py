#!/bin/env ipy
# -*- coding: utf-8 -*-

import sys

if (__name__ == '__main__'): # running as script?
    sys.path.append(r'C:\Users\alfredo.chavez\Proyectos\Medtzin\Comunes')

from comp import comp, PacienteNoEncontrado
from data import okw_data_ctx, RecordSource, smt_data_ctx

def _to_folios(args):
    return (int(arg) for arg in args if arg.isdigit())

def _get_folios_paciente():
    return list(_to_folios(sys.argv))

def _verbose():
    return bool([1 for arg in sys.argv if arg == '-v'])

def _compara_okw(fl_paciente):
    with okw_data_ctx('s') as src_context:
        with okw_data_ctx('t') as ref_context:
            rsrc = RecordSource(src_context, ref_context, fl_paciente)
            return comp('OKW', rsrc, _verbose())

def _compara_somatom(fl_paciente):
    with smt_data_ctx('s') as src_context:
        with smt_data_ctx('t') as ref_context:
            rsrc = RecordSource(src_context, ref_context, _fl_paciente)
            return comp('SOMATOM', rsrc, _verbose())

def _pide_folios():
    is_first = True
    while 1:
        prompt = 'Digite el folio del%s expediente a comparar: ' % ('' if is_first else ' siguiente')
        try:
            yield raw_input(prompt).strip()
        except EOFError:
            break
        is_first = False


pacientes = _get_folios_paciente()
if not pacientes:
    pacientes = _to_folios(_pide_folios())

_first = True
for _fl_paciente in pacientes:
    if not _first:
        print '-' * 80

    print 'Paciente %d...' % _fl_paciente

    okw_ok = som_ok = False

    try:
        okw_ok = _compara_okw(_fl_paciente)
        som_ok = _compara_somatom(_fl_paciente)
    except PacienteNoEncontrado, e:
        print e

    if okw_ok and som_ok:
        print 'Los expedientes son iguales'

    _first = False
# done!
