from fastapi import FastAPI
from .fastauth import Fastauth, FastauthSettings
from fastapi.responses import RedirectResponse


app = FastAPI(root_path="/test-api")
settings = {
    "app_name": "fastauth",
    "database_api_path": "http://127.0.0.1:6789/mydb/data",
    "master_token": "kAONxbkATfyk3kmnUhw7YyAMotmvuJ6tVsuT1w3A6N4=",
    "cryptography_key": "kAONxbkATfyk3kmnUhw7YyAMotmvuJ6tVsuT1w3A6N4=",
    "headers": {},
    "master_token_paths": ["/master"],
    "access_token_paths": ["/access"],
}
auth = Fastauth(settings=settings)
auth.set_auth(app)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/access/health")
async def access_health_check():
    return {"status": "healthy", "service": "access health that need access token"}


@app.get("/master/health")
async def master_health_check():
    return {"status": "healthy", "service": "master health that need master token"}
