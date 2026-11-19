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
#  * sum values for all keys
#  * get record having largest value
#  * get N largest key-values using value as sort criteria
#  Limitations: * attributes should not contain separator char (by default, COMMA)
#               * values can not be None
#
# This is extension of multikey0 class: support of non-key attributes is added.
# non-key (info) attributes are not used for unique key construction.


import heapq

from multikey0 import multikey0_base

class multikey1_base(multikey0_base):
    
    def __init__(self,attr_names,key_names,append_mode):
        ## ATTENTION! key_names must be subset of attr_names
        ## the rest of attrs are info (non-key) fields
        self.OK=False # check this flag after init
        super(multikey1_base, self).__init__(attr_names,append_mode)
        self.key_names=key_names
        self.info_idx = [] # indices if info fields in attrs
        self.key_idx = [] # indices if key fields in attrs
        self.info_names = []
        self._set_key_indices()
    # end func ----------------------------------------------------------------

    def _set_key_indices(self):  # set keys and info mapping
        self.nkeys = len(self.key_names)
        # self.nattrs = len(self.attr_names) # it is set earlier
        self.info_idx = []
        self.info_names = []
        self.ninfo=0
        rev_idx = [-1] * self.nattrs
        self.key_idx = [-1] * self.nkeys
        succs = True
        for j in range(0, self.nkeys):
            try:
                self.key_idx[j] = self.attr_names.index(self.key_names[j])
                rev_idx[self.key_idx[j]]=j
            except:
                self.key_idx[j] = -2
                succs = False
                raise ValueError('key name '+self.key_names[j]+' isnt listed in attributes')
            # end try
        # end for j
        if succs and (self.nattrs>self.nkeys): # collect attrs not listed in keys
            for j in range(0, self.nattrs):
                if rev_idx[j]==-1:
                    self.info_idx.append(j)
                    self.info_names.append(self.attr_names[j])
                # end if
            # end for j
        # end if
        self.ninfo=len(self.info_idx)
        if self.ninfo<1:
            raise ValueError('no info attributes')
        self.OK=succs
        return
    # end func -------------------------------------------------------------------

    def _create_strkey(self,attrs):
        strattrs=[str(elem) for elem in attrs]
        if (len(strattrs)!=self.nattrs): return None
        keyattr=[]
        for j in range(self.nkeys):
            keyattr.append(strattrs[self.key_idx[j]])
        # end for j
        infoattr=[]
        for j in range(self.ninfo):
            infoattr.append(strattrs[self.info_idx[j]])
        # end for j
        key=self.sepchar.join(keyattr)
        info=self.sepchar.join(infoattr)
        return key,info
    # end func ----------------------------------------------------------------

    def _unpack_strkey(self,key,info):
        keyattrs=key.split(self.sepchar)
        infoattrs=info.split(self.sepchar)
        attrs= [''] * self.nattrs
        for j in range(self.nkeys):
            attrs[self.key_idx[j]]=keyattrs[j]
        # end for j
        for j in range(self.ninfo):
            attrs[self.info_idx[j]]=infoattrs[j]
        # end for j
        return attrs
    # end func ----------------------------------------------------------------

    # subsidiary func for get_nlargest
    def _finalize_sort_list(self,n,records):
        # each record is [value,packed_key,packed_info]
        rslt=None
        try:
            ntop=heapq.nlargest(n, records, key=lambda x: x[0])
            rslt=[]
            for item in ntop:
                attrs=self._unpack_strkey(item[1],item[2])
                rslt.append([item[0],attrs])
            # end for
        finally:
            return rslt
        # end try
    # end func ----------------------------------------------------------------

# end class ===================================================================


class multikey1_list(multikey1_base):

    def __init__(self,attr_names,key_names,append_mode):
        super(multikey1_list, self).__init__(attr_names,key_names,append_mode)
        self.keys=[]
        self.vals=[]
        self.infos=[]
    # end func ----------------------------------------------------------------

    @property
    def nRecs(self):
        return len(self.keys)
    # end func ----------------------------------------------------------------

    def _check_internal(self,key):
        try:
            idx=self.keys.index(key)
        except:
            idx=-1
        return idx
    # end func ----------------------------------------------------------------

    def check_if_present(self,attrs):
        if self.paranoid: self.check_attrs(attrs)
        key,info=self._create_strkey(attrs)
        matched=self._check_internal(key)
        if matched>=0:
            return True
        else:
            return False
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
        key,info=self._create_strkey(attrs)
        matched=self._check_internal(key)
        if matched==-1:
            self.keys.append(key)
            self.vals.append(value)
            self.infos.append(info)
            rslt=0 # new record created
        else:
            rslt=2  # duplicate detected and value updated
            if self.append_mode==1:
                if self.vals[matched]<value:
                    self.vals[matched]=value
                # end if
            elif self.append_mode==2:
                self.vals[matched] += value
            else:
                rslt=1 # skipped duplicate
            # end if
        # end if
        return rslt
    # end func ----------------------------------------------------------------

    def get_value(self,attrs):
        rslt=None
        if self.paranoid: self.check_attrs(attrs)
        key,info=self._create_strkey(attrs)
        matched=self._check_internal(key)
        if matched>=0:
            rslt=self.vals[matched]
        # end if
        return rslt
    # end func ----------------------------------------------------------------

    def set_value(self,attrs,newvalue):
        rslt=False
        if self.paranoid:
            self.check_attrs(attrs)
            self.check_value(newvalue)
        # end if

        key,info=self._create_strkey(attrs)
        matched=self._check_internal(key)
        if matched>=0:
            self.vals[matched]=newvalue
            rslt=True
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
        matched=self._check_internal(key)
        if matched>=0:
            self.vals[matched]+=newvalue
            rslt=True
        # end if
        return rslt
    # end func ----------------------------------------------------------------

    def sum_values(self):
        rslt=0.0
        try:
            for k in range(len(self.keys)):
                rslt += self.vals[k]
            # end for k
        finally:
            return rslt
        # end try
    # end func ----------------------------------------------------------------

    def get_nlargest(self,n): # result is list of lists. Each line is [value, [attrs]]
        rslt=None
        tmp=[]
        nlist=len(self.vals)
        for k in range(nlist):
            tmp.append([self.vals[k],self.keys[k],self.infos[k]])
        # end for k
        rslt=self._finalize_sort_list(n,tmp)
        return rslt
        # end try
    # end func ----------------------------------------------------------------

# end class ===================================================================


class multikey1_dict(multikey1_base):
    def __init__(self,attr_names,key_names,append_mode):
        super(multikey1_dict, self).__init__(attr_names,key_names,append_mode)
        self.data={}
    # end func ----------------------------------------------------------------

    @property
    def nRecs(self):
        return len(self.data.keys())
    # end func ----------------------------------------------------------------

    def _check_internal(self,key):
        Value=self.data.get(key)
        if not(Value is None):
            Value=Value[0]
        # end if
        return Value
    # end func ----------------------------------------------------------------

    def check_if_present(self,attrs):
        if self.paranoid: self.check_attrs(attrs)
        key,info=self._create_strkey(attrs)
        matched=self._check_internal(key)
        if matched is None:
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
        key,info=self._create_strkey(attrs)
        matched=self._check_internal(key)
        if matched is None:
            self.data.update({key:[value,info]})
            rslt=0 # new record created
        else:
            rslt=2  # duplicate detected and value updated
            if self.append_mode==1:
                if self.data[key][0]<value:
                    self.data[key][0]=value
                # end if
            elif self.append_mode==2:
                self.data[key][0] += value
            else:
                rslt=1 # skipped duplicate
            # end if
        # end if
        return rslt
    # end func ----------------------------------------------------------------

    def get_value(self,attrs):
        rslt=None
        if self.paranoid: self.check_attrs(attrs)
        key,info=self._create_strkey(attrs)
        rslt=self.data.get(key)
        if not(rslt is None):
            rslt=rslt[0]
        return rslt
    # end func ----------------------------------------------------------------

    def set_value(self,attrs,newvalue):
        rslt=False
        if self.paranoid:
            self.check_attrs(attrs)
            self.check_value(newvalue)
        # end if
        key,info=self._create_strkey(attrs)
        matched=self._check_internal(key)
        if matched!=None:
            self.data[key][0]=newvalue
            rslt=True
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
        matched=self._check_internal(key)
        if matched!=None:
            self.data[key][0]+=newvalue
            rslt=True
        # end if
        return rslt
    # end func ----------------------------------------------------------------

    def get_nlargest(self,n):
        rslt=None
        try:
            tmp=[]
            for key in self.data.keys():
                tmp.append([self.data[key][0],key,self.data[key][1]])
            # end for k
            rslt=self._finalize_sort_list(n,tmp)
        finally:
            return rslt
        # end try
    # end func ----------------------------------------------------------------

    def sum_values(self):
        rslt=0.0
        try:
            for key in self.data.keys():
                rslt += self.data[key][0]
            # end for k
        finally:
            return rslt
        # end try
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
                info_rslt=self.data[key_rslt][1]
                rslt=self._unpack_strkey(key_rslt,info_rslt)
        finally:
            return rslt
        # end try
    # end func ----------------------------------------------------------------

# end class ===================================================================


