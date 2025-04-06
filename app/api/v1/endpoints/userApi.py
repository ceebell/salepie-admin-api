from typing import List, Optional , Any, Dict

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks


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


router = APIRouter()


class Movie(BaseModel):
    name: Optional[str] = ""
    

async def get_user(conn: AsyncIOMotorClient) -> Movie:
    # row = await conn[database_name][users_collection_name].find_one({"username": username})
    row = await conn["alex_office_admin"]["movie"].find_one()
    if row:
        return Movie(**row)

async def get_multiple(conn: AsyncIOMotorClient) -> List[Movie]:
    # row = await conn[database_name][users_collection_name].find_one({"username": username})
    mm = []

    #*** ถ้าเป็น list ไม่ต้องใส่ await ใช้ async ตรง for
    rows = conn["alex_office_admin"]["movie"].find()

    # async for row in rows:
    #     mm.append(Movie(**row))
    # Movie(**row)

    xx =   [Movie(**row) async for row in rows]


    return xx
    


@router.get("/getUserList",  tags=["user"] ,  response_model=List[user.UserView])
async def getUserList(db: AsyncIOMotorClient =  Depends(get_database)):
   
    try:
        rows = db["ecouponv1"]["user"].find({})
        xx =   [user.UserView(**row) async for row in rows]
    except:
        raise HTTPException(status_code=400, detail="Unable to get user list")

    return xx

@router.post("/get-user-in-domain/{id}",  tags=["user"] ,  response_model=List[user.UserForView])
async def getUserInDomain(id: str, SearchForm: user.SearchForm,  db: AsyncIOMotorClient =  Depends(get_database),  currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
   
    try:
        rows = db["ecouponv1"]["user"].find({ "domainId" : id })
        xx =   [user.UserForView(**row) async for row in rows]
    except:
        raise HTTPException(status_code=400, detail="Unable to get user list")

    return xx


@router.post("/change-user-status",  tags=["user"] )
async def changeUserStatus( searchForm : user.SearchForm,  db: AsyncIOMotorClient =  Depends(get_database),  currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
    print(f"searchForm >>> ",searchForm.uid)
    try:
        row = await db["ecouponv1"]["user"].find_one({ "uid" : searchForm.uid })
        userDb =   user.UserDb(**row) 
    except:
        raise HTTPException(status_code=400, detail="Unable to get user")
    
    userDb.admin = searchForm.admin
    edit = await db["ecouponv1"]["user"].update_one({"uid": searchForm.uid}, {'$set': userDb.dict() })

    return "OK"

@router.post("/delete-user",  tags=["user"] )
async def deleteUserInDomain( searchForm : user.SearchForm,  db: AsyncIOMotorClient =  Depends(get_database),  currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
    print(f"searchForm >>> ",searchForm.uid)
    try:
        result  = await db["ecouponv1"]["user"].delete_one({ "uid" : searchForm.uid })
       
    except:
        raise HTTPException(status_code=400, detail="Unable to delete user")
    
    return "OK" # {"deleted_count": result.deleted_count}


@router.post("/add-user-in-domain/{domainId}",  tags=["user"])
async def createUserInDomain( domainId: str, userCreate: user.UserCreate,  db: AsyncIOMotorClient =  Depends(get_database),  currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
    # students = await retrieve_students()
    # students = StudentSchema()
    # students = await conn["alex_office_admin"]["movie"].find({})
    userdb = await userRepo.getUserByEmail(db, userCreate.username)


    if userdb:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    
    # newuser = await userRepo.createUser(db=db, create=userCreate)
    dbuser = user.UserDb(**userCreate.dict())
    # dbuser.change_password(user.password)
    dbuser.uid = util.getUuid()
    dbuser.hashedPassword = authRepo.get_password_hash(userCreate.password)
    dbuser.domainId = domainId
    row = await db["ecouponv1"]["user"].insert_one(dbuser.dict())
   
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





@router.post("/user",  tags=["user"])
async def createUser( userCreate: user.UserCreate,  db: AsyncIOMotorClient =  Depends(get_database)):
    # students = await retrieve_students()
    # students = StudentSchema()
    # students = await conn["alex_office_admin"]["movie"].find({})
    userdb = await userRepo.getUserByEmail(db, userCreate.email)


    if userdb:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    newuser = await userRepo.createUser(db=db, create=userCreate)
   
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




# @router.post("/uploadfiles/",  tags=["user"])
# async def create_upload_files(files: List[UploadFile] = File(...), username: Optional[str] = "",  db: AsyncIOMotorClient =  Depends(get_database)):
    
#     userdb = await userRepo.getUserByEmail(db, username)
#     if not userdb:
#         raise HTTPException(status_code=400, detail="User not found") 
    
   
    
#     u = []
    
#     for file in files:
#         new_guid = util.getUuid()
#         tmp_file_name = file.filename.split(".")
#         new_file_name = f"{new_guid}.{tmp_file_name[1]}"
#         with open(f"assets/images/user/{new_file_name}", "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
#         print(file)
#         a = dict()
#         a["id"] = new_guid
#         a["name"] = f"{new_file_name}"
#         # a["size"] = file.size
        
#         u.append(a)
        
#     print(u)
     
#     # **** UNCOMMENT!!!!! to save into database
#     udb = await userRepo.updateImage(db=db, userdb=userdb, imageList=u )
    
#     view = user.UserView(**udb)
        
#     return view
        
        


# @router.post("/upload-multiple-files",  tags=["user"])
# async def upload_multiple_files(files: List[UploadFile] = File(...)):
#     u = []

    
#     for file in files:
#         print(f"file size>>> {len(file)}")

#         new_guid = util.getUuid()
#         tmp_file_name = file.filename.split(".")
#         new_file_name = f"{new_guid}.{tmp_file_name[1]}"
#         with open(f"assets/images/user/{new_file_name}", "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
#         print(file)
#         a = dict()
#         a["id"] = new_guid
#         a["name"] = f"{new_file_name}"
#         # a["size"] = file.size
        
#         u.append(a)
        
#     print(f"assets/images/user/{new_file_name}")
    

        
    # return view


# conf = ConnectionConfig(
#     MAIL_USERNAME=AlexEmail.MAIL_USERNAME,
#     MAIL_PASSWORD=AlexEmail.MAIL_PASSWORD,
#     MAIL_FROM=AlexEmail.MAIL_FROM,
#     MAIL_PORT=AlexEmail.MAIL_PORT,
#     MAIL_SERVER=AlexEmail.MAIL_SERVER,
#     MAIL_FROM_NAME=AlexEmail.MAIL_FROM_NAME,
#     MAIL_TLS = True,
#     MAIL_SSL = False,
#     USE_CREDENTIALS = True,
#     VALIDATE_CERTS = True,
#     TEMPLATE_FOLDER='templates'
# )


# @router.post("/send-email",  tags=["email"])
# async def SendEmail(subject: str, email_to: str, body: str):
#     message = MessageSchema(
#         subject=subject,
#         recipients=[email_to],
#         body=body,
#         subtype='html',
#     )
    
#     html = """\
#             <html>
#                 <body style="margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, Helvetica, sans-serif;">
#                 <div style="width: 100%; background: #efefef; border-radius: 10px; padding: 10px;">
#                 <div style="margin: 0 auto; width: 90%; text-align: center;">
#                     <h1 style="background-color: rgba(0, 53, 102, 1); padding: 5px 10px; border-radius: 5px; color: white;">Subscription</h1>
#                     <div style="margin: 30px auto; background: white; width: 40%; border-radius: 10px; padding: 50px; text-align: center;">
#                     <h3 style="margin-bottom: 100px; font-size: 24px;">Bell</h3>
#                     <p style="margin-bottom: 30px;">Lorem ipsum dolor sit amet consectetur adipisicing elit. Eligendi, doloremque.</p>
#                     <a style="display: block; margin: 0 auto; border: none; background-color: rgba(255, 214, 10, 1); color: white; width: 200px; line-height: 24px; padding: 10px; font-size: 24px; border-radius: 10px; cursor: pointer; text-decoration: none;"
#                         href="https://fastapi.tiangolo.com/"
#                         target="_blank"
#                     >
#                         Let's Go
#                     </a>
#                     </div>
#                 </div>
#                 </div>
#                 </body>
#                 </html>
#             """
    
#     fm = FastMail(conf)
#     await fm.send_message(message, template_name='email.html')
    
#     return {"success": True}

# @router.post("/send-email-with-bg",  tags=["email"])
# def send_email_background(background_tasks: BackgroundTasks, subject: str, email_to: str, body: str):
#     message = MessageSchema(
#         subject=subject,
#         recipients=[email_to],
#         body=body,
#         subtype='html',
#     )
#     fm = FastMail(conf)
#     background_tasks.add_task(
#        fm.send_message, message, template_name='email.html')
    
#     return {"success": True}


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