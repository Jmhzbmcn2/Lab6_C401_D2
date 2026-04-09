from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.utils.logger import get_logger

logger = get_logger()

app = FastAPI(title="Vinmec RAG Graph API")

# Add CORS so Vue frontend can call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
def startup_event():
    logger.info("FastAPI Application Started")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
