from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes.product import router as product_router
from backend.app.api.routes.social import router as social_router


app = FastAPI()


origins = [
    "*",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router)
app.include_router(social_router)


@app.get("/")
def health():
    return {"status": "ok"}