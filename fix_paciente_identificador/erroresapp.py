# -*- coding: utf-8 -*-

class ErrorEsperado(Exception):

    LOG_FORMAT = ''

    def __init__(self, *args, **kwds):
        fmt = self.__class__.LOG_FORMAT
        mensaje = fmt % (kwds if kwds else tuple(args))
        Exception.__init__(self, mensaje)

#end class


class ErrorPacienteNoEncontrado(ErrorEsperado):

    LOG_FORMAT = 'Paciente %d no encontrado%s'

    def __init__(self, fl_paciente, en_federado=False):
        ErrorEsperado.__init__(self, fl_paciente, (' en federado' if en_federado else ''))

#end class


class ErrorNombrePacienteNoCoincide(ErrorEsperado):

    LOG_FORMAT = 'FL_PACIENTE=%d|%s|%s'

    def __init__(self, local, federado):
        ErrorEsperado.__init__(self, local.FL_PACIENTE, local.nombre_comp, federado.nombre_comp)

#end class


class ErrorIdentificadorNoEncontrado(ErrorEsperado):

    LOG_FORMAT = 'FL_PACIENTE=%d|FL_IDENTIFICADOR=%d'

    def __init__(self, fl_paciente, fl_identificador):
        ErrorEsperado.__init__(self, fl_paciente, fl_identificador)

#end class


class ErrorIdentificadorNoCoincide(ErrorEsperado):

    LOG_FORMAT = 'FL_PACIENTE=%(fl_paciente)d|FL_IDENTIFICADOR=%(fl_identificador)d|%(ds_texto_local)s|%(ds_texto_federado)s'

    def __init__(self, local, federado):
        ErrorEsperado.__init__(self,
            fl_paciente=fl_paciente,
            fl_identificador=local.FL_IDENTIFICADOR,
            ds_texto_local=local.DS_TEXTO,
            ds_texto_federado=federado.DS_TEXTO)

#end class


class ErrorIdentificadoresFaltantes(ErrorEsperado):

    LOG_FORMAT = 'Los identificadores %(ids)s del paciente %(folio)d faltan localmente'

    def __init__(self, local, federado):
        fl_paciente = local.FL_PACIENTE
        faltantes = local.ids_que_te_faltan_de(federado)
        ErrorEsperado.__init__(self, folio=fl_paciente, ids=faltantes)

#end class

