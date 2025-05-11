"""
FastAPI application for the code explainer service.
Demonstrates SOLID principles in API design.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv
import logging

from app.models import CodeInput, ExplanationResponse
from app.services.explainer_service import ExplainerService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate environment variables early
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL")
MODEL_NAME = os.getenv("CODELLAMA_MODEL")

if not OLLAMA_URL or not MODEL_NAME:
    logger.error("Required environment variables are not set!")
    logger.error(f"OLLAMA_BASE_URL: {'set' if OLLAMA_URL else 'not set'}")
    logger.error(f"CODELLAMA_MODEL: {'set' if MODEL_NAME else 'not set'}")
    logger.error("Please create a .env file in the project root with these variables.")

app = FastAPI(
    title="AutoGen Code Explainer",
    description="API to explain Python code snippets using AutoGen and CodeLlama.",
    version="0.1.0"
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_explainer_service() -> ExplainerService:
    """
    Dependency injection for ExplainerService.
    Demonstrates DIP by providing service configuration through environment.
    """
    ollama_url = os.getenv("OLLAMA_BASE_URL")
    model_name = os.getenv("CODELLAMA_MODEL")
    
    if not ollama_url or not model_name:
        error_msg = (
            "Environment variables not set. Please create a .env file with:\n"
            "OLLAMA_BASE_URL='http://localhost:11434'\n"
            "CODELLAMA_MODEL='codellama:7b'"
        )
        logger.error(error_msg)
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )
    
    return ExplainerService(ollama_base_url=ollama_url, model_name=model_name)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root():
    """Serve the HTML interface."""
    try:
        with open("static/index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        error_msg = "Error: index.html not found. Make sure static/index.html exists."
        logger.error(error_msg)
        return HTMLResponse(
            content=f"<h1>{error_msg}</h1>",
            status_code=500
        )

@app.post("/explain/", response_model=ExplanationResponse)
async def explain_code_endpoint(
    code_input: CodeInput,
    explainer_service: ExplainerService = Depends(get_explainer_service)
):
    """
    Endpoint to explain Python code.
    Demonstrates SRP by handling only the HTTP interface for code explanation.
    """
    if not code_input.code.strip():
        raise HTTPException(status_code=400, detail="Code snippet cannot be empty.")
    
    try:
        explanation = await explainer_service.explain_code(code_input.code)
        return ExplanationResponse(explanation=explanation)
    except Exception as e:
        error_msg = f"Error during explanation: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint that also validates environment configuration.
    """
    env_status = {
        "ollama_url": bool(os.getenv("OLLAMA_BASE_URL")),
        "model_name": bool(os.getenv("CODELLAMA_MODEL")),
    }
    
    if all(env_status.values()):
        return {"status": "healthy", "config": env_status}
    else:
        return {
            "status": "misconfigured",
            "config": env_status,
            "message": "Some environment variables are missing. Please check .env file."
        }

# To run: uvicorn app.main:app --reload 