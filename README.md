# AutoGen Code Explainer

A Python code explanation service using AutoGen with two agents (Clarifier and Explainer) powered by CodeLlama via Ollama.

## Prerequisites

1. Install [Ollama](https://ollama.ai/)
2. Pull the CodeLlama model:
```bash
ollama pull codellama:7b-instruct
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with:
```
OLLAMA_BASE_URL=http://localhost:11434
CODELLAMA_MODEL=codellama:7b-instruct
```

Note: We're using the `7b-instruct` variant which is optimized for instruction following and better suited for our code explanation task.

## Running the Application

1. Ensure Ollama is running:
```bash
# Check if Ollama is running and model is available
curl http://localhost:11434/api/tags
ollama list
```

2. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

3. Open http://127.0.0.1:8000 in your browser

## Project Structure

```
autogen_code_explainer/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application
│   │   ├── __init__.py
│   │   └── explainer_service.py # AutoGen logic
│   ├── agents/
│   │   ├── __init__.py
│   │   └── prompts.py          # System prompts for agents
│   └── models.py           # Pydantic models for API
├── static/
│   └── index.html         # Simple web interface
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
└── README.md
```

## SOLID Principles Implementation

1. **Single Responsibility Principle (SRP)**
   - Each class has one specific responsibility
   - ExplainerService handles only code explanation logic
   - API routes handle only HTTP request/response

2. **Open/Closed Principle (OCP)**
   - Services are open for extension but closed for modification
   - New agent types can be added without modifying existing ones

3. **Liskov Substitution Principle (LSP)**
   - AutoGen agents are designed to be substitutable
   - Different LLM backends can be swapped without breaking the system

4. **Interface Segregation Principle (ISP)**
   - Clean, focused interfaces for each component
   - No unnecessary dependencies between components

5. **Dependency Inversion Principle (DIP)**
   - High-level modules don't depend on low-level modules
   - Both depend on abstractions
   - LLM configuration is injected rather than hardcoded