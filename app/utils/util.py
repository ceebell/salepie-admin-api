import os
import uuid
import random
import string

from datetime import datetime

def getUuid():
    uid = str(uuid.uuid4())
    return uid

def base64Encoding(text):
    text_string_bytes = text.encode("ascii")
    base64_bytes = base64.b64encode(text_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string

def base64Encoding(base64text):
    text_string_bytes = base64text.encode("ascii")
    sample_string_bytes = base64.b64decode(text_string_bytes)
    base64_string = sample_string_bytes.decode("ascii")
    return base64_string

def genRandomText(number):
    code = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k = number))
    return code

def genUpperAlphaNumbericText(number):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k = number))
    return code

def genRandomDigit(number):
    code = ''.join(random.choices(string.digits, k = number))
    return code


def getShopCode():
    code_date = datetime.today().strftime("%Y%m%d")
    print(f"code_date = {code_date}")
    code_suff = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 8))
    print(f"code = {code_suff}")
    # code_a = ''.join(code_date , "_" , code)
    res = f"{code_date}_{code_suff}"
    print(f"result  = {res}")
    return res

def convertDateTime(obj):
    
    print(f"convertDateTime >>>>>>>>> {obj}")
    keys = list(obj.keys())
    
    for aKey in keys:
        # value = obj['aKey']
        print(f"{aKey} >>>>>>>>> {obj[aKey]}")
        if(aKey.lower().find("at") > -1 or aKey.lower().find("datetime") > -1):
            if(obj[aKey]):
                print(aKey)
                obj[aKey] = obj[aKey].strftime("%Y-%m-%d %H:%M:%S.%f")
    return obj
