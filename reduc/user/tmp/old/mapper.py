#! /usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010. Jose Dinuncio
# All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License.
#
##############################################################################
from reduc.ldap import filter as _filter

class Mapper:
    MAP = {}

    def __init__(self, dct):
        self.dct = dct

    def __getitem__(self, k):
        key = self.MAP.get(k, k)
        return self.dct[key]

    def __setitem__(self, k, v):
        key = self.MAP.get(k, k)
        self.dct[key] = v


class UserMapper(Mapper):
    DEFAULT = {}

    def __init__(self, entry):
        Mapper.__init__(self, entry)
        self._setDefaults()

    def _setDefaults(self):
        for k, v in self.DEFAULT.items():
            key = self.MAP[k]
            if key not in self.dct:
                self.dct[key] = v

    def update(self):
        raise NotImplementedError()

    def first(self, key, default=None):
        '''Devuelve el primer elemento de self[key]'''
        if default is None:
            v = self[key]
        else:
            v = self.get(key, default)

        if type(v) == list:
            return v[0]
        else:
            return v

    def ciFilter(self):
        key = self.MAP['ci']
        ci = self.first('ci')
        return _filter.Eq(key, ci)

    def fullName(self):
        name = self.first('name1')
        surname = self.first('surname1')
        return '{0} {1}'.format(name, surname)


class OldMapper(UserMapper):
    MAP = dict(
            name1='uceduveNombre1',
            name2='uceduveNombre2',
            surname1='uceduveApellido1',
            surname2='uceduveApellido2',
            dep1='uceduveDependencia1',
            dep2='uceduveDependencia2',
            dep3='uceduveDependencia3',
            dep4='uceduveDependencia4',
            type='uceduveUsuarioTipo',
            ci='uceduveCI',
        )
    DEFAULT = dict()


def NewMapper(UserMapper):
    MAP = dict()
    DEFAULT = dict()
