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
import datetime


class Helper:
    def __init__(self, objectClasses):
        self.objectClasses = objectClasses

    def _getMainObjectClass(self, entry):
        """
        Devuelve el objectClass principal de una entrada.

        Una entrada solo puede tener un main objectClass que controla
        sus propiedades dependientes.
        """
        for objectClass in self.objectClasses:
            if objectClass.isMainClass(entry):
                return objectClass

    def setObjectClass(self, entry):
        self._getMainObjectClass(entry).setObjectClass(entry)

    def setDn(self, entry):
        self._getMainObjectClass(entry).setDn(entry)

    def setDefaultValues(self, entry):
        for objectClass in self.objectClasses:
            if objectClass.isInEntry(entry):
                objectClass.setDefaultValues(entry)

    def setDependentValues(self, entry):
        self._getMainObjectClass(entry).setDependentValues(entry)

    def hasFilesystem(self, entry):
        return self._getMainObjectClass(entry).HAS_FILESYSTEM

    def ciKey(self, entry):
        return self._getMainObjectClass(entry).CI_KEY

    def cryptMethod(self, entry):
        return self._getMainObjectClass(entry).CRYPT_METHOD


class ObjectClass:
    OBJECT_CLASS = []
    DEFAULT_VALUES = {}

    @classmethod
    def _className(cls):
        name = cls.__name__
        return name[0].lower() + name[1:]

    def isMainClass(self, entry):
        return False

    def isInEntry(self, entry):
        return self._className() in entry.get('objectClass', [])

    def setObjectClass(self, entry):
        entry['objectClass'] = list(set(self.OBJECT_CLASS).union(
            entry.get('objectClass', [])))

    def setDefaultValues(self, entry):
        defaults = dict(**self.DEFAULT_VALUES)
        defaults.update(entry)
        entry.update(defaults)

    def setDn(self, entry):
        pass

    def setDependentValues(self, entry):
        pass


class MainObjectClass(ObjectClass):
    REQUIRED_KEY = ''
    CI_KEY = 'uniqueId'
    CRYPT_METHOD = 'sha1'
    HAS_FILESYSTEM = False

    def _hasRequiredKey(self, entry):
        return self.REQUIRED_KEY in entry

    def isMainClass(self, entry):
        # Este objectClass es main solo si esta en entry
        return self.isInEntry(entry) or self._hasRequiredKey(entry)


class UceduveAccount(MainObjectClass):
    REQUIRED_KEY = 'uceduveNombre1'
    CI_KEY = 'uceduveCI'
    CRYPT_METHOD = 'crypt'
    HAS_FILESYSTEM = False

    OBJECT_CLASS = ['top', 'posixAccount', 'shadowAccount',
            'uceduveAccount', 'uceduveMailAccount', 'uceduveWebAccount']

    DEFAULT_VALUES = dict(
        uceduveUsuarioPrivilegio='0',
        uceduveHost='thor.uc.edu.ve',
        uceduveQuota='12288',
        uceduveQuotaHard='24576',
        uceduveStatus='ok',
        uceduveFechaExpiracion='-',
    )

    def setDn(self, entry):
        uid = entry.first('uid').lower()
        ut = entry.first('uceduveUsuarioTipo')
        d1 = entry.first('uceduveDependencia1')
        d2 = entry.first('uceduveDependencia2')
        entry.dn = 'uid={0},ou={1},ou={2},ou={3},ou=people,dc=uc,dc=edu,dc=ve'.format(
                uid, ut, d2, d1)

    def setDependentValues(self, entry):
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
    def _gidNumber(self, entry):
        ut = entry.first('uceduveUsuarioTipo').lower()
        ub = self._uceduveUsuarioUbicacion(entry).lower()
        return self.INIT_GID + self.GID_UT[ut] + self.GID_UB[ub]

    HASH = 16
    def _homeDirectory(self, entry):
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

    def _uceduveUsuarioUbicacion(self, entry):
        ub = entry.first('uceduveDependencia1').lower()
        return self.UBICACION.get(ub, 'Facultad')

    def _title(self, entry):
        return self._isProfessor(entry) and 'Prof. ' or ''

    def _isProfessor(self, entry):
        return entry.first('uceduveUsuarioTipo', '').lower() == 'profesor'

    def _isStudent(self, entry):
        return entry.first('uceduveUsuarioTipo', '').lower() == 'estudiante'

    def _name(self, entry):
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


class NewUceduveAccount(MainObjectClass):
    def setDependentValues(self, entry):
        self.setZimbraDependentValues(entry)

    def setDn(self, entry):
        uid = entry.first('uid')
        entry.dn = 'uid={0},ou=people,dc=uc,dc=edu,dc=ve'.format(uid)

    def setZimbraDependentValues(self, entry):
        entry['zimbraId'] = ZimbraAccount.zimbraId()
        entry['mail'] = self.mail()
        entry['zimbraMailDeliveryAddress'] = self.mail()
        entry['zimbraHost'] = self.zimbraHost(entry)
        entry['zimbraMailTransport'] = self.zimbraMailTransport(entry)
        #entry['zimbraPasswordModifiedTime'] = \
        #        self.zimbraPasswordModifiedTime()

    def mail(self, entry):
        uid = entry.first('uid')
        return '{0}@uc.edu.ve'

    def zimbraMailTransport(self, entry):
        host = self.zimbraHost(entry)
        return 'lmtp:{0}:7025'.format(host)

    def zimbraHost(self, entry):
        for clasif in self.accountClassification(entry):
            type_ = clasif[0].lower()
            if type_ in ['profesor', 'empleado', 'dependencia']:
                return 'c.correo.uc.edu.ve'
        return 'd.correo.uc.edu.ve'

    def accountClassification(self, entry):
        ac = entry.get('accountClassification', [])
        return [part.split(',') for part in ac]


class UceduveUser(NewUceduveAccount):
    OBJECT_CLASS = ['uceduveUser', 'organizationalPerson',
                    'zimbraAccount', 'amavisAccount']



class UceduveDependency(NewUceduveAccount):
    OBJECT_CLASS = ['uceduveDependency', 'organizationalPerson',
                    'zimbraAccount', 'amavisAccount']


class ZimbraAccount(ObjectClass):
    DEFAULT_VALUES = dict(
            zimbraMailStatus='enabled',
            zimbraAccountStatus='active',
            zimbraPrefTagTreeOpen='TRUE',
            zimbraPrefFolderTreeOpen='TRUE',
            zimbraPrefZimletTreeOpen='FALSE',
            zimbraPrefSearchTreeOpen='TRUE',
            zimbraPrefReadingPaneEnabled='TRUE',
    )

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


class UceduveMailAccount(ObjectClass):
    DEFAULT_VALUES = dict(
        uceduveMailStatus='ok',
        quota='12288',
    )


class UceduveWebAccount(ObjectClass):
    DEFAULT_VALUES = dict(
        uceduveWebStatus='ok',
    )


class UceduveAdminAccount(ObjectClass):
    DEFAULT_VALUES = dict(
        uceduveAdminStatus='ok',
    )


class PosixAccount(ObjectClass):
    DEFAULT_VALUES = dict(
        loginShell='/usr/local/sbin/menu_nat',
    )


class ShadowAccount(ObjectClass):
    DEFAULT_VALUES=dict(
        shadowLastChange='11451',
        shadowMax='99999',
        shadowMin='',
        shadowWarning='7',
        shadowInactive='',
        shadowExpire='',
        shadowFlag='',
    )


class UceduveWebUser(ObjectClass):
    DEFAULT_VALUES={}

class UceduveAdminUser(ObjectClass):
    DEFAULT_VALUES={}

class OrganizationalPerson(ObjectClass):
    DEFAULT_VALUES={}

class OrganizationalUnit(ObjectClass):
    DEFAULT_VALUES={}


def getHelper():
    return Helper([UceduveAccount(), UceduveMailAccount(), UceduveWebAccount(),
            UceduveAdminAccount(), UceduveUser(), UceduveDependency(),
            PosixAccount(), ShadowAccount(),
            ZimbraAccount(),
            OrganizationalPerson(), OrganizationalUnit()])
