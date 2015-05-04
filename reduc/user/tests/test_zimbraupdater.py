#! /usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008, RedUC <reduc@uc.edu.ve>
# All Rights Reserved.
#
# LICENCE HERE
#
##############################################################################
import unittest

from  reduc.user.zimbraupdater import zimbraUpdater as updater
from reduc.ldap.ldapuc import Entry


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.entry = Entry(
            gn='Pedro',
            sn='Perez',
            uid='pperez',
            accountClassification='profesor,ingenieria,electrica',
        )


class ZimbraPropertyUpdaterDefaultTest(BaseTest):
    def test_defaults_zimbraMailStatus_set(self):
        '''Test zimbraupdater default 'zimbraMailStatus' added'''
        defaults = updater._defaults(self.entry)
        assert 'zimbraMailStatus' in defaults
        assert defaults['zimbraMailStatus'] == 'enabled'

    def test_defaults_zimbraMailStatus_not_overwrite(self):
        '''Test zimbraupdater default doesn't overwrite a preset value'''
        self.entry['zimbraMailStatus'] = 'blah'
        defaults = updater._defaults(self.entry)
        assert 'zimbraMailStatus' in defaults
        assert defaults['zimbraMailStatus'] == 'blah'


class ZimbraPropertyUpdaterDependentTest(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        self.entry.update(updater._defaults(self.entry))

    def test_dependent_mail_set(self):
        '''Test zimbraupdater dependent 'mail' added'''
        updater._dependents(self.entry)
        assert 'mail' in self.entry
        assert self.entry['mail'] == 'pperez@uc.edu.ve'


