# -*- coding: utf-8 -*-

import sys
from System.IO import File
from System import DateTime

from erroresapp import *

class LogManager(object):

    def __init__(self):
        self.loggers = {
            ErrorIdentificadorNoCoincide:   Log('identificadores_diferentes', ErrorIdentificadorNoCoincide.HEADER),
            ErrorIdentificadorNoEncontrado: Log('identificadores_no_encontrados', ErrorIdentificadorNoEncontrado.HEADER),
            ErrorIdentificadorYaExiste:     Log('identificadores_ya_existentes', ErrorIdentificadorYaExiste.HEADER),
            ErrorIdentificadoresFaltantes:  Log('identificadores_falantes_fed', ErrorIdentificadoresFaltantes.HEADER),
            ErrorNombrePacienteNoCoincide:  Log('pacientes_nombres_diferentes', ErrorNombrePacienteNoCoincide.HEADER),
            ErrorPacienteNoEncontrado:      Log('pacientes_no_encontrados', ErrorPacienteNoEncontrado.HEADER),
            }
        self.default = Log('errores')

    @property
    def _all_loggers(self):
        return [self.default] + self.loggers.values()

    def _logger_for(self, exception):
        return self.loggers.get(exception.__class__, self.default)

    def error(self, exception):
        self._logger_for(exception).error(exception)
        sys.stdout.write('!')

    def __enter__(self):
        for log in self._all_loggers:
            log.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for log in self._all_loggers:
            log.close()


class Log(object):

    def __init__(self, nombre, header=None):
        self.nombre = '%s.log' % nombre
        self.header = header
        self.file = None
        self.lineas = 0

    def open(self):
        self.file = open(self.nombre, 'w', 1)
        if self.header:
            self.file.write('timestamp|%s\n' % self.header)
        return self

    def close(self):
        try:
            if self.file:
                self.file.close()
            if self.lineas == 0 and File.Exists(self.nombre):
                File.Delete(self.nombre)
        except:
            pass

    @property
    def timestamp(self):
        return DateTime.Now.ToString('yyyy-MM-dd HH:mm:ss.fff')

    def error(self, exception):
        self.file.write('%s|%s\n' % (self.timestamp, exception))
        self.file.flush()
        self.lineas += 1

