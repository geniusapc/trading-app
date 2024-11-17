from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("deriv.html", {"request": request})

@router.get("/deriv", response_class=HTMLResponse)
async def deriv(request: Request):
    return templates.TemplateResponse("deriv.html", {"request": request})

@router.get("/tws", response_class=HTMLResponse)
async def tws(request: Request):
    return templates.TemplateResponse("tws.html", {"request": request})
