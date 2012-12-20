#!/bin/env ipy
# -*- coding: utf-8 -*-

import clr
import sys

from comp import comp, PacienteNoEncontrado
import data

data.is_script = (__name__ == '__main__')

def _to_folios(args):
    return (int(arg) for arg in args if arg.isdigit())

def _get_folios_paciente():
    return list(_to_folios(sys.argv))

def _verbose():
    return bool([1 for arg in sys.argv if arg == '-v'])

def _compara_okw(fl_paciente):
    with data.okw_data_ctx('Source') as src_context:
        with data.okw_data_ctx('Target') as ref_context:
            rsrc = data.RecordSource(src_context, ref_context, fl_paciente)
            return comp('OKW', rsrc, _verbose())

def _compara_somatom(fl_paciente):
    with data.smt_data_ctx('Source') as src_context:
        with data.smt_data_ctx('Target') as ref_context:
            rsrc = data.RecordSource(src_context, ref_context, _fl_paciente)
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
