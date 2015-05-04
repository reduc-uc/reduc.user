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
from reduc.user.adapter import ObjectClassAdapter, MainObjectClassAdapter
from reduc.user.adapter import StrategyObjectClassAdapter
from reduc.user.fileadapter import FileAdapter, VoidFileAdapter

class UceduveAccount(MainObjectClassAdapter):
    DEFAULT_OBJECT_CLASS = ['top', 'posixAccount', 'shadowAccount',
            'uceduveAccount', 'uceduveMailAccount', 'uceduveWebAccount']

    DEFAULT_VALUES = dict(
        uceduveUsuarioPrivilegio='0',
        uceduveHost='thor.uc.edu.ve',
        uceduveQuota='12288',
        uceduveQuotaHard='24576',
        uceduveStatus='ok',
        uceduveFechaExpiracion='-',
    )

    #FILE_ADAPTER = FileAdapter()
    FILE_ADAPTER = VoidFileAdapter

    @classmethod
    def setFileAdapter(cls, fileAdapter):
        cls.FILE_ADAPTER = fileAdapter

    @classmethod
    def _isTheMainClass(cls, entry):
        return 'uceduveNombre1' in entry

    def setDn(self):
        entry = self.entry
        uid = entry.first('uid').lower()
        ut = entry.first('uceduveUsuarioTipo')
        d1 = entry.first('uceduveDependencia1')
        d2 = entry.first('uceduveDependencia2')
        entry.dn = 'uid={0},ou={1},ou={2},ou={3},ou=people,dc=uc,dc=edu,dc=ve'.format(
                uid, ut, d2, d1)

    def setDependentValues(self):
        entry = self.entry
        entry['gidNumber'] = self._gidNumber(entry)
        entry['homeDirectory'] = self._homeDirectory(entry)
        entry['uceduveTitulo'] = self._title(entry)
        entry['uceduveFechaCreacion'] = self._uceduveFechaCreacion()
        entry['uceduveUsuarioUbicacion'] = self._uceduveUsuarioUbicacion(entry)

        # posixAccoun
        title = self._title(entry)
        name = self._name(entry)
        entry['cn'] = '{0}{1}'.format(title, name)
        entry['gecos'] = entry['cn']

        # uceduveMailAccount
        uid = entry.first('uid')
        entry['mail'] = '{0}@uc.edu.ve'.format(uid)
        entry['maildrop'] = '{0}@thor.uc.edu.ve'.format(uid)

    def fileAdapter(self):
        return self.FILE_ADAPTER(entry)

    def nameAndSurname(self):
        name = self.entry['uceduveNombre1']
        surname = self.entry['uceduveApellido1']
        return name, surname

    def cryptMethod(self):
        return 'crypt'

    def ciKey(self):
        return 'uceduveCI'

    GID_UT = {
        'otro'              :   0,
        'profesor'          : 100,
        'estudiante'        : 200,
        'empleado'          : 300,
        'dependencia'       : 400
    }

    GID_UB = {
        'otro'              :   0,
        'facultad'          :  10,
        'direccionsuperior' :  10,
        'fundacion'         :  30,
        'externo'           :  40
    }

    INIT_GID = 1000
    def _gidNumber(self):
        entry = self.entry
        ut = entry.first('uceduveUsuarioTipo').lower()
        ub = self._uceduveUsuarioUbicacion(entry).lower()
        return self.INIT_GID + self.GID_UT[ut] + self.GID_UB[ub]

    HASH = 16
    def _homeDirectory(self):
        entry = self.entry
        d1 = self._uncapitalize(entry.first('uceduveDependencia1'))
        d2 = self._uncapitalize(entry.first('uceduveDependencia2'))
        ut = entry.first('uceduveUsuarioTipo').lower()
        uid = entry.first('uid').lower()
        un = entry.first('uidNumber')
        hash = ''

        if self._isStudent(entry):
            hash = str(int(un) % self.HASH) + '/'

        return '/home/{0}/{1}/{2}/{3}{4}'.format(d1, d2, ut, hash, uid)

    def _uceduveFechaCreacion(self):
        today = datetime.date.today()
        return '{0}/{1:02}/{2:02}'.format(today.year, today.month, today.day)

    UBICACION = dict(direccionsuperior='DireccionSuperior',
            fundacion='Fundacion',
            externo='Externo')

    def _uceduveUsuarioUbicacion(self):
        entry = self.entry
        ub = entry.first('uceduveDependencia1').lower()
        return self.UBICACION.get(ub, 'Facultad')

    def _title(self):
        entry = self.entry
        return self._isProfessor(entry) and 'Prof. ' or ''

    def _isProfessor(self):
        entry = self.entry
        return entry.first('uceduveUsuarioTipo', '').lower() == 'profesor'

    def _isStudent(self):
        entry = self.entry
        return entry.first('uceduveUsuarioTipo', '').lower() == 'estudiante'

    def _name(self):
        entry = self.entry
        nom1 = entry.first('uceduveNombre1')
        nom2 = 'uceduveNombre2' in entry and (entry.first('uceduveNombre2') + '') or ''
        ape1 = entry.first('uceduveApellido1')
        ape2 = entry.first('uceduveApellido2', '')
        return '{0} {1}{2} {3}'.format(nom1, nom2, ape1, ape2)

    def _uncapitalize(self, strn):
        if strn[0].isupper and strn[1].isupper():
            r = strn.lower()
        else:
            r = strn[0].lower() + strn[1:]
        return r
    pass


class NewUceduveAccount(MainObjectClassAdapter):
    def setDn(self):
        uid = self.entry.first('uid')
        entry.dn = 'uid={0},ou=people,dc=uc,dc=edu,dc=ve'.format(uid)

    def setDependentValues(self):
        entry = self.entry
        entry['zimbraId'] = ZimbraAccount.zimbraId()
        entry['mail'] = self.mail()
        entry['zimbraMailDeliveryAddress'] = self.mail()
        entry['zimbraHost'] = self.zimbraHost(entry)
        entry['zimbraMailTransport'] = self.zimbraMailTransport(entry)
        #entry['zimbraPasswordModifiedTime'] = \
        #        self.zimbraPasswordModifiedTime()

    def mail(self):
        uid = self.entry.first('uid')
        return '{0}@uc.edu.ve'

    def zimbraMailTransport(self):
        host = self.zimbraHost(self.entry)
        return 'lmtp:{0}:7025'.format(host)

    def zimbraHost(self):
        for clasif in self.accountClassification(self.entry):
            type_ = clasif[0].lower()
            if type_ in ['profesor', 'empleado', 'dependencia']:
                return 'c.correo.uc.edu.ve'
        return 'd.correo.uc.edu.ve'

    def accountClassification(self):
        ac = self.entry.get('accountClassification', [])
        return [part.split(',') for part in ac]



class UceduveUser(MainObjectClassAdapter):
    DEFAULT_OBJECT_CLASS = ['uceduveUser', 'organizationalPerson',
                    'zimbraAccount', 'amavisAccount']

    @classmethod
    def _isTheMainClass(cls, entry):
        sn = ('sn' in entry) or ('surname' in entry)
        gn = ('gn' in entry) or ('givenname' in entry)
        return sn and gn

    def ciKey(self):
        return 'uniqueIdentifier'


class UceduveDependency(MainObjectClassAdapter):
    DEFAULT_OBJECT_CLASS = ['uceduveDependency', 'organizationalPerson',
                    'zimbraAccount', 'amavisAccount']

    @classmethod
    def _isTheMainClass(cls, entry):
        sn = ('sn' in entry) or ('surname' in entry)
        gn = ('gn' in entry) or ('givenname' in entry)
        return sn and not gn


# Clases nuevas secundarias
class ZimbraAccount(ObjectClassAdapter):
    DEFAULT_VALUES = dict(
            zimbraMailStatus='enabled',
            zimbraAccountStatus='active',
            zimbraPrefTagTreeOpen='TRUE',
            zimbraPrefFolderTreeOpen='TRUE',
            zimbraPrefZimletTreeOpen='FALSE',
            zimbraPrefSearchTreeOpen='TRUE',
            zimbraPrefReadingPaneEnabled='TRUE',
    )

    def setDependentValues(self):
        self.entry['zimbraId'] = ZimbraAccount.zimbraId()

    @staticmethod
    def zimbraId():
        now = time.time()
        (tm_year, tm_mon, tm_mday,
         tm_hour, tm_min,tm_sec,
         tm_wday, tm_yday, tm_isdst) = time.gmtime(now)
        tm_msec = int(now*100) % 100
        last = hex(int(now*10**7))[-12:]
        format = '%04i%02i%02i-%03i%02i-%02i%02i-%02i%02i-%12s'
        return format % (tm_year, tm_mon, tm_mday,
                        tm_yday, tm_wday,
                        tm_hour, tm_min,
                        tm_sec, tm_msec,
                        last)

    @staticmethod
    def zimbraPasswordModifiedTime():
        return None


class UceduveWebUser(ObjectClassAdapter):
    DEFAULT_VALUES={}


class UceduveAdminUser(ObjectClassAdapter):
    DEFAULT_VALUES={}


class OrganizationalPerson(ObjectClassAdapter):
    DEFAULT_VALUES={}


class OrganizationalUnit(ObjectClassAdapter):
    DEFAULT_VALUES={}


# clases viejas secundarias
class UceduveMailAccount(ObjectClassAdapter):
    DEFAULT_VALUES = dict(
        uceduveMailStatus='ok',
        quota='12288',
    )


class UceduveWebAccount(ObjectClassAdapter):
    DEFAULT_VALUES = dict(
        uceduveWebStatus='ok',
    )


class UceduveAdminAccount(ObjectClassAdapter):
    DEFAULT_VALUES = dict(
        uceduveAdminStatus='ok',
    )


class PosixAccount(ObjectClassAdapter):
    DEFAULT_VALUES = dict(
        loginShell='/usr/local/sbin/menu_nat',
    )


class ShadowAccount(ObjectClassAdapter):
    DEFAULT_VALUES=dict(
        shadowLastChange='11451',
        shadowMax='99999',
        shadowMin='',
        shadowWarning='7',
        shadowInactive='',
        shadowExpire='',
        shadowFlag='',
    )


def getObjectClassFactory():
    adapter = StrategyObjectClassAdapter
    classes = [UceduveAccount, UceduveUser, UceduveDependency,
               UceduveMailAccount, UceduveWebAccount, UceduveAdminAccount,
               PosixAccount, ShadowAccount,
               ZimbraAccount]
    adapter.setObjectClasses(classes)
    return adapter
