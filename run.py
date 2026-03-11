from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.registrarion import router as registration_router
from api.authent import router as auth_router
from api.virt_currency import router as currency_router

app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов
app.include_router(registration_router)
app.include_router(auth_router)
app.include_router(currency_router)

@app.get("/")
def read_root():
    return {"message": "API работает"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
