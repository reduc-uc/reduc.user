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
import unittest
from reduc.user.mapper import Helper, ObjectClass

class THelper(Helper):
    MAP = dict(
            map_a='base_a',
            map_b='base_b',
            map_c='base_c',
        )

class TObjectClass(ObjectClass):
    MAP = THelper.MAP
    DEFAULT = dict(
            map_b='default b',
            map_c='default c',
    )

class TestHelper(unittest.TestCase):
    '''Test sobre Helper'''
    def setUp(self):
        self.base = dict(
                base_a='original a',
                base_b='original b',
            )
        self.mapped = THelper(self.base)

    def test_get_map(self):
        'Lectura del mapeo'
        assert self.mapped['map_a'] == 'original a'

    def test_set_maps_map(self):
        'Escritura en mapeo (chequeo en el mapa)'
        self.mapped['map_a'] = 'nuevo valor'
        assert self.mapped['map_a'] == 'nuevo valor'

    def test_set_maps_base(self):
        'Escritura en mapeo (chequeo en el original)'
        self.mapped['map_a'] = 'nuevo valor'
        assert self.base['base_a'] == 'nuevo valor'


class TestObjectClass(unittest.TestCase):
    '''Test sobre ObjectClass'''
    def setUp(self):
        self.base = dict(
                base_a='original a',
                base_b='original b',
            )
        self.mapped = TObjectClass(self.base)

    def test_default_new_map(self):
        'Lectura de valores por defecto nuevos (en el mapa)'
        assert self.mapped['map_c'] == 'default c'

    def test_default_new_base(self):
        'Lectura de valores por defecto nuevos (en el original)'
        assert self.base['base_c'] == 'default c'

    def test_default_old_map(self):
        'Lectura de valores por defecto existentes (en el mapa)'
        assert self.mapped['map_b'] == 'original b'


if __name__ == '__main__':
    unittest.main()
