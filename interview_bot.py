import os
import time
import pyttsx3
import uuid
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI API Key Missing! Check .env file.")

genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = 'gemini-2.5-flash'

def get_gemini_response(prompt):
    model = genai.GenerativeModel(MODEL_NAME)
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def generate_interview_question(role, topic, difficulty, resume_text="", company_name="General"):
    context = f"Candidate's Resume Context: '{resume_text[:1500]}'" if resume_text else "No resume provided."
    prompt = f"""
    Act as a Technical Recruiter for {company_name}.
    Role: {role}
    Topic: {topic}
    Difficulty: {difficulty}
    {context}
    
    Task: Generate ONE conversational, clear technical interview question tailored to the resume (if provided) and topic.
    Output ONLY the question text. Do not include answers or formatting. Make it sound like a natural spoken question.
    """
    return get_gemini_response(prompt)

def analyze_answer(question, user_answer, resume_text=""):
    prompt = f"""
    Evaluate the candidate's answer based on the question.
    Question: {question}
    Candidate Answer: {user_answer}
    Resume Context (to gauge experience level): {resume_text[:1000]}
    
    Task: Provide structured feedback using markdown.
    Format strictly as:
    * **Rating:** ⭐ [Score/10]
    * **Strengths:** [1-2 lines on what went well]
    * **Technical Correction:** [What was factually wrong or missing]
    * **Ideal Approach:** [How to structure a better answer]
    """
    return get_gemini_response(prompt)

def analyze_resume(resume_text):
    prompt = f"""
    Act as an Expert Career Coach. Review this resume text:
    "{resume_text[:3000]}"
    
    Provide a quick, actionable analysis:
    1. **Top 3 Core Skills Detected**
    2. **Weaknesses / Missing Information** (e.g., lack of metrics, poor descriptions)
    3. **ATS Optimization Tip**
    """
    return get_gemini_response(prompt)

def text_to_speech(text):
    """Generates an audio file from text and returns the file path."""
    try:
        if not text: return None
        clean_text = text.replace("*", "").replace('"', "").replace("#", "")
        
        engine = pyttsx3.init()
        if engine._inLoop: engine.endLoop()
        
        voices = engine.getProperty('voices')
        # Try to find a female/pleasant voice for the interviewer
        for v in voices:
            if "zira" in v.name.lower() or "female" in v.name.lower():
                engine.setProperty('voice', v.id)
                break
                
        engine.setProperty('rate', 155)
        
        filename = f"interviewer_audio_{int(time.time())}_{uuid.uuid4().hex[:4]}.mp3"
        engine.save_to_file(clean_text, filename)
        engine.runAndWait()
        time.sleep(0.5) 
        
        return filename
    except Exception as e:
        print(f"TTS Error: {e}")
        return None