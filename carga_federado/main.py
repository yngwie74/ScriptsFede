#!/env/ipy
# -*- coding: utf-8 -*-

import clr
clr.AddReference('DAO')
import DAO
from DAO.OKW import DAOokwDataContext
from DAO.SOMATOM import DAOSomatomDataContext

clr.AddReference('System.Configuration')
from System.Configuration import ConfigurationManager

import System

from script import Script
from utils import get_ratio, get_help, with_trace

_DEFAULT_COMMAND_TIMEOUT = 300
_CS_OKW     = "Data Source=localhost;Initial Catalog=OKW;Persist Security Info=True;User ID=super;Pwd=super"
_PRG_NAME   = 'carga_federado'

def syntax():
    ayuda = u'''\
%s [/rate:[<porcentaje>]] [/huge]
donde:
\t/rate\tIndica el porcentaje de carga a generar con respecto a
\t\tla carga típica. El porcentaje es un número entero de
\t\t1 a 10,000 (sin comas).
\t/huge\tIndica que se generarán notas adicionales en un solo
\t\texpediente a fin de generar un expediente enorme. El
\t\ttamaño por default es 13MB. Si se especifica /rate,
\t\tpuede modificarse el tamaño generado.
''' % _PRG_NAME
    print ayuda.encode('cp1252')

def main():
    print 'Cargando... rate = %r...' % get_ratio()
    with DAOokwDataContext(_CS_OKW) as okw:
        okw.CommandTimeout = _DEFAULT_COMMAND_TIMEOUT
        with DAOSomatomDataContext(_CS_OKW) as somatom:
            somatom.CommandTimeout = _DEFAULT_COMMAND_TIMEOUT

            script = Script(okw, somatom, get_ratio())
            script.procesa()
    print 'listo...'

if __name__ != '__main__':
    _CS_OKW = str(ConfigurationManager.ConnectionStrings['ConnStr'])
#print _CS_OKW

if get_help():
    syntax()
else:
    main()
