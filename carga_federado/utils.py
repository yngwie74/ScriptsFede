#! /env//ipy
# -*- coding: utf-8 -*-

from System import Random, DateTime

from sys import argv

_rand = Random()


def with_trace():
    return ('-t' in argv)


def _get_bool_arg(arg_name):
    args =  [arg for arg in argv if arg == arg_name]
    return not (not args)


def get_ratio():
    ARG_NAME = '/rate:'

    args =  [arg for arg in argv if arg.startswith(ARG_NAME)]
    if len(args):
        try:
            return float(args[-1][len(ARG_NAME):]) / 100
        except:
            pass
    return 1


def get_huge_exp():
    return _get_bool_arg('/huge')


def get_help():
    return _get_bool_arg('/?')


def transac(func):
    def wrapped_f(*args, **kwargs):
        contexto = kwargs['contexto']

        conn = contexto.Connection
        conn.Open()

        tran = conn.BeginTransaction()
        contexto.Transaction = tran

        try:
            result = func(*args, **kwargs)
            tran.Commit();
            return result;

        except Exception:
            if tran:
                tran.Rollback()
            raise

        finally:
            if tran:
                contexto.Transaction = None
    return wrapped_f


def trace(func):
    def wrapped_f(*args, **kwargs):
        print '%s...' % func.__name__
        return func(*args, **kwargs)
    return wrapped_f


def safe_set_prop(o, p, v):
    if hasattr(o, p):
        setattr(o, p, v)


def rand(max):
    return _rand.Next(max)


def getdate():
    return DateTime.Now


def clona(entidad):
    def _es_clonable(prop):
        return prop.isupper() and ('_' in prop) and \
           not ( prop.startswith('C_') or prop.startswith('K_') )

    nueva = entidad.__class__()
    for prop in dir(entidad):
        if _es_clonable(prop):
            valor = getattr(entidad, prop)
            safe_set_prop(nueva, prop, valor)
    return nueva

class LargestList(object):
    def __init__(self, max):
        self._list = []
        self._max = max

    def __getitem__(self, index):
        return self._list[index]

    def __len__(self):
        return len(self._list)

    def _shrink(self):
        if len(self) > self._max:
            self._list = self._list[:self._max]

    def __lshift__(self, other):
        length, data = other
        for i in range(len(self)):
            if self._list[i][0] < length:
                self._list.insert(i, other)
                self._shrink()
                break
        else:
            if len(self) < self._max:
                self._list.append(other)
        return self

    def __iter__(self):
        return iter(self._list)

    def __str__(self):
        return str(self._list)
# end class
