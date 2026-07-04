from fastapi import FastAPI, Request,Form,HTTPException,Depends
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from auth import SECRET_KEY
from starlette.middleware.sessions import SessionMiddleware
from db import TeamMember,Client,User,Tickets



app=FastAPI()

app.add_middleware(SessionMiddleware,secret_key=SECRET_KEY)

app.mount("/static",StaticFiles(directory="templates/css"),name="static")

templates=Jinja2Templates(directory="templates")


def get_current_user(request: Request)->dict:
    user_id = request.session.get("id")
    user_role=request.session.get("role")
    if not user_id or not user_role:
        raise HTTPException(status_code=401)
    if user_role=="team_member":
        user_info=TeamMember.member_info(user_id)
    elif user_role=="client":
        user_info=Client.client_info(user_id)
    else:
        raise HTTPException(status_code=403)
    if user_info is None:
        raise HTTPException(status_code=401)
    return user_info    


@app.get("/",response_class=HTMLResponse)
def initial_page(request:Request):
    return templates.TemplateResponse(request,name="index.html")
    

@app.get("/create_account",response_class=HTMLResponse)
def create_account_get(request:Request):
    return templates.TemplateResponse(request,name="pages/create_account.html")


@app.get("/profile/team_member")
def profile_team_member(request:Request,user_id:dict=Depends(get_current_user)):
    if request.session.get("role")!="team_member":
        raise HTTPException(status_code=401)
    tickets=Tickets.see_all_open_tickets()
    return templates.TemplateResponse(request,name="pages/profile.html",context={"user_id":user_id,"tickets":tickets})


@app.get("/profile/client")
def profile_client(request:Request,user_id:dict=Depends(get_current_user)):
    if request.session.get("role")!="client":
        raise HTTPException(status_code=401)
    return templates.TemplateResponse(request,name="pages/client_interface.html",context={"user_id":user_id})


@app.post("/",response_class=HTMLResponse)
def login(request:Request,email:str=Form(),password:str=Form()):
    user_id=User.login(email,password)
    request.session["id"]=user_id[0]
    request.session["role"]=user_id[1]
    return RedirectResponse(url=f"/profile/{user_id[1]}",status_code=302)


@app.post("/create_account",response_class=HTMLResponse)
def create_account_post(request:Request,name:str=Form(),email:str=Form(),phone_number:str=Form(),password:str=Form()):
    Client.new_client(name,email,phone_number,password)
    return RedirectResponse(url="/",status_code=302)


@app.post("/logout")
def profile_logout(request:Request):
    request.session.clear()
    return RedirectResponse(url="/",status_code=302)


@app.post("/receive/tickets/{id}")
def receive_tickets(request:Request,id:int,title:str=Form(),msg:str=Form()):
    Tickets.new_ticket(title,msg,id)
    return RedirectResponse(url="/profile/client",status_code=302)

