from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from routes.web import router as web_router
from routes.products import router as products_router
from routes.orders import router as orders_router
from routes.stats import router as stats_router
from routes.auth import router as auth_router
from routes.addresses import router as addresses_router  

app = FastAPI(
    title="SmartCartAI - India's Smartest Shopping Destination",
    description="Amazon-style e-commerce platform with Indian products and AI recommendations",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(web_router)
app.include_router(auth_router, prefix="/auth")
app.include_router(products_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(addresses_router, prefix="/api")  


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)