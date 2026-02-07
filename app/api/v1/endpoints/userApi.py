
from typing import List, Optional , Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, BackgroundTasks, File


from repo import  userRepo, authRepo, fileRepo

##### BEGIN : DATABSE #####

from models import  schemas, user
# from loguru import logger
from pydantic import BaseModel, Json ,ValidationError, validator, Field, EmailStr
from database.mongodb  import AsyncIOMotorClient, get_database

# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.config  import AlexEmail
import shutil

from utils import util
import math
import uuid ,base64, re
from pathlib import Path
from datetime import datetime


router = APIRouter()


# [u-4]
@router.get("/get-user-by-id/{uid}",  tags=["user"] )
async def getUserByID( uid:str,   db: AsyncIOMotorClient =  Depends(get_database),  currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
   

    # print(f" **************** current user >>> ",currentUser)

    if uid is None or uid == "":
            raise HTTPException(status_code=400, detail="uid is required")
    
    aUser = await db["salepiev1"]["user"].find_one({ "uid" : uid , "deleted": { "$ne": True } , "domainId" : currentUser.domainId })

    if aUser is None:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        userOut =  user.UserOut(**aUser)
    except:
        raise HTTPException(status_code=500, detail="Data Converting Error")

    return userOut


# [u-5] get user list with pagination
@router.get("/get-user-list-in-domain",  tags=["user"] )
async def getUserListInDomain(
    db: AsyncIOMotorClient =  Depends(get_database),  
    currentUser  : user.UserDb = Depends(authRepo.get_current_active_user),
    page: int = Query(1, ge=1),  # Default page = 1
    page_size: int = Query(10, ge=1, le=100),  # Default page_size = 10
    q: Optional[str] = Query(None),
    itemStatus: Optional[str] = Query(None),
    roles: Optional[List[str]] = Query(None),
    sortBy: Optional[str] = Query(None)
    ):

    # ============================================
    #  Begin: Variable preparation
    # ============================================
    criteria = {}
    

    
    start = (page - 1) * page_size
    end = start + page_size
    
    
    if q:
        criteria["textSearch"] = q
    else:
        criteria["textSearch"] = ""
        
    if itemStatus:
        criteria["itemStatus"] = itemStatus

    if sortBy:
        sorting = sortBy

    # ============================================
    #  End: Variable preparation
    # ============================================
   

    rows = []

    query = {
                    "domainId": currentUser.domainId,
                    "deleted": { "$ne": True },
                    "$or": [
                        { "email": { "$regex": criteria["textSearch"], "$options": "i" }},
                        { "firstName": { "$regex": criteria["textSearch"], "$options": "i" }},
                        { "lastName": { "$regex": criteria["textSearch"], "$options": "i" }},
                        { "description": { "$regex": criteria["textSearch"], "$options": "i" }}
                    ]
                }
    
    # ++++++ เพิ่มส่วนนี้ครับ ++++++
    if roles:
        # $in จะหาว่าใน DB (ที่เป็น array) มีค่าใดค่าหนึ่งตรงกับใน input list หรือไม่
        query["roles"] = { "$in": roles }
    # +++++++++++++++++++++++++++

    # นับจำนวนทั้งหมดก่อน (เพื่อให้ได้ totalItems ที่ถูกต้องตาม Filter)
    totalItems =  await db["salepiev1"]["user"].count_documents(query)

    # Query ข้อมูลตามหน้า
    cursor = db["salepiev1"]["user"].find(query).sort("createDateTime", -1)
    
    # Apply Pagination ในระดับ Database (เร็วกว่าและประหยัด Ram กว่า)
    cursor.skip(start).limit(page_size)

    # 3. ดึงข้อมูลจริง (*** ต้อง await ***)
    rows = await cursor.to_list(length=page_size)

    # resp =   [user.UserOut(**row) async for row in rows]
    resp = [user.UserOut(**row) for row in rows]

    
    if not resp:
        return {
            "success": True,
            "page": 1,
            "pageSize": 10,
            "totalItems": 0,
            "totalPages": 1,
            "data": [],
        } 
        # raise HTTPException(
        #           status_code=404, detail="Not Found Users"
        #   )
    

    # data = resp[start:end]
    # ไม่ต้อง slice resp[start:end] อีกแล้ว เพราะ resp คือข้อมูลของ page นั้นๆ แล้ว
    data = resp
   

    return {
        "success": True,
        "page": page,
        "pageSize": page_size,
        "totalItems": totalItems,
        "totalPages": math.ceil(totalItems / page_size),
        "data": data,
    }   


# [u-7] Change user active status  
@router.post("/change-user-active",  tags=["user"] )
async def changeUserStatus( activeForm : user.ActiveForm,  db: AsyncIOMotorClient =  Depends(get_database),  currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
    print(f"searchForm >>> ",activeForm.uid)
    try:
        row = await db["salepiev1"]["user"].find_one({ "uid" : activeForm.uid })
        userDb =   user.UserDb(**row) 
    except:
        raise HTTPException(status_code=400, detail="Unable to get user")
    
    userDb.isActive = activeForm.isActive
    edit = await db["salepiev1"]["user"].update_one({"uid": activeForm.uid}, {'$set': userDb.model_dump() })

    return {
        "success": True
    }


# [u-6] Edit my profile
@router.post("/edit-my-profile",  tags=["user"] )
async def editMyProfile( 
            editForm : user.UserEditProfile,  
            db: AsyncIOMotorClient =  Depends(get_database),  
            currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
    # print(f"searchForm >>> ",searchForm.uid)

    try:
        row = await db["salepiev1"]["user"].find_one({ "uid" : currentUser.uid })
        userDb =   user.UserDb(**row) 
    except:
        raise HTTPException(status_code=400, detail="Unable to get user")
    
    userDb.firstName = editForm.firstName
    userDb.lastName  = editForm.lastName
    userDb.address   = editForm.address
    userDb.phone     = editForm.phone
    userDb.phone     = editForm.phone
    userDb.isActive  = editForm.isActive
    userDb.roles     = editForm.roles
    userDb.status    = editForm.status
    userDb.updateDateTime = datetime.now(),

    # ---- handle images array ----
    new_images = []

    # print("editForm.images >>>>>>> {editForm.images}")

    for idx, img in enumerate(editForm.images or []):
        # ถ้าส่ง deleted มา → เก็บสถานะไว้ (ตามโครงสร้างคุณ)
        print("* * * * *This is images ")
        if img.deleted:
            new_images.append({
                "seq": img.seq if img.seq is not None else idx,
                "deleted": True,
            })
            continue

        if img.url:
            saved = save_data_url_image(img.url, userDb.uid)
            new_images.append({
                "seq": img.seq if img.seq is not None else idx,
                "deleted": False,
                **saved
            })
        else:
            # ถ้าไม่มี dataUrl และไม่ deleted → ข้าม หรือจะ error ก็ได้
            # raise HTTPException(400, "image missing dataUrl")
            pass

        # เลือกพฤติกรรม:
        # (A) replace ทั้ง images
        if new_images:
            userDb.images = new_images
    
    # userDb.admin = searchForm.admin
    edit = await db["salepiev1"]["user"].update_one({"uid": currentUser.uid}, {'$set': userDb.model_dump() })
    
    print (f"edit >>> ",edit.modified_count)
    
    userOut = user.UserOut(**userDb.model_dump())


    return{
            "success": True,
             "data": userOut
           }



# [u-3]
@router.post("/delete-user/{userId}",  tags=["user"] )
async def deleteUserInDomain( userId : str,  db: AsyncIOMotorClient =  Depends(get_database),  currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
    print(f"userId >>> ",userId)
    try:
        result  = await db["salepiev1"]["user"].delete_one({ "uid" : userId })
       
    except:
        return{
            "success": False,
            "data": userOut
        }
    #     raise HTTPException(status_code=400, detail="Unable to delete user")
    
    return "OK" # {"deleted_count": result.deleted_count}

# [u-2]
@router.post("/soft-delete/{userId}",  tags=["user"] )
async def deleteUserInDomain( userId : str,  db: AsyncIOMotorClient =  Depends(get_database),  currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
    # print(f"searchForm >>> ",userId)
    row = await db["salepiev1"]["user"].find_one({ "uid" : userId })

    if row is None:
        raise HTTPException(status_code=404, detail="Not found user")

    # try:
    #     row = await db["salepiev1"]["user"].find_one({ "uid" : userId })
    #     userDb =   user.UserDb(**row) 
    # except:
    #     raise HTTPException(status_code=400, detail="Not found user")
    
    userDb =   user.UserDb(**row) 
    userDb.deleted = True

    try:
        edit = await db["salepiev1"]["user"].update_one({"uid": userId}, {'$set': userDb.dict() })

        # print(f"edit >>> ",edit)
       
    except:
        raise HTTPException(status_code=500, detail="Unable to delete user")
    
    return "OK" # {"deleted_count": result.deleted_count}


@router.post("/add-user-in-domain",  tags=["user"])
async def createUserInDomain( domainId: str, userCreate: List[user.UserCreate],  db: AsyncIOMotorClient =  Depends(get_database),  currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
    # students = await retrieve_students()
    # students = StudentSchema()
    # students = await conn["alex_office_admin"]["movie"].find({})
    
    # if userdb:
    #     raise HTTPException(status_code=400, detail="Email already registered")
    
    
    # newuser = await userRepo.createUser(db=db, create=userCreate)
    dbuser = user.UserDb(**userCreate.dict())
    # dbuser.change_password(user.password)
    dbuser.uid = util.getUuid()
    dbuser.hashedPassword = authRepo.get_password_hash(userCreate.password)
    dbuser.domainId = domainId
    row = await db["salepiev1"]["user"].insert_one(dbuser.dict())
   
    # if row:
    #     return Movie(**row)
    


@router.post("/register",  tags=["user"] ,  response_model=user.UserUpdate)
async def register_user(reguser: user.UserCreate,  db: AsyncIOMotorClient =  Depends(get_database)):
   
    # logger.info(">>>>>>>>>>>> userReg  DB >>>>>>>>>>>>>>>>>>>>>")
    try: 
        userdb = await userRepo.createUser(db=db, create=reguser) 
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")

    return userdb

USER_IMAGE_URL = "http://localhost:8000/static/uploads/user"
UPLOAD_ROOT = Path("static/uploads/user")
ALLOWED = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB

dataurl_re = re.compile(r"^data:(image\/(?:png|jpeg|webp));base64,(.+)$")

def save_data_url_image(data_url: str, uid: str) -> dict:
    m = dataurl_re.match(data_url or "")
    if not m:
        raise HTTPException(status_code=400, detail="Invalid image dataUrl")

    content_type = m.group(1)
    b64 = m.group(2)

    raw = base64.b64decode(b64)
    if len(raw) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="Image too large (max 5MB)")

    user_dir = UPLOAD_ROOT / uid
    user_dir.mkdir(parents=True, exist_ok=True)

    ext = ALLOWED.get(content_type)
    if not ext:
        raise HTTPException(status_code=400, detail=f"Unsupported image type: {content_type}")

    filename = f"staff_{uuid.uuid4().hex}{ext}"
    path = user_dir / filename
    path.write_bytes(raw)

    return {
        "getUrl" : f"{USER_IMAGE_URL}/{uid}/{filename}",
        "path": str(path).replace("\\", "/"),
        "filename": filename,
        "contentType": content_type,
        "size": len(raw),
    }


# [u-8] Edit my shop staff profile
@router.post("/edit-staff-profile/{userId}",  tags=["user"] )
async def editStaffProfile( 
    userId : str, editForm : user.UserEditProfile,  
    db: AsyncIOMotorClient =  Depends(get_database),  
    currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
    # print(f"editForm >>> ",editForm)

    try:
        row = await db["salepiev1"]["user"].find_one({ "domainId" : currentUser.domainId, "uid" : userId })
        userDb =   user.UserDb(**row) 
    except:
        raise HTTPException(status_code=404, detail="Unable to get user")
    
    userDb.firstName = editForm.firstName
    userDb.lastName  = editForm.lastName
    userDb.address   = editForm.address
    userDb.phone     = editForm.phone
    userDb.isActive  = editForm.isActive
    userDb.roles     = editForm.roles
    userDb.status    = editForm.status
    userDb.updateDateTime = datetime.now()

    # ---- handle images array ----
    new_images = []

    for idx, img in enumerate(editForm.images or []):
        print(f"IMAGE ::: for loop ")
        # ถ้าส่ง deleted มา → เก็บสถานะไว้ (ตามโครงสร้างคุณ)
        if img.deleted:
            new_images.append({
                "seq": img.seq if img.seq is not None else idx,
                "deleted": True,
            })
            continue
        print(f"IMAGE ::: ON data Url")
        if img.dataUrl:
            print(f"IMAGE ::: img.dataUrl comes")
            # ✅✅ 1. เพิ่ม Logic: ลบไฟล์เก่าทั้งหมดในโฟลเดอร์ของ User นี้ทิ้งก่อน
            user_dir = UPLOAD_ROOT / userDb.uid
            
            if user_dir.exists():
                for file_path in user_dir.iterdir():
                    if file_path.is_file():
                        try:
                            file_path.unlink() # ลบไฟล์
                            print(f"Deleted old file: {file_path}")
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")
            
            # ✅✅ 2. จากนั้นค่อยบันทึกไฟล์ใหม่
            saved = save_data_url_image(img.dataUrl, userDb.uid)
            print(f"* * * * *This is images {saved}")

            new_images.append({
                "seq": img.seq if img.seq is not None else idx,
                "deleted": False,
                **saved
            })

            print(f"\n\n\n\n🧮🧮🧮🧮 new_images >>> ",new_images)
        elif not img.getUrl :
            print(f"IMAGE ::: not img.getUrl")
            # ถ้าไม่มี dataUrl และไม่ deleted → ข้าม หรือจะ error ก็ได้
            # raise HTTPException(400, "image missing dataUrl")
            print(f"I NEED TO DELETE !!!! {userDb.email}'s image")
            userDb.images = []
            break
        print(f"IMAGE ::: End each loop")
        # เลือกพฤติกรรม:
        # (A) replace ทั้ง images
        if new_images:
            userDb.images = new_images

    print(f"IMAGE ::: End ALL loop")
    
    
    # userDb.admin = searchForm.admin
    edit = await db["salepiev1"]["user"].update_one({"uid": userId}, {'$set': userDb.model_dump() })
    
    print (f"edit >>> ",edit.modified_count)
    
    userOut = user.UserOut(**userDb.model_dump())


    return{
            "success": True,
             "data": userOut
           }

# [u-1]
@router.post("/create-staff",  tags=["user"])
async def createStaff( userCreate: user.UserCreate,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
    # students = await retrieve_students()
    # students = StudentSchema()
    # students = await conn["alex_office_admin"]["movie"].find({})
    userdb = await userRepo.getUserByEmail(db, userCreate.email)


    if userdb:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    
    newuser = await userRepo.createUserInTheSameDomain(db=db, create=userCreate, currentUser=currentUser)

    userOut = user.UserOut(**newuser.model_dump())
   
    return {"success": True,
             "data": userOut
           }
    # if row:
    #     return Movie(**row)
    

@router.post("/add-user-from-google",  tags=["user"])
async def createUser( userCreate: user.SocialRegister,  db: AsyncIOMotorClient =  Depends(get_database)):
    # students = await retrieve_students()
    # students = StudentSchema()
    # students = await conn["alex_office_admin"]["movie"].find({})
    userdb = await userRepo.getUserByEmail(db, userCreate.email)


    if userdb:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    userCreate.userType = "google"
    
    newuser = await userRepo.addSocialUser(db=db, create=userCreate)
   
    if newuser is None:
        raise HTTPException(status_code=400, detail="Unable to add new user")
    return newuser


@router.put("/user",  tags=["user"])
async def updateUser( updateUser: user.UserUpdate,  db: AsyncIOMotorClient =  Depends(get_database)):

    # students = await retrieve_students()
    # students = StudentSchema()
    # students = await conn["alex_office_admin"]["movie"].find({})

    # rows = await userRepo.create_user(userCreate)
    updated = await userRepo.updateUser(db=db, update=updateUser)
   
    # if row:
    #     return Movie(**row)
  
    return updated


@router.post("/upload-image",  tags=["user"])
async def image(image: UploadFile = File(...)):
    with open("assets/images/user/destination.png", "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    return {"filename": image.filename}



@router.post("/send-email-text-template",  tags=["email"])
def send_email_text_template():
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    password = "Lll3ell-1234%"
    sender_email = "v.blue.front1@gmail.com"
    receiver_email = "belliecee@gmail.com"
    message = MIMEMultipart("alternative")

    message["Subject"] = "test with another lib"
    message["From"] = sender_email
    message["To"] = receiver_email
    
    # text = """\
    # Hi,
    # How are you?
    # Real Python has many great tutorials:
    # www.realpython.com"""
    html = """\
    <html>
                    <body style="margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, Helvetica, sans-serif;">
                    <div style="width: 100%; background: #efefef; border-radius: 10px; padding: 10px;">
                    <div style="margin: 0 auto; width: 90%; text-align: center;">
                        <h1 style="background-color: rgba(0, 53, 102, 1); padding: 5px 10px; border-radius: 5px; color: white;">Subscription</h1>
                        <div style="margin: 30px auto; background: white; width: 40%; border-radius: 10px; padding: 50px; text-align: center;">
                        <h3 style="margin-bottom: 100px; font-size: 24px;">Bell</h3>
                        <p style="margin-bottom: 30px;">Lorem ipsum dolor sit amet consectetur adipisicing elit. Eligendi, doloremque.</p>
                        <a style="display: block; margin: 0 auto; border: none; background-color: rgba(255, 214, 10, 1); color: white; width: 200px; line-height: 24px; padding: 10px; font-size: 24px; border-radius: 10px; cursor: pointer; text-decoration: none;"
                            href="https://fastapi.tiangolo.com/"
                            target="_blank"
                        >
                            Let's Go
                        </a>
                        </div>
                    </div>
                    </div>
                    </body>
                    </html>
    """


    # Turn these into plain/html MIMEText objects
    # part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")


    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    # message.attach(part1)
    message.attach(part2)
 
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
    except:
        raise HTTPException(status_code=400, detail="Unable to send email")

    
    return {"success": True}