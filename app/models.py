from pydantic import BaseModel, Field

class CodeInput(BaseModel):
    """
    Model for code input request.
    Demonstrates SRP by handling only input validation.
    """
    code: str = Field(..., description="Python code snippet to explain")

class ExplanationResponse(BaseModel):
    """
    Model for explanation response.
    Demonstrates SRP by handling only response structure.
    """
    explanation: str = Field(..., description="Generated explanation of the code") 