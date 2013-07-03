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

from reduc.user.updater import Updater


def cn(entry):
    gn = entry.first('gn', entry.first('givenName', ''))
    sn = entry.first('sn', entry.first('surname', ''))
    return '{0} {1}'.format(gn, sn)

def mail(entry):
    uid = entry.first('uid')
    return '{0}@uc.edu.ve'.format(uid)

def zimbraMailDeliveryAddress(entry):
    return mail(entry)

B_HOST = 'b.correo.uc.edu.ve'
C_HOST = 'c.correo.uc.edu.ve'
D_HOST = 'd.correo.uc.edu.ve'
E_HOST = 'e.correo.uc.edu.ve'
F_HOST = 'f.correo.uc.edu.ve'

MAILHOST_FROM_STUDENT_DEPENDENCY = {
    'derecho'     : D_HOST,
    'direccionsuperior' : C_HOST,
    'educacion'   : D_HOST,
    'externo'     : C_HOST,
    'faces'       : B_HOST,
    'facesna'     : B_HOST,
    'facyt'       : D_HOST,
    'fcs'         : B_HOST,
    'fcsna'       : B_HOST,
    'fundacion'   : C_HOST,
    'ingenieria'  : C_HOST,
    'odontologia' : D_HOST,
    'postgrado'   : B_HOST,
}

def zimbraMailHost(entry):
    type_, dep1, _ = _accountClassification(entry)
    if type_ <> 'estudiante':
        return C_HOST
    return MAILHOST_FROM_STUDENT_DEPENDENCY.get(dep1, 'd.correo.uc.edu.ve')

def zimbraMailTransport(entry):
    mailhost = zimbraMailHost(entry)
    return 'lmtp:{0}:7025'.format(mailhost)

def _accountClassification(entry):
    act = entry.first('accountClassification',
            'clasificame,clasificame,clasificame')
    return [x.lower() for x in act.split(',')]


DAFAULT_OBJECT_CLASS = ['organizationalPerson',
                        'zimbraAccount',
                        'amavisAccount',
                        'uceduveUser']

DEFAULT_VALUES = dict(
    zimbraAccount = dict(
        zimbraMailStatus = 'enabled',
        zimbraAccountStatus = 'active',
        zimbraPrefTagTreeOpen = 'TRUE',
        zimbraPrefFolderTreeOpen = 'TRUE',
        zimbraPrefZimletTreeOpen = 'FALSE',
        zimbraPrefSearchTreeOpen = 'TRUE',
        zimbraPrefReadingPaneEnabled = 'TRUE',
        ),
    )

DEPENDENT_VALUES = dict(
    zimbraAccount = dict(
        cn = cn,
        mail = mail,
        zimbraMailDeliveryAddress = zimbraMailDeliveryAddress,
        zimbraMailHost = zimbraMailHost,
        zimbraMailTransport = zimbraMailTransport,
        ),
    )

zimbraUpdater = Updater(DAFAULT_OBJECT_CLASS, DEFAULT_VALUES, DEPENDENT_VALUES)
