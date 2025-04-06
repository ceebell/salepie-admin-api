#!/usr/bin/env python3
import fileinput
from shutil import copyfile
import json 

def  replaceText(filename, searchtext, replacetext ) : 
    # https://stackoverflow.com/questions/17140886/how-to-search-and-replace-text-in-a-file-using-python
    with fileinput.FileInput(filename, inplace=True ) as file:
        for line in file:
            print(line.replace(searchtext, replacetext), end='')
         
         

data = json.loads(loadJson)

# print(data["name"])

def generateModelFile(data):
            
    copyfile("template1.txt", "template2.txt")           
    # replaceText("template2.txt", "{{modelname}}", "TheModel" )
    # Append-adds at last
    file1 = open("template2.txt", "a")  # append mode

    file1.write("\n\n")
    file1.write(f"class {data['name']}(BaseModel):\n")
    for item in data["fields"]: 
        file1.write(f"\t{item['name']} : ")
        if "isOption" in item : 
            if item['isOption'] == "n":
                file1.write("Option[")
        if  'isList' in item :
            if item['isList'] == "y":
                file1.write("List[")
        file1.write(f"{item['dataType']}")
        if 'isList' in item : 
            if item['isList'] == "y":
                file1.write("]")
        if 'isOption' in item : 
            if item['isOption'] == "n":
                file1.write("]")
        if  (not item['init']) == False:
            file1.write(f" = {item['init']}")

        file1.write("\n")

    file1.close()   
            
# loadJson = """{
#         "name": "ProductItem",
#         "detail": "model1",
#         "id": "yabfy9f34-baed-11eb-afd9-6c4008ad0d26",
#         "fields": [
#             {
#                 "name": "name",
#                 "dataType": "str",
#                 "desc": "name of product item",
#                 "init": "",
#                 "id": "xxx60e-baed-11eb-afd9-6c4008ad0d26",
#                 "createDatetime":"2021-05-22T18:05:11.819+07:00",
#                 "updateDatetime":"2021-05-22T18:05:11.819+07:00"
#             },
#             {
#                 "name": "code",
#                 "dataType": "str",
#                 "isList": "n",
#                 "isOption" : "y",
#                 "desc": "code of name",
#                 "init": "xxx",
#                 "id": "yyy60e-baed-11eb-afd9-6c4008ad0d26",
#                 "createDatetime":"2021-05-22T18:05:11.819+07:00",
#                 "updateDatetime":"2021-05-22T18:05:11.819+07:00"
#             }
#         ],
#         "createDatetime": "2021-05-22T18:05:11.819+07:00"
#     }"""
