#! /usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012. RedUC
# All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License.
#
##############################################################################
from reduc.ldap import Entry


class Updater:

    def __init__(self, default_objectClass, default_values, dependent_values):
        self.default_objectClass = default_objectClass
        self.default_values = default_values
        self.dependent_values = dependent_values

    def update(self, entry):
        nentry = self._set_update(entry)
        entry.update(nentry)
        self._update_dn(entry)

    def _set_update(self, entry):
        nentry = self._defaults(entry)
        self._dependents(nentry)
        return nentry

    def _defaults(self, entry):
        # Obtenemos el objectClass del entry o su valor por defecto
        objectClass = entry.get('objectClass') or self.default_objectClass
        default = Entry(objectClass=objectClass)

        for oc in objectClass:
            default.update(self.default_values.get(oc, {}))

        default.update(entry)
        return default

    def _dependents(self, entry):
        '''Modifica entry con los valores de los campos dependientes'''
        objectClass = entry['objectClass']

        for oc, methods in self.dependent_values.items():
            if oc in objectClass:
                for method_name, method in methods.items():
                    entry[method_name] = method(entry)

    def _update_dn(self, entry):
        uid = entry.first('uid')
        entry.dn = 'uid={0},ou=people,dc=uc,dc=edu,dc=ve'.format(uid)


