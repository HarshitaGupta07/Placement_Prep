import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-2.5-flash"

def clean_json_response(response_text):
    try:
        # Aggressive cleaning for markdown blocks (```json ... ```)
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        match = re.search(r'\[.*\]|\{.*\}', response_text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(response_text)
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        return None

def get_gemini_json(prompt):
    model = genai.GenerativeModel(MODEL_NAME)
    try:
        response = model.generate_content(prompt)
        return clean_json_response(response.text)
    except Exception as e:
        print(f"API Error: {e}")
        return None

def generate_aptitude_questions(role, company, count, resume_text=""):
    context = f"Base the technical questions heavily on skills found in this resume: {resume_text[:1000]}" if resume_text else ""
    prompt = f"""
    Generate {count} multiple-choice questions for a placement test.
    Target Role: {role} @ {company}. {context}
    
    OUTPUT EXACTLY THIS JSON ARRAY FORMAT (No markdown formatting, just raw JSON):
    [
        {{
            "id": 1,
            "q": "Question text here?",
            "options": ["Opt 1", "Opt 2", "Opt 3", "Opt 4"],
            "correct_index": 0
        }}
    ]
    """
    return get_gemini_json(prompt) or []

def generate_logic_games(count=3):
    prompt = f"""
    Generate {count} interactive logical reasoning puzzles or pattern recognition games.
    Make them fun, engaging, and relevant to a tech interview (e.g., number series, situational logic riddles, visual pattern text descriptions).
    
    OUTPUT EXACTLY THIS JSON ARRAY FORMAT:
    [
        {{
            "id": 1,
            "q": "🧩 Find the missing number in the server rack sequence: 2, 6, 12, 20, ?",
            "options": ["30", "28", "24", "32"],
            "correct_index": 0,
            "explanation": "The pattern is n^2 + n. So 5^2 + 5 = 30."
        }}
    ]
    """
    return get_gemini_json(prompt) or []

def generate_coding_questions(role, company, count, resume_text=""):
    context = f"Align the problem domain with the candidate's background: {resume_text[:1000]}" if resume_text else ""
    prompt = f"""
    Generate {count} distinct DSA/Coding problems.
    Target Role: {role} @ {company}. {context}
    
    OUTPUT EXACTLY THIS JSON ARRAY FORMAT (No markdown, just raw JSON):
    [
        {{
            "id": 1,
            "title": "Problem Title",
            "desc": "Detailed problem description...",
            "example_in": "input data",
            "example_out": "expected output"
        }}
    ]
    """
    return get_gemini_json(prompt) or []

def evaluate_code_submission(problem_desc, user_code, language):
    prompt = f"""
    Evaluate this {language} code submission for the given problem.
    Problem: {problem_desc}
    Language Used: {language}
    Code:
    {user_code}
    
    OUTPUT EXACTLY THIS JSON FORMAT (No markdown):
    {{
        "score": 8,
        "status": "Partially Correct",
        "feedback": "Logic is good, but edge cases are missing. Time complexity is O(N)."
    }}
    """
    res = get_gemini_json(prompt)
    if not res:
        return {"score": 0, "status": "Error", "feedback": "Evaluation failed to parse."}
    return res