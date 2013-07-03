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
import time
import string
from reduc.ldap import Ldap, Entry, filter as _filter
from reduc.crypt import Crypt
from reduc.user.zimbraupdater import zimbraUpdater


class Command:
    def __init__(self, db, updater=None):
        self.db = db
        self.updater = updater or zimbraUpdater

    def __call__(self, *args, **kargs):
        raise NotImplemented()

    def _update(self, entry):
        self.updater.update(entry)

    def _password(self, pwd='', salt='', encode=True):
        return Crypt.encode(pwd, salt, method='sha', encode=encode)

    def _is_free(self, key, val):
        '''True si no hay entradas con key=val'''
        filter = _filter.Eq(key, val)
        result = self.db.find(filter)
        return not result

    def _verify_free(self, key, newEntry, oldEntry=None):
        '''False si key ha cambiado y ya esta utilizada'''
        if not self._has_changed(key, oldEntry, newEntry):
            return

        val = newEntry.first(key)
        filter = _filter.Eq(key, val)
        result = self.db.find(filter)
        if not result:
            return

        msg = "El campo '{0}'='{1}' le pertenece al usuario {2}"
        uid = result.first('uid', '???')
        raise AssertionError(msg.format(key, val, uid))

    def _has_changed(self, key, oldEntry, newEntry):
        #hack: usamos self en oldEntry.first(key, self) para que en caso
        # de que key no este en oldEntry devolver un valor que asegure
        # que la comparacion <> sea exitosa
        if oldEntry is None:
            return True

        return ((key in newEntry) and
                (newEntry.first(key) <> oldEntry.first(key, self)))


class New(Command):
    def __call__(self, dct):
        entry = Entry(dn='', **dct)
        self._new_values(entry)
        self._update(entry)
        self._verify(entry)
        self.db.add(entry)
        return entry

    def _new_values(self, entry):
        if not entry.first('uid', ''):
            entry['uid'] = self._new_uid(entry).lower()
        if not entry.first('userPassword', ''):
            entry['userPassword'] = self._password()
        if not entry.first('zimbraId', ''):
            entry['zimbraId'] = self._new_zimbraId()

    def _verify(self, entry):
        self._verify_free('uid', entry)
        self._verify_free('uniqueIdentifier', entry)

    def _new_uid(self, entry):
        base_uid = self._base_uid(entry)
        uids = [base_uid] + [base_uid + str(x) for x in range(1,1000)]

        for uid in uids:
            if self._is_free('uid', uid):
                return uid

        raise AssertionError('Nos quedamos sin nombres!')

    def _base_uid(self, entry):
        gn = entry.first('gn', '') or entry.first('givenName', '')
        sn = entry.first('sn', '') or entry.first('surname', '')
        base_uid = (gn[0] if len(gn) else '') + sn
        return base_uid

    def _new_zimbraId(self, now=None):
        now = now or time.time()
        (tm_year, tm_mon, tm_mday, tm_hour, tm_min,tm_sec,
         tm_wday, tm_yday, tm_isdst) = time.gmtime(now)
        tm_msec = int(now*100) % 100
        last = hex(int(now*10**7))[-12:]
        format = '%04i%02i%02i-%03i%02i-%02i%02i-%02i%02i-%12s'
        zid = format % (tm_year, tm_mon, tm_mday,
                        tm_yday, tm_wday,
                        tm_hour, tm_min,
                        tm_sec, tm_msec,
                        last)
        return zid


class Modify(Command):
    def __call__(self, oldEntry, dct):
        newEntry = self._new_entry(oldEntry, dct)
        #import pdb; pdb.set_trace()
        self._verify(oldEntry, newEntry)
        self.db.modify(oldEntry, newEntry)
        return newEntry

    def _new_entry(self, entry, dct):
        newEntry = entry.clone()
        newEntry.update(dct)
        self._update(newEntry)
        return newEntry

    def _verify(self, oldEntry, newEntry):
        self._verify_free('uid', newEntry, oldEntry)
        self._verify_free('uniqueIdentifier', newEntry, oldEntry)


class Password(Command):
    MINIMUM_LENGHT = 8
    MINIMUM_COMPLEXITY = 2
    COMPLEXITY_LENGHT = 10
    ALLOWED_SYMBOLS = ''  #TODO
    ALLOWED_CHARS = string.letters + string.digits + ALLOWED_SYMBOLS

    def __call__(self, entry, pwd='', salt='',  encode=True):
        if encode and pwd:
            # pwd debe ser verificado si va a ser codificado y no es ''
            self._verify(pwd)
        newEntry = entry.clone()
        newEntry['userPassword'] = self._password(pwd, salt, encode)
        self.db.modify(entry, newEntry)
        return newEntry

    @classmethod
    def _verify(cls, pwd):
        if len(pwd) < cls.MINIMUM_LENGHT:
            raise PasswordException(
                'El password tiene menos de {0} caracteres'.format(
                    cls.MINIMUM_LENGHT))
        if cls._complexity(pwd) < cls.MINIMUM_COMPLEXITY:
            raise PasswordException(
                'El password debe tener al menos {0} tipos de caracteres'.format(
                    cls.MINIMUM_COMPLEXITY))
        invalid_chars = cls._invalid_password_chars(pwd)
        if invalid_chars:
            raise PasswordException(
                'El password tiene caracteres invalidos: "{0}"'.format(
                    invalid_chars))

    @classmethod
    def _complexity(cls, pwd):
        c = 0
        c = c + any(x.islower() for x in pwd)
        c = c + any(x.isupper() for x in pwd)
        c = c + any(x.isdigit() for x in pwd)
        c = c + any(x in cls.ALLOWED_SYMBOLS for x in pwd)
        c = c + (len(pwd) > cls.COMPLEXITY_LENGHT)
        return c

    @classmethod
    def _invalid_password_chars(cls, pwd):
        return [x for x in pwd if x not in cls.ALLOWED_CHARS]


class Search(Command):
    def __call__(self, filter):
        return self.db.search(filter)


class Delete(Command):
    def __call__(self, entry):
        self.db.delete(entry)
        return entry


class CommandException(Exception):
    '''Raiz de las excepciones arrojadas por los comandos'''
    def __init__(self, message):
        self.message = message

class PasswordException(CommandException):
   '''Error al cambiar el password'''


class User:
    def __init__(self, uri, base_dn, root_dn='', root_pwd='', updater=None):
        self.db = Ldap(uri, base_dn, root_dn, root_pwd)
        self.updater = updater or zimbraUpdater

        self.new = New(self.db, self.updater)
        self.modify = Modify(self.db, self.updater)
        self.password = Password(self.db, self.updater)
        self.search = Search(self.db, self.updater)
        self.delete = Delete(self.db, self.updater)

