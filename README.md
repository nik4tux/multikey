Class for storage of key-value pairs. Key is composite: it is list of attributes.
Each key is assumed to be unique (it differs from others at least in one attribute)
Features:
  * check if new key is already in storage
  * append key-value to storage (and, optionally, check if key is already there)
  * get value by key
  * set new value for given key
  * for given key, append new value for old value (accumulate)
  * sum values for all keys
  * get record having largest value
  * get N largest key-values using value as sort criteria
  Limitations: * attributes should not contain separator char (by default, COMMA)
               * values can not be None
