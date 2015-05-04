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
from reduc.user.adapter import Adapter
from reduc.user.filemanager import FileManager

class FileAdapter(Adapter):
    filemanager = FileManager()

    @classmethod
    def setFilemanager(cls, filemanager):
        cls.filemanager = filemanager

    def _path_uid_gid(self, entry=None):
        if not entry:
            entry = self.entry

        path = entry['homeDirectory']
        uid  = entry['uidNumber']
        gid  = entry['gidNumber']
        return path, uid, gid

    def new_home(self):
        path, uid, gid = self._path_uid_gid()
        self.filemanager.new(path, uid, gid)

    def modify_home(self, oldEntry):
        oldpath, _, _ = self._path_uid_gid(oldEntry)
        path, uid, gid = self._path_uid_gid()
        self.filemanager.modify(oldpath, path, uid, gid)

    def delete_home(self):
        path, _, _ = self._path_uid_gid()
        self.filemanager.delete(path)
