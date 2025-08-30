# -*- Mode: Python; python-indent-offset: 4 -*-
#
# Time-stamp: <2022-10-10 16:20:01 alex>
#
# pylint: enable=R0801


"""
SOLIDserver NOM folder

"""

import binascii
import ipaddress
import logging
import re
import time

from packaging.version import Version, parse
from SOLIDserverRest.Exception import (SDSError, SDSInitError)

from .class_params import ClassParams
from .space import Space


class NomFolder(ClassParams):
    """ class to manipulate the SOLIDserver Network Object Manager folder """

    # -------------------------------------
    def __init__(self, sds=None,  # pylint: enable=too-many-arguments
                 name=None,
                 parent=None,
                 class_params=None):
        """init a NOM folder object:
        - sds: object SOLIDserver, could be set afterwards
        """

        self.clean_params()

        super().__init__(sds, name)
        # self.set_sds(sds)

        if parent:
            self.set_parent(parent)

        if class_params is not None:
            self.set_class_params(class_params)

    # -------------------------------------
    def clean_params(self):
        """ clean the object params """
        super().clean_params()

        self.space = None
        self.parent = None

    # -------------------------------------
    def set_parent(self, parent):
        """ set a parent folder for this subfolder """
        if parent and not isinstance(parent, NomFolder):
            raise SDSError(
                message=f"parent folder {parent} not of type NomFolder")

        self.parent = parent

    # -------------------------------------

    def create(self):
        """ create the folder """

        if self.sds is None:
            raise SDSError(message="not connected")

        # if object already created
        if self.myid > 0:
            return

        params = {
            **self.additional_params
        }

        if self.name is not None:
            params['nomfolder_name'] = self.name
        else:
            raise SDSInitError(message="missing name to NOM folder")

        if self.parent:
            params['parent_nomfolder_id'] = self.parent.myid

        self.prepare_class_params('nomfolder', params)

        rjson = self.sds.query("nom_folder_create",
                               params=params)

        if 'errmsg' in rjson:
            raise SDSError(message="folder creation, "
                           + rjson['errmsg'])

        self.params['nomfolder_id'] = int(rjson[0]['ret_oid'])
        self.myid = int(self.params['nomfolder_id'])

        self.refresh()

    # -------------------------------------
    def get_id_by_fullname(self, fullname):
        """get the ID of the folder with parent path,
           return None if non existant"""

        params = {
            "limit": 1,
            **self.additional_params
        }
        params.update({"WHERE": f"nomfolder_path='{fullname}'"})

        try:
            rjson = self.sds.query('nom_folder_list',
                                   params=params)
        except SDSError as err_descr:
            msg = f"cannot found NOM folder by full name {fullname}"
            msg += " / " + str(err_descr)
            raise SDSError(msg) from err_descr

        if rjson[0]['errno'] != '0':  # pragma: no cover
            raise SDSError("errno raised on get folder")

        return rjson[0]['nomfolder_id']

    # -------------------------------------
    def refresh(self):
        """refresh content of the NOM folder from the SDS"""

        if self.sds is None:
            raise SDSError(message="not connected")

        try:
            if self.parent:
                parents_name = self.parent.get_parent_name_hierarchy()
                nomfolder_id = self.get_id_by_fullname(
                    fullname=f"{parents_name}{self.name}")
            else:
                nomfolder_id = self.get_id_by_fullname(fullname=f"{self.name}")
        except SDSError as err_descr:
            msg = "cannot get NOM folder id"
            msg += " / " + str(err_descr)
            raise SDSError(msg) from err_descr

        params = {
            "nomfolder_id": nomfolder_id,
            **self.additional_params
        }

        rjson = self.sds.query("nom_folder_info",
                               params=params)

        rjson = rjson[0]
        # logging.info(rjson)

        self.myid = int(rjson['nomfolder_id'])

        for label in ['nomfolder_id',
                      'nomfolder_description',
                      'nomfolder_class_name',
                      'nomfolder_nb_netobj']:
            if label not in rjson:   # pragma: no cover
                raise SDSError(f"parameter {label} not found in NOM folder")
            self.params[label] = rjson[label]

        if not self.space and rjson['nomfolder_site_name'] != '#':
            self.bind_spacename(rjson['nomfolder_site_name'])

        if 'nomfolder_class_parameters' in rjson:   # pragma: no cover
            self.update_class_params(rjson['nomfolder_class_parameters'])

    # -------------------------------------

    def bind_spacename(self, spacename):
        """ associate the folder with a space by name"""
        self.space = Space(self.sds, name=spacename)
        try:
            self.space.refresh()
        except SDSError:
            self.space = None
            logging.error(f"Folder cannot be associated"
                          f" with unexistent space ({spacename})")
            raise SDSError("space not found")

    def bind_space(self, space):
        """ associate the folder with a space"""

        if not isinstance(space, Space):
            raise SDSError("bind not provided space object")

        self.space = space

    # -------------------------------------
    def delete(self):
        """deletes the NOM folder in the SDS"""
        if self.sds is None:
            raise SDSError(message="not connected")

        if self.myid == -1:
            raise SDSError("on NOM folder delete")

        params = {
            'nomfolder_id': self.myid,
            **self.additional_params
        }

        self.sds.query("nom_folder_delete",
                       params=params)

        # check if not present
        bError = False
        try:
            time.sleep(1)
            self.refresh()
            bError = True
        except SDSError:
            pass

        if bError:
            raise SDSError("folder not empty, still exists after delete")

        self.clean_params()

    # -------------------------------------

    def update(self):
        """ update the NOM folder in SDS """

        if self.sds is None:
            raise SDSError(message="not connected")

        if self.name is None or self.name == '':
            raise SDSError(message="requires a name")

        params = {
            'nomfolder_id': self.myid,
            'nomfolder_name': str(self.name),
            **self.additional_params
        }

        self.prepare_class_params('nomfolder', params)

        rjson = self.sds.query("nom_folder_update",
                               params=params)

        if 'errmsg' in rjson:  # pragma: no cover
            raise SDSError(message="NOM folder update error, "
                           + rjson['errmsg'])

        self.refresh()

    # -------------------------------------

    def set_param(self, param=None, value=None, exclude=None, name=None):
        """ set a specific param on the NOM folder object """
        super().set_param(param,
                          value,
                          exclude=['nomfolder_id'],
                          name='name')

    # -------------------------------------

    def get_parent_name_hierarchy(self):
        if self.parent:
            parent_name = self.parent.get_parent_name_hierarchy()
            return f"{parent_name}{self.name}/"
        else:
            return f"{self.name}/"

    # -------------------------------------

    def __str__(self):  # pragma: no cover
        """return the string notation of the NOM Folder object"""

        return_val = "*NOM folder* "

        if self.parent:
            parents_name = self.parent.get_parent_name_hierarchy()
            return_val += f"{parents_name}"

        if self.name:
            return_val += f"{self.name}"
        else:
            return_val += f"no_name"

        if self.space is not None:
            return_val += f" space={self.space.name}"

        return_val += self.str_params(exclude=['nomfolder_id',
                                               'name'])

        return_val += str(super().__str__())

        return return_val
