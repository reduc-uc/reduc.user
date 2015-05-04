#! /usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012, RedUC <reduc@uc.edu.ve>
# All Rights Reserved.
#
# LICENCE HERE
#
##############################################################################
import unittest
import time

import reduc.user.zimbraupdater as z
from reduc.ldap.ldapuc import Entry

class ZimbraPropertyTest(unittest.TestCase):
    def setUp(self):
        self.entry = Entry(
            gn='Pedro',
            sn='Perez',
            uid='pperez',
            accountClassification='profesor,ingenieria,electrica',
        )
        self.now = time.mktime((2012, 3, 15, 9, 55, 30, 3, 75, 0))
   
    ## Propiedades aisladas

    def test_email(self):
        '''Test zimbraupdater 'mail' property'''
        assert z.mail(self.entry) == 'pperez@uc.edu.ve'
        
    def test_zimbraMailDeliveryAddress(self):
        '''Test zimbraupdater 'zimbraMailDeliveryAddress' property'''
        assert z.zimbraMailDeliveryAddress(self.entry) == 'pperez@uc.edu.ve'

    def test_zimbraId(self):
        '''Test zimbraupdater 'zimbraId' property'''
        assert z.zimbraId(self.entry, self.now) == \
                '20120315-07503-1425-3000-50d8a3ffa900'

    def test_zimbraMailTransport(self):
        '''Test zimbraupdater 'zimbraMailTransport' property for professors'''
        assert z.zimbraMailTransport(self.entry) == \
                'lmtp:{0}:7025'.format(z.C_HOST)
        
    def test_zimbraMailHost_profesor(self):
        '''Test zimbraupdater 'zimbraMailHost' property for professors'''
        assert z.zimbraMailHost(self.entry) == z.C_HOST
        
    def test_zimbraMailHost_empleado(self):
        '''Test zimbraupdater 'zimbraMailHost' property for employees'''
        self.entry['accountClassification'] = 'empleado,ingenieria,electrica'
        assert z.zimbraMailHost(self.entry) == z.C_HOST
        
    def test_zimbraMailHost_dependencia(self):
        '''Test zimbraupdater 'zimbraMailHost' property for dependencies'''
        self.entry['accountClassification'] = 'dependencia,ingenieria,electrica'
        assert z.zimbraMailHost(self.entry) == z.C_HOST
        
    def test_zimbraMailHost_estudiante_postgrado(self):
        '''Test zimbraupdater 'zimbraMailHost' property for postgrad students'''
        self.entry['accountClassification'] = 'estudiante,postgrado,electrica'
        assert z.zimbraMailHost(self.entry) == z.C_HOST
        
    def test_zimbraMailHost_estudiante_ingenieria(self):
        '''Test zimbraupdater 'zimbraMailHost' property for engineer students'''
        self.entry['accountClassification'] = 'estudiante,ingenieria,electrica'
        assert z.zimbraMailHost(self.entry) == z.D_HOST
        
    def test_zimbraMailHost_estudiante_odontologia(self):
        '''Test zimbraupdater 'zimbraMailHost' property for odontology students'''
        self.entry['accountClassification'] = 'estudiante,odontologia,electrica'
        assert z.zimbraMailHost(self.entry) == z.E_HOST
        
    def test_zimbraMailHost_estudiante_faces(self):
        '''Test zimbraupdater 'zimbraMailHost' property for faces students'''
        self.entry['accountClassification'] = 'estudiante,faces,electrica'
        assert z.zimbraMailHost(self.entry) == z.F_HOST
        
