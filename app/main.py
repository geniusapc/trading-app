# app/main.py
from fastapi import FastAPI
from app.services.ib_client import connect_ib, disconnect_ib
from app.routers import ui, trade
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Event handlers
@app.on_event("startup")
async def startup_event():
    await connect_ib()

@app.on_event("shutdown")
async def shutdown_event():
   await disconnect_ib()


# Include routers
app.include_router(ui.router)
app.include_router(trade.router)
