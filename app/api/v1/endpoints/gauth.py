
# INSTALL pyjwt / httplib2 / google-auth

from typing import Optional
from datetime import datetime, timedelta

import jwt
# from jwt import PyJWTError

from fastapi import Depends, FastAPI, HTTPException, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.security.oauth2 import (
    OAuth2,
    OAuthFlowsModel,
    get_authorization_scheme_param,
)
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse, HTMLResponse
from starlette.requests import Request

from pydantic import BaseModel

import httplib2
from oauth2client import client
from google.oauth2 import id_token
from google.auth.transport import requests

from database.mongodb  import AsyncIOMotorClient, get_database
from core.config import ACCESS_TOKEN_EXPIRE_HOURS
from models import  user
from utils import util

COOKIE_AUTHORIZATION_NAME = "Authorization"
COOKIE_DOMAIN = "localhost"

PROTOCOL = "http://"
FULL_HOST_NAME = "localhost"
PORT_NUMBER = 8000

CLIENT_ID = "753065350883-71sqo61a56gr9gv0b8noc53bc7oe33f1.apps.googleusercontent.com"
CLIENT_SECRETS_JSON = "i2X5xInGPabJ-PAPG1B_xCLy"

API_LOCATION = f"{PROTOCOL}{FULL_HOST_NAME}:{PORT_NUMBER}"
SWAP_TOKEN_ENDPOINT = "/gauth/swap_token"
SUCCESS_ROUTE = "/gauth/users/me"
ERROR_ROUTE = "/login_error"

# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


from repo import userRepo, authRepo

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None
    email: str = None


class User(BaseModel):
    username: str
    email: str = None
    full_name: str = None
    disabled: bool = None



# oauth2_scheme = (tokenUrl="/token")



def get_user_by_email(db, email: str):
    for username, value in db.items():
        if value.get("email") == email:
            user_dict = db[username]
            return User(**user_dict)



@router.get("/google_login_client", tags=["security"])
def google_login_client():

    return HTMLResponse(google_login_javascript_client)


@router.get("/google_login_server", tags=["security"])
def google_login_server():

    return HTMLResponse(google_login_javascript_server)

# https://www.vuescript.com/vue-js-plugin-google-sign-button/ *** Google Sign-in Button
# https://github.com/phanan/vue-google-signin-button *** Google Sign-in Button GITHUB

# https://vuejsexamples.com/handling-signup-or-signin-with-google-and-facebook-using-vuejs/ *** อีก Library
# https://developers.google.com/identity/sign-in/web/backend-auth *** Verify ID Token by google



class IdTokenForm(BaseModel):
    id_token: Optional[str] = None
    
@router.post("/swap_token", response_model=Token, tags=["security"])
# async def swap_token(request: Request = None):
async def swap_token(request: Request = None, db: AsyncIOMotorClient =  Depends(get_database)):
    if not request.headers.get("X-Requested-With"):
        raise HTTPException(status_code=400, detail="Incorrect headers")

    google_client_type = request.headers.get("X-Google-OAuth2-Type")


    # if google_client_type == 'server':
    #     try:
    #         body_bytes = await request.body()
    #         auth_code = jsonable_encoder(body_bytes)

    #         credentials = client.credentials_from_clientsecrets_and_code(
    #             CLIENT_SECRETS_JSON, ["profile", "email"], auth_code
    #         )

    #         http_auth = credentials.authorize(httplib2.Http())

    #         email = credentials.id_token["email"]

    #     except:
    #         raise HTTPException(status_code=400, detail="Unable to validate social login")


    if google_client_type == 'client':
        body_bytes = await request.body()
        auth_code = jsonable_encoder(body_bytes)
     
        
        # print(f"auth_code = {auth_code}")
        # print(f"id_token = {id_token}")
        print("Before validate info")
        idinfo = id_token.verify_oauth2_token(auth_code, requests.Request(), CLIENT_ID)
        # idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        print("id info can be verified")
        # print(idinfo)

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise HTTPException(status_code=400, detail="wrong issuer")

        if idinfo['email'] and idinfo['email_verified']:
            print(idinfo['email'])
            email = idinfo.get('email')

        else:
            print("email not verified")
            raise HTTPException(status_code=400, detail="email is no verified")

        # except:
        #     raise HTTPException(status_code=400, detail="Unable to validate social login")
        
        
    # *** ตรวจสอบ EMAIL ใน DATABASE
    authenticated_user = ""
    row = await db["alex_office_admin"]["user"].find_one({ "email" :  email }) 
    if row:
        aUser = user.UserDb(**row)
        print(aUser)
        authenticated_user = aUser
    else:
        print("ไม่มี  user")
        
    if not authenticated_user:
        raise HTTPException(status_code=400, detail="Incorrect email address")

    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    # *** สร้าง activeToken ใหม่ ของ RP เอง หลังเช็ค access token จาก Google
    access_token = authRepo.create_access_token(
        # data={"sub": authenticated_user.email}, expires_delta=access_token_expires
         data={"sub": email, "iss": "wtg.promo", "nonce": util.genRandomText(32) }, expires_delta=access_token_expires
    )

    token = jsonable_encoder(access_token)

    
    # print(f"time delta is  {access_token_expires}")
    
    authenticated_user.activeToken = access_token
    authenticated_user.tokenExpiredAt = datetime.now() + access_token_expires
    
    row = await db["alex_office_admin"]["user"].update_one({"email": authenticated_user.email}, {'$set': authenticated_user.dict()})

    response = JSONResponse({"access_token": token, "token_type": "bearer"})
    
    response.set_cookie(
        COOKIE_AUTHORIZATION_NAME,
        value=f"Bearer {token}",
        domain=COOKIE_DOMAIN,
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return response


# @router.get("/")
# async def homepage():
#     return "Welcome to the security test!"


@router.get(f"{ERROR_ROUTE}", tags=["security"])
async def login_error():
    return "Something went wrong logging in!"


@router.get("/logout", tags=["security"])
async def route_logout_and_remove_cookie():
    response = RedirectResponse(url="/")
    response.delete_cookie(COOKIE_AUTHORIZATION_NAME, domain=COOKIE_DOMAIN)
    return response





# @router.get("/secure_endpoint", tags=["security"])
# async def get_open_api_endpoint(current_user: User = Depends(get_current_active_user)):
#     response = "How cool is this?"
#     return response


# @router.get("/users/me/", response_model=User, tags=["users"])
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return current_user


# @router.get("/users/me/items/", tags=["users"])
# async def read_own_items(current_user: User = Depends(get_current_active_user)):
#     return [{"item_id": "Foo", "owner": current_user.username}]


google_login_javascript_client = f"""<!DOCTYPE html>
<html itemscope itemtype="http://schema.org/Article">
<head>
    <meta charset="UTF-8">
    <meta name="google-signin-client_id" content="{CLIENT_ID}">
    <title>Google Login</title><script src="https://apis.google.com/js/platform.js" async defer></script>
    <body>
    <div class="g-signin2" data-onsuccess="onSignIn"></div>
    <script>
    function onSignIn(googleUser) {{
  
  var id_token = googleUser.getAuthResponse().id_token;
    var xhr = new XMLHttpRequest();
xhr.open('POST', '{API_LOCATION}{SWAP_TOKEN_ENDPOINT}');
xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
xhr.setRequestHeader('X-Google-OAuth2-Type', 'client');
xhr.onload = function() {{
    
    
   console.log('Signed in as: ' + xhr.responseText);
}};
xhr.send(id_token);
}}</script>
<div><br></div>
<a href="#" onclick="signOut();">Sign out</a>
<script>
  function signOut() {{
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {{
      console.log('User signed out.');
    }});
  }}
</script>
</body>
</html>"""


google_login_javascript_server = f"""<!DOCTYPE html>
<html itemscope itemtype="http://schema.org/Article">
<head>
    <meta charset="UTF-8">
    <title>Google Login</title>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js">
    </script>
    <script src="https://apis.google.com/js/client:platform.js?onload=start" async defer>
    </script>
    <script>
    function start() {{
      gapi.load('auth2', function() {{
        auth2 = gapi.auth2.init({{
          client_id: '{CLIENT_ID}',  
          // Scopes to request in addition to 'profile' and 'email'
          // scope: 'additional_scope'
        }});
      }});
    }}
  </script>
</head>
<body>
<button id="signinButton">Sign in with Google</button>
<script>
  $('#signinButton').click(function() {{
    // signInCallback defined in step 6.
    auth2.grantOfflineAccess().then(signInCallback);
  }});
</script>
<script>
function signInCallback(authResult) {{
  if (authResult['code']) {{
    // Hide the sign-in button now that the user is authorized, for example:
    $('#signinButton').attr('style', 'display: none');
    // Send the code to the server
    $.ajax({{
      type: 'POST',
      url: '{API_LOCATION}{SWAP_TOKEN_ENDPOINT}',
      // Always include an `X-Requested-With` header in every AJAX request,
      // to protect against CSRF attacks.
      headers: {{
        'X-Requested-With': 'XMLHttpRequest',
        'X-Google-OAuth2-Type': 'server'
      }},
      contentType: 'application/octet-stream; charset=utf-8',
      success: function(result) {{
          location.href = '{API_LOCATION}{SUCCESS_ROUTE}'
        // Handle or verify the server response.
      }},
      processData: false,
      data: authResult['code']
    }});
  }} else {{
    // There was an error.
    console.log(e)
    location.href = '{API_LOCATION}{ERROR_ROUTE}'
  }}
}}
</script>
</body>
</html>"""