from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.routers import post, user, auth_routes, protected
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",   # Local frontend
        "http://localhost:8000",   # Just in case
        "https://varshu-funblog.onrender.com"  # Replace with your actual deployed frontend URL if needed
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static folder for serving CSS/JS files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Register routers
app.include_router(user.router)
app.include_router(post.router)
app.include_router(auth_routes.router)
app.include_router(protected.router)



# Path to index.html
INDEX_PATH = os.path.join("app", "static", "index.html")

@app.get("/", response_class=FileResponse)
def serve_homepage():
    return FileResponse(INDEX_PATH)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)


