# -*- coding: utf-8 -*-

_SCRIPT_CREATE_TABLE = '''-- Crear tabla temporal
CREATE TABLE #tmp_paciente_identificador
  (
     FL_PACIENTE_IDENTICADOR INT NOT NULL
    ,FL_PACIENTE INT NOT NULL
    ,FL_IDENTIFICADOR INT NOT NULL
    ,DS_TEXTO NVARCHAR(50) NOT NULL
    ,FE_CREACION DATETIME NOT NULL
    ,FE_ULTMOD DATETIME NOT NULL
    ,CL_USUARIO NVARCHAR(25) NULL
    ,NB_PROGRAMA NVARCHAR(50) NULL
    ,FG_REPLICADO BIT NOT NULL DEFAULT (1)
  )'''

_SCRIPT_INSERT_TMP = \
    "INSERT INTO #tmp_paciente_identificador (FL_PACIENTE_IDENTICADOR ,FL_PACIENTE ,FL_IDENTIFICADOR ,DS_TEXTO ,FE_CREACION ,FE_ULTMOD ,CL_USUARIO ,NB_PROGRAMA) VALUES (%(fl_paciente_identicador)d ,%(fl_paciente)d ,%(fl_identificador)d ,'%(ds_texto)s' ,'%(fe_creacion)s' ,'%(fe_ultmod)s' ,'%(cl_usuario)s' ,'%(nb_programa)s')"

_SCRIPT_BEGIN_TRAN = '''BEGIN TRAN Homologar_Idents

-- Borrar registros que se van a actualizar'''

_SCRIPT_DELETE_ANT = \
    'DELETE FROM okw.K_PACIENTE_IDENTIFICADOR WHERE FL_PACIENTE_IDENTICADOR = %(fl_paciente_identicador)d and FL_PACIENTE=%(fl_paciente)d and FL_IDENTIFICADOR=%(fl_identificador)d'

_SCRIPT_INSERT_NVO = '''

-- Re-insertar registros cambiados
SET IDENTITY_INSERT OKW.K_PACIENTE_IDENTIFICADOR ON

INSERT INTO OKW.K_PACIENTE_IDENTIFICADOR
           (FL_PACIENTE_IDENTICADOR
           ,FL_PACIENTE
           ,FL_IDENTIFICADOR
           ,DS_TEXTO
           ,FE_CREACION
           ,FE_ULTMOD
           ,CL_USUARIO
           ,NB_PROGRAMA
           ,FG_REPLICADO)
     SELECT FL_PACIENTE_IDENTICADOR
           ,FL_PACIENTE
           ,FL_IDENTIFICADOR
           ,DS_TEXTO
           ,FE_CREACION
           ,FE_ULTMOD
           ,CL_USUARIO
           ,NB_PROGRAMA
           ,FG_REPLICADO
       FROM #tmp_paciente_identificador

SET IDENTITY_INSERT OKW.K_PACIENTE_IDENTIFICADOR OFF'''

_SCRIPT_COMMIT_TRAN = 'COMMIT TRAN Homologar_Idents'

_SCRIPT_DROP_TABLE = 'DROP TABLE #tmp_paciente_identificador'


def auto_generate(f):

    def _wrap(self, *args, **kwds):
        ret = f(self, *args, **kwds)

        if len(self) >= self.slice_size:
            self._generate()
        return ret

    return _wrap


class ScriptGen(object):

    def __init__(self, name, slice_size=500):
        self.fname_fmt = '%s_%%03d.sql' % name
        self.slice_size = slice_size
        self.cur_slice = 1
        self.to_synch = {}
        self.to_insert = []
        self.file = None

    @property
    def fname(self):
        return self.fname_fmt % self.cur_slice

    @auto_generate
    def addInserts(self, identificador):
        self.to_insert.extend(identificador)

    @auto_generate
    def addSynch(self, folio_org, identificador):
        self.to_synch[folio_org] = identificador

    def __len__(self):
        return len(self.to_synch) + len(self.to_insert)

    def _writeln(self, fmt, *args, **kwds):
        line = fmt % (kwds if kwds else tuple(args))
        self.file.write('%s\n' % line)

    def _createTempTable(self):
        self._writeln(_SCRIPT_CREATE_TABLE)

    def _insertIntoTempTable(self, idents, header):
        _FMT = 'yyyyMMdd HH:mm:ss.fff'

        if header:
            self._writeln(header)

        for p in idents:
            self._writeln(
                _SCRIPT_INSERT_TMP,
                fl_paciente_identicador=p.FL_PACIENTE_IDENTICADOR,
                fl_paciente=p.FL_PACIENTE,
                fl_identificador=p.FL_IDENTIFICADOR,
                ds_texto=p.DS_TEXTO,
                fe_creacion=p.FE_CREACION.ToString(_FMT),
                fe_ultmod=p.FE_ULTMOD.ToString(_FMT),
                cl_usuario=p.CL_USUARIO,
                nb_programa=p.NB_PROGRAMA,
                )

    def _populateTempTable(self):
        self._insertIntoTempTable(self.to_synch.itervalues(),
            '-- Insertar registros que se van a actualizar')
        self._insertIntoTempTable(self.to_insert,
            '-- Insertar registros de federado que faltan localmente')

    def _beginTransaction(self):
        self._writeln(_SCRIPT_BEGIN_TRAN)

    def _deleteOldRecords(self):
        for (f, p) in self.to_synch.iteritems():
            self._writeln(
                _SCRIPT_DELETE_ANT,
                fl_paciente_identicador=f,
                fl_paciente=p.FL_PACIENTE,
                fl_identificador=p.FL_IDENTIFICADOR,
                )

    def _insertNewRecords(self):
        self._writeln(_SCRIPT_INSERT_NVO)

    def _commitTransaction(self):
        self._writeln(_SCRIPT_COMMIT_TRAN)

    def _dropTempTable(self):
        self._writeln(_SCRIPT_DROP_TABLE)

    def _useOkw(self):
        self._writeln('USE OKW')
        self._writeln('')

    def _generate_slice(self):
        with open(self.fname, 'w') as self.file:
            self._useOkw()
            self._createTempTable()
            self._populateTempTable()
            self._beginTransaction()
            self._deleteOldRecords()
            self._insertNewRecords()
            self._commitTransaction()
            self._dropTempTable()

    def _clear(self):
        self.to_synch = {}
        self.to_insert = []

    def _generate(self):
        self._generate_slice()
        self._clear()
        self.cur_slice += 1

    def done(self):
        if len(self):
            self._generate()
