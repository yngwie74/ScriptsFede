# -*- coding: utf-8 -*-

class ErrorEsperado(Exception):

    LOG_FORMAT = ''

    def __init__(self, *args, **kwds):
        fmt = self.__class__.LOG_FORMAT
        mensaje = fmt % (kwds if kwds else tuple(args))
        Exception.__init__(self, mensaje)

#end class


class ErrorPacienteNoEncontrado(ErrorEsperado):

    LOG_FORMAT = '%d|%s'
    HEADER = 'FL_PACIENTE|LUGAR'

    def __init__(self, fl_paciente, en_federado=False):
        ErrorEsperado.__init__(self, fl_paciente, ('federado' if en_federado else 'local'))

#end class


class ErrorNombrePacienteNoCoincide(ErrorEsperado):

    LOG_FORMAT = '%d|%s|%s'
    HEADER = 'FL_PACIENTE|NOMBRE LOCAL|NOMBRE FEDERADO'

    def __init__(self, local, federado):
        ErrorEsperado.__init__(self, local.FL_PACIENTE, local.nombre_comp, federado.nombre_comp)

#end class


class ErrorIdentificadorNoEncontrado(ErrorEsperado):

    LOG_FORMAT = '%d|%d'
    HEADER = 'FL_PACIENTE|FL_IDENTIFICADOR'

    def __init__(self, fl_paciente, fl_identificador):
        ErrorEsperado.__init__(self, fl_paciente, fl_identificador)

#end class


class ErrorIdentificadorNoCoincide(ErrorEsperado):

    LOG_FORMAT = '%(fl_paciente)d|%(fl_identificador)d|%(ds_texto_local)s|%(ds_texto_federado)s'
    HEADER = 'FL_PACIENTE|FL_IDENTIFICADOR|DS_TEXTO LOCAL|DS_TEXTO FEDERADO'

    def __init__(self, local, federado):
        ErrorEsperado.__init__(self,
            fl_paciente=local.FL_PACIENTE,
            fl_identificador=local.FL_IDENTIFICADOR,
            ds_texto_local=local.DS_TEXTO,
            ds_texto_federado=federado.DS_TEXTO)

#end class


class ErrorIdentificadoresFaltantes(ErrorEsperado):

    LOG_FORMAT = '%d|%s'
    HEADER = 'FL_PACIENTE|FALTANTES'

    def __init__(self, fl_paciente, ids_diff):
        str_diff = self._formatea_diff(ids_diff)
        ErrorEsperado.__init__(self, fl_paciente, str_diff)

    def _formatea_diff(self, idents):
        return '|'.join('FL_IDENTIFICADOR={0};DS_TEXTO={1}'.format(id.FL_IDENTIFICADOR, id.DS_TEXTO) for id in idents)

#end class


class ErrorIdentificadorYaExiste(ErrorEsperado):

    LOG_FORMAT = '%(fl_paciente_identicador)d|%(fl_paciente_local)d|%(ds_texto_local)s|%(fl_paciente_federado)d|%(ds_texto_federado)s'
    HEADER = 'FL_PACIENTE_IDENTICADOR|FL_PACIENTE LOCAL|DS_TEXTO LOCAL|FL_PACIENTE FEDERADO|DS_TEXTO FEDERADO'

    def __init__(self, local, federado):
        ErrorEsperado.__init__(self,
            fl_paciente_identicador=local.FL_PACIENTE_IDENTICADOR,
            fl_paciente_local=local.FL_PACIENTE,
            ds_texto_local=local.DS_TEXTO,
            fl_paciente_federado=federado.FL_PACIENTE,
            ds_texto_federado=federado.DS_TEXTO,
            )

