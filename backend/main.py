import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

# Initialize Environment and Groq Client
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)
app = FastAPI()

# Data model for the request
class CodeReviewRequest(BaseModel):
    code: str
    language: str
    focus_areas: list 

@app.get("/", response_class=HTMLResponse)
async def serve_login():
    try:
        with open("../frontend/login.html", "r", encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>login.html not found</h1>", status_code=404)

@app.get("/app", response_class=HTMLResponse)
async def serve_tool():
    try:
        with open("../frontend/index.html", "r", encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>index.html not found</h1>", status_code=404)

@app.post("/api/review")
async def review_code(request: CodeReviewRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    # Prompt designed to simulate output and provide professional review
    prompt = f"""You are an expert developer and code auditor.
    Analyze this {request.language} code:
    {request.code}
    
    Provide your response in these exact sections:
    
    ### 🚀 Expected Execution Output
    Predict what this code will print or return if executed. If there is a logic error, explain what the output WOULD be versus what it SHOULD be.
    
    ### 🔍 Review Results
    Categorize issues by severity:
    - ### 🔴 Critical Issues
    - ### 🟠 High Priority
    - ### 🟡 Medium/Low Priority
    
    ### 💡 Refactored & Optimized Code
    Provide the corrected version of the code here.
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2500
        )
        return {"review": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)