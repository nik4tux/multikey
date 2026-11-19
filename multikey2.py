#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: nik4tux
Copyright (C) 2021
Licensed under GNU GPLv3 (or later): see <https://www.gnu.org/licenses/>
"""
#  Class for storage of key-value pairs. Key is composite: it is list of attributes.
#  Each key is assumed to be unique (it differs from others at least in one attribute)
#  Features:
#  * check if new key is already in storage
#  * append key-value to storage (and, optionally, check if key is already there)
#  * get value by key
#  * set new value for given key
#  * for given key, append new value for old value (accumulate)
#  * get record having largest value
#  * get N largest key-values using value as sort criteria
#  Limitations: * attributes should not contain separator char (by default, COMMA)
#               * values can not be None
#
# This is extension of multikey0, multikey1 classes: support of two-level keys is added.
# Subset of attributes is primary key, the rest of attributes is secondary key.
# The main goal is storage of values, associated with unique keys.
# Value, attributed to pri key is composite. It is sum of values for records,
# having the same primary key and different secondary keys.

from multikey0 import multikey0_dict
from multikey1 import multikey1_dict

class multikey2_dict(multikey1_dict):
    def __init__(self,attr_names,key_names,append_mode):
        ## ATTENTION! key_names must be subset of attr_names
        ## the rest of attrs are info (non-key) fields        
        # append_mode is integer number from 0 to 2
        # 0 -- do not add if combo key is already present (duplicate)
        # 1 -- if key is duplicate, set value to maximum among old and new value
        # 2 -- if key is duplicate, set value to sum of old and new value
        super(multikey2_dict, self).__init__(attr_names,key_names,append_mode)
    # end func ----------------------------------------------------------------

    @property
    def nRecs(self):
        return len(self.data.keys())
    # end func ----------------------------------------------------------------

    def _check_internal(self,key): #this will return composite value for pri key
                                   # key is string (it is packed list of key attrs)
        rec=self.data.get(key)
        if not(rec is None):
            Value=rec[0] # rec[0] is composite Value, rec[1] is of type multikey0_dict
        else:
            Value=None
        # end if
        return Value
    # end func ----------------------------------------------------------------

    def _get_full_record(self,key): #this will return composite attrs for pri key
                                 # key is string (it is packed list of key attrs)
        rslt=None
        rec=self.data.get(key)
        if not(rec is None):
            key_attrs=key.split(self.sepchar)
            combo_value=rec[0]
            rec_dict=rec[1] # each rec_dict is of type multikey0_dict
            info_attrs=rec_dict.get_max_item()
            attrs = key_attrs + info_attrs
            rslt= [combo_value,attrs]
        # end if
        return rslt
    # end func ----------------------------------------------------------------

    def _check_internal_ext(self,key,info):
        rec=self.data.get(key)
        if not(rec is None):
            # rec[0] is composite Value
            rec_dict=rec[1] # each rec_dict is of type multikey0_dict
            Value=rec_dict._check_internal(info) # None if not found
        else:
            Value=None
        # end if
        return Value
    # end func ----------------------------------------------------------------


    def check_if_present(self,attrs):
        if self.paranoid: self.check_attrs(attrs)
        key,info=self._create_strkey(attrs)
        Value=self._check_internal_ext(key,info)
        if Value is None:
            return False
        else:
            return True
        # end if
    # end func ----------------------------------------------------------------

    # return codes: None -- some error, 0 -- skipped duplicate
    #              1-- duplicate detected and value updated
    def append_record(self,attrs,value):
        rslt=None
        if self.paranoid:
            self.check_attrs(attrs)
            self.check_value(value)
        # end if
        try:
            key,info=self._create_strkey(attrs)
            info_list=info.split(self.sepchar)
            rec=self.data.get(key)
            if (rec is None):
                rslt=0 # create new pri key
                self.data.update({key:[]})
                self.data[key].append(value) # composite value is equal to value of single record
                self.data[key].append(multikey0_dict(self.info_names,self.append_mode))
                self.data[key][1].append_record(info_list,value)
            else:
                rec_dict=rec[1] # each rec_dict is of type multikey0_dict
                OldVal=rec_dict._check_internal(info) # None if not found
                if (OldVal is None):
                    rslt=0 # create new secondary key
                    rec[0] += value # increment pri key value
                    rec_dict.append_record(info_list,value)
                else: # full duplicate (both key and info identic)
                    rslt=2  # duplicate detected and value updated
                    if self.append_mode==1: # take the biggest one
                        if OldVal<value: # update value
                            rec[0] = rec[0] - OldVal + value
                            rec_dict[info] = value
                        # end if
                    elif self.append_mode==2: # sum
                        rec[0] += value
                        rec_dict[info] += value
                    else:
                        rslt=1 # skipped duplicate
                    # end if
                # end if
            # end if
        except Exception as e:
            raise Exception('exception in append_record: '+str(e))
        finally:
            return rslt
        # end try
    # end func ----------------------------------------------------------------

    def get_value(self,attrs):
        rslt=None
        if self.paranoid: self.check_attrs(attrs)
        key,info=self._create_strkey(attrs)
        rslt=self._check_internal_ext(key,info)
        return rslt
    # end func ----------------------------------------------------------------

    def set_value(self,attrs,newvalue):
        rslt=False
        if self.paranoid:
            self.check_attrs(attrs)
            self.check_value(newvalue)
        # end if
        key,info=self._create_strkey(attrs)
        rec=self.data.get(key)
        if not(rec is None):
            rec_dict=rec[1] # each rec_dict is of type multikey0_dict
            OldVal=rec_dict._check_internal(info) # None if not found
            if (OldVal!=None):
                rec_dict.data[info]=newvalue
                rslt=True
            # end if
        # end if
        return rslt
    # end func ----------------------------------------------------------------

    def set_value_append(self,attrs,newvalue):
        rslt=False
        if self.paranoid:
            self.check_attrs(attrs)
            self.check_value(newvalue)
        # end if
        key,info=self._create_strkey(attrs)
        rec=self.data.get(key)
        if not(rec is None):
            rec_dict=rec[1] # each rec_dict is of type multikey0_dict
            OldVal=rec_dict._check_internal(info) # None if not found
            if (OldVal!=None):
                rec_dict.data[info] += newvalue
                rslt=True
            # end if
        # end if
        return rslt
    # end func ----------------------------------------------------------------

    # get attrs for item having max value
    def get_max_item(self):  # result is list of attrs
        key_rslt=None
        rslt=None
        try:
            for key in self.data.keys():
                if (key_rslt is None):
                    key_rslt = key
                else:
                    if self.data[key][0]>self.data[key_rslt][0]:
                        key_rslt = key
                    # end if
                # end if
            # end for k

            if (key_rslt is None):
                return rslt
            else:
                rec=self.data[key_rslt][1]
                info_rslt=rec.get_max_item()
                info=self.sepchar.join(info_rslt)
                rslt=self._unpack_strkey(key_rslt,info)
        finally:
            return rslt
        # end try
    # end func ----------------------------------------------------------------


    def get_nlargest(self,n):
        rslt=None
        try:
            tmp=[]
            for key in self.data.keys():
                rec=self.data.get(key)
                combo_value=rec[0]
                rec_dict=rec[1] # each rec_dict is of type multikey0_dict
                info=rec_dict.get_max_item()
                info_str=self.sepchar.join(info)
                tmp.append([combo_value,key,info_str])
            # end for k
            rslt=self._finalize_sort_list(n,tmp)
        finally:
            return rslt
        # end try
    # end func ----------------------------------------------------------------

# end class ===================================================================


