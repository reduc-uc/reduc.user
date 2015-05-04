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
class Adapter:
    def __init__(self, entry):
        self.entry = entry


class ObjectClassAdapter(Adapter):
    DEFAULT_VALUES = {}

    @classmethod
    def _isOneObjectClass(cls, entry):
        myName = cls.__name__.lower()
        oc = [x.lower() for x in entry.get('objectClass', [])]
        return myName in oc

    @classmethod
    def _isTheMainClass(cls, entry):
        return False

    def setDefaultValues(self):
        for k, v in self.DEFAULT_VALUES.items():
            if k not in self.entry:
                self.entry[k] = v

    def setDependentValues(self):
        pass


class MainObjectClassAdapter(ObjectClassAdapter):
    DEFAULT_OBJECT_CLASS = []

    def setDn(self):
        raise NotImplemented

    def setObjectClass(self):
        oc = set(self.entry.get('objectClass'))
        oc = oc.union(self.DEFAULT_OBJECT_CLASS)
        self.entry['objectClass'] = list(oc)

    def fileAdapter(self):
        return VoidFileAdapter(self.entry)

    def nameAndSurname(self):
        name = self.entry.first('gn')
        surname = self.entry.first('sn', '')
        return name, surname

    def cryptMethod(self):
        return 'md5'

    def ciKey(self):
        return ''


class StrategyObjectClassAdapter(MainObjectClassAdapter):
    OBJECT_CLASSES = []

    @classmethod
    def setObjectClasses(cls, objectClasses):
        cls.OBJECT_CLASSES = objectClasses

    def __init__(self, entry):
        Adapter.__init__(self, entry)
        self._mainClass = self._getMainClass()

        if not self.entry.get('objectClass'):
            self.setObjectClass()

    def _getMainClass(self):
        for oc in self.OBJECT_CLASSES:
            if oc._isTheMainClass(self.entry):
                return oc(self.entry)
        raise AssertionError('objectClass principal no encontrada')

    def setDefaultValues(self):
        for oc in self.OBJECT_CLASSES:
            if oc._isOneObjectClass():
                oc(self.entry).setDafaultValues()

    def setDependentValues(self):
        self._mainClass.setDependentValues()

    def setDn(self):
        self._mainClass.setDn()

    def setObjectClass(self):
        self._mainClass.setObjectClass()

    def fileAdapter(self):
        return self._mainClass.fileAdapter()

    def cryptMethod(self):
        return self._mainClass.cryptMethod()

    def ciKey(self):
        return self._mainClass.ciKey()


class VoidFileAdapter(Adapter):
    def new_home(self):
        pass

    def modify_home(self, oldEntry):
        pass

    def delete_home(self):
        pass


