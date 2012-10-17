#!/env/ipy
# -*- coding: utf-8 -*-

import clr
import sys

from comp import comp
import data

data.is_script = (__name__ == '__main__')

def _to_folios(args):
    return [int(arg) for arg in args if arg.isdigit()]

def _get_folios_paciente():
    return _to_folios(sys.argv)

def _verbose():
    return bool([1 for arg in sys.argv if arg == '-v'])

pacientes = _get_folios_paciente()
if not pacientes:
    print 'No se proporcionó ningún folio de paciente. Por favor, digite los folios a comparar: ',
    pacientes = _to_folios(raw_input().split())

for _fl_paciente in pacientes:
    print 'Paciente %d...' % _fl_paciente

    are_equal = True

    with data.okw_data_ctx('Source') as src_context:
        with data.okw_data_ctx('Target') as ref_context:
            rsrc = data.RecordSource(src_context, ref_context, _fl_paciente)
            are_equal = are_equal and comp('OKW', rsrc, _verbose())

    with data.smt_data_ctx('Source') as src_context:
        with data.smt_data_ctx('Target') as ref_context:
            rsrc = data.RecordSource(src_context, ref_context, _fl_paciente)
            are_equal = are_equal and comp('SOMATOM', rsrc, _verbose())

    if are_equal:
        print 'Los expedientes son iguales'
# done!
