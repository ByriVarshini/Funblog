from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.routers import post, user, auth_routes, protected
from fastapi.middleware.cors import CORSMiddleware
import os
from supabase import create_client, Client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = "https://hbmjmbgbuxhygzrdkeuj.supabase.co"
SUPABASE_KEY = "yeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhibWptYmdidXhoeWd6cmRrZXVqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3MTE5OTksImV4cCI6MjA2MDI4Nzk5OX0.W3C0f52r1ZPMDNIAkxG-SPaLe4KzxTi6u40VlFcWZ9Q"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
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


