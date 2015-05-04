#! /usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008, RedUC
# All Rights Reserved.
#
##############################################################################
'''
Acciones sobre el sistema de archivos por el Manejo de Usuarios.

El manejo de usuarios requiere la creacion de home directories, su movimiento,
cambio de permisología y de dueños. Este modulo define todas esas acciones.
'''
import os.path
import commands

class FileManager:
    '''Manejador del sistema de archivos'''
    def __init__(self, skel='/reduc/etc/skel',
                       base_dir='/home',
                       trash_dir='/tmp/trash',
                       min_depth=6,
                       max_depth=7):
        self.skel = skel
        self.base_dir = base_dir
        self.trash_dir = trash_dir
        self.min_depth = min_depth
        self.max_depth = max_depth

    def new(self, path, uid, gid, skel=''):
        '''Crea un nuevo home para el usuario'''
        if not skel:
            skel = self.skel
        path = self._fix_path(path)
        self._exists_path(path, False)
        self._create_parent(path)
        self._exec('cp -r %s %s' % (skel, path))
        self._exec('chown %s.%s %s -R' % (uid, gid, path))

    def modify(self, oldpath, newpath, uid=-1, gid=-1):
        '''Modifica el home del usuario'''
        oldpath = self._fix_path(oldpath)
        newpath = self._fix_path(newpath)
        if oldpath <> newpath:
            self._exists_path(oldpath, True)
            self._exists_path(newpath, False)
            self._create_parent(newpath)
            self._exec('mv %s %s' % (oldpath, newpath))
        self._exec('chown %s.%s %s -R' % (uid, gid, newpath))

    def delete(self, path):
        '''Borra el home del usuario'''
        path = self._fix_path(path)
        if os.path.exists(path):
            self._exec('mkdir -p %s' % self.trash_dir)
            # TODO: Renombrar el directorio para hacerlo unico
            self._exec('mv %s %s' % (path, self.trash_dir))

    def _create_parent(self, path):
        '''Crea el directorio padre de path'''
        path = os.path.dirname(os.path.abspath(path))
        self._exec('mkdir -p %s' % path)


    def _fix_path(self, path):
        '''Verifica que el path dado sea sano y lo devuelve regularizado'''
        apath = os.path.abspath(path)
        if not apath.startswith(self.base_dir):
            raise RuntimeError("Home '%s' fuera de '%s'" % (apath,
                                                             self.base_dir))
        depth = len(apath.split('/'))
        if depth < self.min_depth or depth > self.max_depth:
            raise RuntimeError('Intento crear un home en la profundidad '
                                'errada')
        return apath

    def _exists_path(self, path, b):
        '''Chequea que el path exista o no o arroja una excepcion'''
        e = os.path.exists(path)
        if e == b:
            return
        if e:
            # El path existe y no deberia
            raise RuntimeError("'%s' existe" % path)
        else:
            # El path no existe y deberia
            raise RuntimeError("'%s' no existe" % path)

    def _exec(self, cmd):
        '''Ejecuta un comando por consola'''
        stat, output = commands.getstatusoutput(cmd)
        if stat:
            raise RuntimeError(output)


