# 🚀 Placement Buddy AI: Your Personal AI Interviewer & Assessment Platform

![Placement Buddy]

**Placement Buddy AI** is a comprehensive, intelligent, and interactive platform designed to revolutionize how candidates prepare for job interviews. Built specifically for hackathons, this platform combines the power of Generative AI (Gemini), real-time computer vision (MediaPipe), and seamless cloud databases (MongoDB) to deliver a true 1-on-1 interview experience.

## ✨ Key Features

### 🎥 1. Live 1-on-1 AI Interviewer
* **Context-Aware Questions:** Generates highly relevant technical and HR questions based on the candidate's target role, company, and difficulty level.
* **Audio-First Experience:** Features a text-to-speech AI voice that asks questions out loud, making it feel like a real interview.
* **Browser-Native STT (Speech-to-Text):** Answers are spoken by the user and transcribed in real-time instantly using a seamless in-browser STT engine.
* **Instant Evaluation:** Provides immediate, constructive feedback on the candidate's answers using Google's Gemini AI.

### 👁️ 2. Real-Time Posture & Eye-Contact Coach
* **Computer Vision Integration:** Uses OpenCV and MediaPipe to track the candidate's facial landmarks and body posture in real-time.
* **Non-Verbal Feedback:** Analyzes if the candidate is maintaining proper eye contact and sitting posture, which are crucial for interview success.

### 📝 3. Resume-Driven Personalized Tests
* **AI-Generated Assessments:** Creates custom 3-round assessments tailored to the specific skills found in the uploaded resume.
* **Round 1 (Aptitude & Core):** Multiple-choice questions testing fundamental knowledge.
* **Round 2 (Logic & Pattern Games):** Interactive puzzles testing problem-solving speed and logical reasoning.
* **Round 3 (Multi-Language Coding):** Technical coding rounds supporting popular languages (Python, C, C++, Java, JS, PHP) with real-time AI code evaluation and scoring.
* **⚡ Fast Mode:** Utilizes parallel execution (Multi-threading) to generate entire multi-round test papers in under 5 seconds!

### 📊 4. Profile Analysis & History Tracking
* **Resume Feedback:** Extracts insights from uploaded PDFs to provide actionable advice on improving the resume.
* **MongoDB Integration:** Securely saves all interview transcripts, test scores, and detailed feedback to a live MongoDB Atlas cluster.
* **Session Continuity:** Candidates can review their past performance and track their improvement over time.

## 🛠️ Technology Stack

* **Frontend & UI:** [Streamlit] (Python)
* **AI Model:** Google Gemini (via `google-generativeai`)
* **Computer Vision:** OpenCV, MediaPipe
* **Audio Processing:** gTTS (Text-to-Speech), `streamlit-mic-recorder` (Native Browser STT)
* **Database:** MongoDB Atlas (via `pymongo`)
* **PDF Parsing:** PyPDF2
* **Concurrency:** Python `concurrent.futures`
  
