from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Import your AI teacher class
from src.ai_iit_teacher import IIT_Teacher

load_dotenv()

app = FastAPI(title="IIT JEE AI Tutor API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    subject: str = "maths"  # default subject

class ChatResponse(BaseModel):
    response: str
    status: str

# Initialize AI teachers for each subject
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise Exception("Please set GOOGLE_API_KEY environment variable")

# Create teacher instances
#teachers = {
#    "maths": IIT_Teacher("maths", api_key),
#    "physics": IIT_Teacher("physics", api_key),
#    "chemistry": IIT_Teacher("chemistry", api_key)
#}

@app.get("/", response_class=HTMLResponse)
async def read_index():
    """Serve the main HTML page"""
    with open("templates/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat requests from the frontend"""
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Determine which subject teacher to use
        subject = request.subject.lower()
        if subject not in ["maths", "physics", "chemistry"]:
            subject = "maths"  # default fallback
        
        # Get response from your AI teacher
        teacher = IIT_Teacher(subject, api_key)
        ai_response = teacher.teach(request.message)
        
        return ChatResponse(
            response=ai_response,
            status="success"
        )
        
    except Exception as e:
        print(f"Error: {e}")  # For debugging
        raise HTTPException(status_code=500, detail="Sorry, I encountered an error. Please try again.")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "AI Tutor API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)