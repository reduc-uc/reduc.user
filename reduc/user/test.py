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
from reduc.user.command import User, Entry

test = Entry(
    uid='test201203',
    gn='testio',
    sn='probamus',
    uniqueIdentifier='V11555444',
)

user = User('ldap://c.correo.uc.edu.ve', 'dc=uc,dc=edu,dc=ve',
            'cn=config', 'pcd1edrxl')
print user.new(test)

