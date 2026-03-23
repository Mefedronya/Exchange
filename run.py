from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.registrarion import router as registration_router
from api.authent import router as auth_router
from api.virt_currency import router as currency_router
from api.chats import router as chats_router
from api.reviews import router as reviews_router
from api.lessons import router as lessons_router
from api.user_schedule import router as user_schedule_router

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
app.include_router(auth_router, prefix="/auth")
app.include_router(currency_router)
app.include_router(chats_router)
app.include_router(reviews_router)
app.include_router(lessons_router)
app.include_router(user_schedule_router)
@app.get("/")
def read_root():
    return {"message": "API работает"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
