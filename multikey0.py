#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: nickkuz
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

import heapq

class multikey0_base:

    def __init__(self,attr_names,append_mode):
        # append_mode is integer number from 0 to 2
        # 0 -- do not add if key is already present (duplicate)
        # 1 -- if key is duplicate, set value to maximum among old and new value
        # 2 -- if key is duplicate, set value to sum of old and new value
        if (append_mode<0)or(append_mode>2):
            self.OK=False
            raise ValueError('wrong append_mode ('+str(append_mode)+')')
        # end if
        self.append_mode=append_mode
        self.attr_names=attr_names
        self.nattrs=len(attr_names)
        self.paranoid=False
        self.sepchar=','  # attention! this char should not be present in attributes
    # end func ----------------------------------------------------------------

    @property
    def nRecs(self):
        return 0  # abstract
    # end func ----------------------------------------------------------------

    def _create_key(self,attrs):
        strattrs=[str(elem) for elem in attrs]
        combokey=self.sepchar.join(strattrs)
        return combokey
    # end func ----------------------------------------------------------------

    def _unpack_strkey(self,key):
        attrs=key.split(self.sepchar)
        return attrs
    # end func ----------------------------------------------------------------

    def check_value(self,value):
        if value is None:
            raise ValueError('value=None is prohibited')
        # end if
        if not((type(value)==float)or(type(value)==int)):
            raise ValueError('value type is incorrect ('+str(value)+')')
    # end func ----------------------------------------------------------------

    def check_attrs(self,attrs): # "attrs" is list of attributes
        if (len(attrs)!=self.nattrs):
            msg='wrong number of attrs'
            raise ValueError(msg)
        # end if
        strattrs=[str(elem) for elem in attrs]
        for attr in strattrs:
            if self.sepchar in attr:
                msg='wrong char in attribute: '+attr
                raise ValueError(msg)
            # end if
        # end for
    # end func ----------------------------------------------------------------

    def check_if_present(self,attrs): # check if new key is already in storage
        self.check_attrs(attrs)
        return True
    # end func ----------------------------------------------------------------

    #append key-value to storage (and, check if key is already there)
    # return codes: None -- some error, 0 -- skipped duplicate
    #              1-- duplicate detected and value updated
    def append_record(self,attrs,value):
        self.check_attrs(attrs)
        return None
    # end func ----------------------------------------------------------------

    def get_value(self,attrs): # get value by key
        self.check_attrs(attrs)
        return None
    # end func ----------------------------------------------------------------

    def set_value(self,attrs,newvalue): # set new value for given key
        self.check_attrs(attrs)
        return True
    # end func ----------------------------------------------------------------

    # for given key, append new value for old value (accumulate)
    def set_value_append(self,attrs,newvalue):
        self.check_attrs(attrs)
        return True
    # end func ----------------------------------------------------------------

    # sum all values
    def sum_values(self):
        return 0.0
    # end func ----------------------------------------------------------------

    # get attrs for item having max value
    def get_max_item(self):  # result is list of attrs
        return []
    # end func ----------------------------------------------------------------

    #  get N largest key-values using value as sort criteria.
    #  Result is list of lists. Each line is [value, [attrs]]
    def get_nlargest(self,n):
        return None
    # end func ----------------------------------------------------------------

    # subsidiary func for get_nlargest
    def _finalize_sort_list(self,n,records):
        # each record is [value,packed_attrs]
        rslt=None
        try:
            ntop=heapq.nlargest(n, records, key=lambda x: x[0])
            rslt=[]
            for item in ntop:
                attrs=self._unpack_strkey(item[1])
                rslt.append([item[0],attrs])
            # end for
        finally:
            return rslt
        # end try
    # end func ----------------------------------------------------------------

    def results_print(self,list2d):
        for line in list2d:
            sline=[]
            for elem in line:
                try:
                    if isinstance(elem,str):
                        sline.append(elem)
                    elif isinstance(elem,list):
                        subitem=[str(item) for item in elem]
                        ss=self.sepchar.join(subitem)
                        sline.append(ss)
                    else:
                        sline.append(str(elem))
                except:
                    sline.append('?')
            merged=self.sepchar.join(sline)
            print('%s' % (merged) )
        # end for line
    # end func ----------------------------------------------------------------

# end class ===================================================================


class multikey0_list(multikey0_base):

    def __init__(self,attr_names,append_mode):
        super(multikey0_list, self).__init__(attr_names,append_mode)
        self.keys=[]
        self.vals=[]
    # end func ----------------------------------------------------------------

    @property
    def nRecs(self):
        return len(self.keys)
    # end func ----------------------------------------------------------------

    def _check_internal(self,combokey):
        try:
            idx=self.keys.index(combokey)
        except:
            idx=-1
        return idx
    # end func ----------------------------------------------------------------

    def check_if_present(self,attrs):
        if self.paranoid: self.check_attrs(attrs)
        combokey=self._create_key(attrs)
        matched=self._check_internal(combokey)
        if matched>=0:
            return True
        else:
            return False
        # end if
    # end func ----------------------------------------------------------------

    # return codes: None -- some error, 0 -- new record created,
    # 1 -- skipped duplicate, 2-- duplicate detected and value updated
    def append_record(self,attrs,value):
        rslt=None
        if self.paranoid:
            self.check_attrs(attrs)
            self.check_value(value)
        # end if
        combokey=self._create_key(attrs)
        matched=self._check_internal(combokey)
        if matched==-1:
            self.keys.append(combokey)
            self.vals.append(value)
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
        combokey=self._create_key(attrs)
        matched=self._check_internal(combokey)
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

        combokey=self._create_key(attrs)
        matched=self._check_internal(combokey)
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

        combokey=self._create_key(attrs)
        matched=self._check_internal(combokey)
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

    # get attrs for item having max value
    def get_max_item(self):  # result is list of attrs
        k_rslt=None
        try:
            for k in range(len(self.keys)):
                if (k_rslt is None):
                    k_rslt = k
                else:
                    if self.vals[k]>self.vals[k_rslt]:
                        k_rslt = k
                    # end if
                # end if
            # end for k
        finally:
            if (k_rslt is None):
                return None
            else:
                key=self.keys[k_rslt]
                return self._unpack_strkey(key)
        # end try
    # end func ----------------------------------------------------------------

    def get_nlargest(self,n): # result is list of lists. Each line is [value, [attrs]]
        rslt=None
        tmp=[]
        nlist=len(self.vals)
        for k in range(nlist):
            tmp.append([self.vals[k],self.keys[k]])
        # end for k
        rslt=self._finalize_sort_list(n,tmp)
        return rslt
        # end try
    # end func ----------------------------------------------------------------

# end class ===================================================================


class multikey0_dict(multikey0_base):
    def __init__(self,attr_names,append_mode):
        super(multikey0_dict, self).__init__(attr_names,append_mode)
        self.data={}
    # end func ----------------------------------------------------------------

    @property
    def nRecs(self):
        return len(self.data.keys())
    # end func ----------------------------------------------------------------

    def _check_internal(self,combokey):
        Value=self.data.get(combokey)
        return Value
    # end func ----------------------------------------------------------------

    def check_if_present(self,attrs):
        if self.paranoid: self.check_attrs(attrs)
        combokey=self._create_key(attrs)
        matched=self._check_internal(combokey)
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
        combokey=self._create_key(attrs)
        matched=self._check_internal(combokey)
        if matched is None:
            self.data.update({combokey:value})
            rslt=0 # new record created
        else:
            rslt=2  # duplicate detected and value updated
            if self.append_mode==1:
                if self.data[combokey]<value:
                    self.data[combokey]=value
                # end if
            elif self.append_mode==2:
                self.data[combokey] += value
            else:
                rslt=1 # skipped duplicate
            # end if
        # end if
        return rslt
    # end func ----------------------------------------------------------------

    def get_value(self,attrs):
        rslt=None
        if self.paranoid: self.check_attrs(attrs)
        combokey=self._create_key(attrs)
        rslt=self.data.get(combokey)
        return rslt
    # end func ----------------------------------------------------------------

    def set_value(self,attrs,newvalue):
        rslt=False
        if self.paranoid:
            self.check_attrs(attrs)
            self.check_value(newvalue)
        # end if
        combokey=self._create_key(attrs)
        matched=self._check_internal(combokey)
        if matched!=None:
            self.data[combokey]=newvalue
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
        combokey=self._create_key(attrs)
        matched=self._check_internal(combokey)
        if matched!=None:
            self.data[combokey]+=newvalue
            rslt=True
        # end if
        return rslt
    # end func ----------------------------------------------------------------

    def sum_values(self):
        rslt=0.0
        try:
            for key in self.data.keys():
                rslt += self.data[key]
            # end for k
        finally:
            return rslt
        # end try
    # end func ----------------------------------------------------------------

    # get attrs for item having max value
    def get_max_item(self):  # result is list of attrs
        key_rslt=None
        try:
            for key in self.data.keys():
                if (key_rslt is None):
                    key_rslt = key
                else:
                    if self.data[key]>self.data[key_rslt]:
                        key_rslt = key
                    # end if
                # end if
            # end for k
        finally:
            if (key_rslt is None):
                return None
            else:
                return self._unpack_strkey(key_rslt)
        # end try
    # end func ----------------------------------------------------------------

    def get_nlargest(self,n): # details: sort dict as is, then convert to list
        rslt=None
        try:
            ntop=heapq.nlargest(n, self.data.items(), key=lambda x: x[1])
            rslt=[]
            for item in ntop:
                attrs=self._unpack_strkey(item[0])
                rslt.append([item[1],attrs])
            # end for item
        finally:
            return rslt
        # end try
    # end func ----------------------------------------------------------------

# end class ===================================================================


