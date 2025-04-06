import requests 
import math
from core.config  import SMS_API
import json

from database.mongodb  import AsyncIOMotorClient, get_database



#***************************************************
#********       SENDING SMS    *********************
#***************************************************

def sendSms(phone: str, coupon: str, couponStatus : str, smsMessage: str, smsSender: str) -> dict:

    

    if couponStatus != "ว่างอยู่" and couponStatus != "ส่งออก" :
        return

    url = SMS_API.SMS_URL

    headers = {
    "Accept": "application/json",
        "Content-Type": "application/json",
        "api_key": SMS_API.API_KEY,
        "secret_key": SMS_API.SECRET_KEY
    }

    link = f"{SMS_API.COUPON_URL}{coupon}"

    smsMsg = f"{link}"

    if not smsMessage:
        smsMsg = f"{link}"
    else:
        smsMsg = f"{smsMessage} {link}"


    payload = {
    "message":smsMsg,
    "phone": phone,
    "sender": smsSender ,
    "url": "",
    } 
    responseObj = dict()
    try:
        apiResponse = requests.request("POST", url, json=payload, headers=headers)     
        print(apiResponse.text)
        
        if apiResponse.text:
            responseObj = json.loads(apiResponse.text)
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            # print(responseObj['code'])
            # print(responseObj['detail'])
            # print(responseObj['result']['usedcredit'])
    except:
        return False
    

    if responseObj : 
        if responseObj["code"] == "000":
            return True
        else:
            return False
    else:
        return False   

    # res = dict()
    # res["success"] = True
    # res["totalItem"] = len(customerList)
    # res["result"] = customerList

    # return res

#***************************************************

#***************************************************
#********       PAGE CALCULATION    ****************
#***************************************************

def pageCalculation(page , pageSize , itemCount) -> dict:

    if page <= 0:
        page = 1
    
    if pageSize <= 0 :
        pageSize = 1

    #*** [1] PAGE COUNT
    #*** INIT
    pageCount = 1
    pageCount = math.floor( itemCount / pageSize ) + 1
    
    #*** [2] SKIP
    skip = (page - 1) * pageSize

    #*** [3] LIMIT
    limit = pageSize

    #*** [4] ITEMS IN PAGE

    #*** page == pageCount
    if page == pageCount:
        itemInPage = itemCount - ( (pageCount - 1) * pageSize )
    
    #*** page > pageCount
    elif page > pageCount:
        page = pageCount
        itemInPage = itemCount - ( (pageCount - 1) * pageSize )

    #*** page < pageCount
    else:
        itemInPage = pageSize

    #*** [5] START INDEX
    startIndex = skip + 1

    #*** [6] END INDEX
    endIndex = skip + itemInPage

    pageData = {
                "page" : page,
                "pageSize" : pageSize,
                "itemCount" : itemCount,
                "pageCount" :  pageCount,
                "skip" : skip,
                "limit" : limit,
                "itemInPage" : itemInPage,
                "startIndex" : startIndex,
                "endIndex" : endIndex

            }
    return pageData


