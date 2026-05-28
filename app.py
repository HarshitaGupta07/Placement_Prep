import streamlit as st
import cv2
import time
from datetime import datetime
import PyPDF2
import base64
import os
import concurrent.futures

# Modern STT Library
from streamlit_mic_recorder import speech_to_text

# Custom Modules
import interview_bot
import posture_check
import test_bot
import db_connect  

# ---------------------------------------------------------
# HELPER FUNCTION: AUTO-PLAY AUDIO (INVISIBLE)
# ---------------------------------------------------------
def autoplay_audio(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay style="display:none">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        print(f"Autoplay Error: {e}")

# ---------------------------------------------------------
# 1. UI CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="Placement Buddy", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FAF3E0; color: #3E2723; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    h1, h2, h3 { color: #4E342E !important; font-weight: 700; letter-spacing: 0.5px; }
    section[data-testid="stSidebar"] { background-color: #EBC7A8; border-right: 2px solid #8D6E63; }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] p { color: #2b1b17 !important; font-weight: 700; }
    .stTextInput > div > div > input, .stSelectbox > div > div > div, .stTextArea > div > div > textarea { background-color: #FFFDF5; color: #3E2723; border: 2px solid #8D6E63; border-radius: 8px; }
    .stButton > button { background-color: #C17A46; color: #FFFFFF; border: 2px solid #5D4037; border-radius: 8px; font-weight: 700; text-transform: uppercase; transition: all 0.1s ease; }
    .stButton > button:hover { background-color: #A0522D; color: #FFFFFF; transform: translateY(2px); }
    .user-box, .ai-box { padding: 18px; border-radius: 12px; margin-bottom: 20px; font-size: 16px; border: 2px solid #8D6E63; }
    .ai-box { background-color: #FFE4C4; border-left: 8px solid #D2691E; }
    .user-box { background-color: #FFFFFF; text-align: right; border-right: 8px solid #8D6E63; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SESSION STATES
# ---------------------------------------------------------
if 'question' not in st.session_state: st.session_state['question'] = None
if 'audio_file' not in st.session_state: st.session_state['audio_file'] = None
if 'resume_text' not in st.session_state: st.session_state['resume_text'] = ""
if 'answer_input' not in st.session_state: st.session_state['answer_input'] = ""
if 'resume_analysis' not in st.session_state: st.session_state['resume_analysis'] = None
if 'history' not in st.session_state: st.session_state['history'] = [] 

if 'test_stage' not in st.session_state: st.session_state['test_stage'] = 'setup'
if 'r1_questions' not in st.session_state: st.session_state['r1_questions'] = []
if 'r1_answers' not in st.session_state: st.session_state['r1_answers'] = {}
if 'r1_score' not in st.session_state: st.session_state['r1_score'] = 0

if 'r1.5_questions' not in st.session_state: st.session_state['r1.5_questions'] = []
if 'r1.5_answers' not in st.session_state: st.session_state['r1.5_answers'] = {}
if 'r1.5_score' not in st.session_state: st.session_state['r1.5_score'] = 0

if 'r2_questions' not in st.session_state: st.session_state['r2_questions'] = []
if 'r2_responses' not in st.session_state: st.session_state['r2_responses'] = {}

# ---------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    st.title("Placement Buddy😎")
    page = st.radio("Navigate", ["🎥 Live Interview", "📝 Personalized Test", "📊 Resume & History"])
    
    st.divider()
    st.subheader("👤 Candidate Profile")
    username = st.text_input("Candidate Name", "Devanshu", key="sb_name")
    target_role = st.selectbox("Target Role", ["Software Engineer", "Frontend Developer", "Backend Developer", "Data Scientist", "AI/ML Engineer"], key="sb_role")
    target_company = st.selectbox("Target Company", ["Google", "Microsoft", "Amazon", "Startups", "TCS/Infosys"], key="sb_comp")
    difficulty = st.select_slider("Difficulty", options=["Easy", "Medium", "Hard"], value="Medium", key="sb_diff")
    
    st.divider()
    st.subheader("📄 Resume Upload")
    uploaded_file = st.file_uploader("Upload PDF Resume to personalize AI", type="pdf", key="sb_resume")
    if uploaded_file:
        try:
            reader = PyPDF2.PdfReader(uploaded_file)
            st.session_state['resume_text'] = "".join([page.extract_text() for page in reader.pages])
            st.success("Resume Active & Read!")
        except: 
            st.error("Error reading PDF")

    if db_connect.sessions_collection is not None:
        st.caption("🟢 Database Connected")
    else:
        st.caption("🔴 Database Offline")

# ---------------------------------------------------------
# 4. PAGE LOGIC
# ---------------------------------------------------------

if page == "🎥 Live Interview":
    st.title("🎥 1-on-1 AI Interviewer")
    
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        st.subheader("Real-Time Q&A")
        topic = st.text_input("Focus Area (e.g., Python, System Design)", "DSA", key="t1_topic")
        
        if st.button("Generate Audio Question 🎲", key="t1_gen"):
            with st.spinner("AI is thinking..."):
                q = interview_bot.generate_interview_question(
                    target_role, topic, difficulty, st.session_state['resume_text'], target_company
                )
                st.session_state['question'] = q
                st.session_state['audio_file'] = interview_bot.text_to_speech(q)
                st.session_state['answer_input'] = ""
        
        if st.session_state['question']:
            st.markdown(f'<div class="ai-box">🤖 <b>AI:</b> {st.session_state["question"]}</div>', unsafe_allow_html=True)
            if st.session_state['audio_file']:
                autoplay_audio(st.session_state['audio_file'])
            
            st.markdown("**🎙️ Your Turn to Answer:**")
            
            spoken_text = speech_to_text(
                language='en', 
                start_prompt="Click to Speak", 
                stop_prompt="Stop Recording", 
                just_once=True,
                key='STT'
            )
            
            if spoken_text:
                st.session_state['answer_input'] = spoken_text
                
            st.session_state['answer_input'] = st.text_area(
                "Your Answer Transcript", 
                value=st.session_state['answer_input'], 
                height=150
            )
            
            if st.button("Submit & Evaluate", key="t1_sub"):
                if st.session_state['answer_input'].strip():
                    with st.spinner("Evaluating response..."):
                        fb = interview_bot.analyze_answer(st.session_state['question'], st.session_state['answer_input'], st.session_state['resume_text'])
                        st.markdown(f"### Evaluation\n{fb}")
                        
                        doc = {
                            "user": username, 
                            "type": "Interview", 
                            "q": st.session_state['question'], 
                            "a": st.session_state['answer_input'], 
                            "fb": str(fb), 
                            "time": datetime.now()
                        }
                        st.session_state['history'].append(doc)
                        
                        if db_connect.sessions_collection is not None:
                            db_connect.sessions_collection.insert_one(doc)
                else:
                    st.warning("Please provide an answer first.")

    with c2:
        st.subheader("Posture & Eye-Contact Coach")
        if st.toggle("Enable Camera Monitoring", key="t1_cam"):
            st.info("Ensure proper lighting for accurate tracking.")
            analyzer = posture_check.PostureAnalyzer()
            cap = cv2.VideoCapture(0)
            ph = st.empty()
            while True:
                ret, frame = cap.read()
                if not ret: 
                    st.error("Failed to access camera.")
                    break
                frame, status = analyzer.process_frame(frame)
                ph.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption=status)
                time.sleep(0.05)
            cap.release()

elif page == "📝 Personalized Test":
    st.title("📝 Resume-Driven Placement Test")

    if st.session_state['test_stage'] == 'setup':
        st.info("The AI will generate a 3-Round test: Aptitude, Logic Games, and Multi-Language Coding.")
        c1, c2, c3 = st.columns(3)
        with c1:
            r1_count = st.selectbox("Aptitude Questions", [5, 10, 20, 30])
        with c2:
            r15_count = st.selectbox("Logic/Pattern Games", [3, 5, 10])
        with c3:
            r2_count = st.selectbox("Coding Problems", [1, 2, 5])
            
        if st.button("🚀 Generate My Custom Test (Fast Mode)"):
            with st.spinner("Analyzing Resume & Generating Papers simultaneously... ⚡"):
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_apt = executor.submit(test_bot.generate_aptitude_questions, target_role, target_company, r1_count, st.session_state['resume_text'])
                    future_log = executor.submit(test_bot.generate_logic_games, r15_count)
                    future_cod = executor.submit(test_bot.generate_coding_questions, target_role, target_company, r2_count, st.session_state['resume_text'])
                    
                    qs_apt = future_apt.result()
                    qs_logic = future_log.result()
                    qs_code = future_cod.result()
                
                if qs_apt and qs_code:
                    st.session_state['r1_questions'] = qs_apt
                    st.session_state['r1_answers'] = {i: None for i in range(len(qs_apt))}
                    st.session_state['r1.5_questions'] = qs_logic
                    st.session_state['r1.5_answers'] = {i: None for i in range(len(qs_logic))}
                    st.session_state['r2_questions'] = qs_code
                    st.session_state['test_stage'] = 'r1_active'
                    st.rerun()
                else:
                    st.error("AI could not generate questions. Try clicking Generate again.")

    elif st.session_state['test_stage'] == 'r1_active':
        st.subheader("🧠 Round 1: Aptitude & Core Fundamentals")
        with st.form("r1_form"):
            for idx, q_data in enumerate(st.session_state['r1_questions']):
                st.markdown(f"**Q{idx+1}. {q_data['q']}**")
                st.session_state['r1_answers'][idx] = st.radio("Options", q_data['options'], key=f"r1_q_{idx}", index=None, label_visibility="collapsed")
                st.divider()
            
            if st.form_submit_button("✅ Submit Round 1"):
                score = sum(1 for idx, q in enumerate(st.session_state['r1_questions']) if st.session_state['r1_answers'].get(idx) and q['options'].index(st.session_state['r1_answers'][idx]) == q.get('correct_index'))
                st.session_state['r1_score'] = score
                st.session_state['test_stage'] = 'r1.5_active'
                st.rerun()

    elif st.session_state['test_stage'] == 'r1.5_active':
        st.success(f"Round 1 Complete! Score: {st.session_state['r1_score']}/{len(st.session_state['r1_questions'])}")
        st.subheader("🧩 Round 2: Logic & Pattern Games")
        
        with st.form("r15_form"):
            for idx, q_data in enumerate(st.session_state['r1.5_questions']):
                st.markdown(f"**Game {idx+1}: {q_data['q']}**")
                st.session_state['r1.5_answers'][idx] = st.radio("Choose the correct pattern:", q_data['options'], key=f"r15_q_{idx}", index=None)
                st.divider()
            
            if st.form_submit_button("🎮 Submit Round 2"):
                score = sum(1 for idx, q in enumerate(st.session_state['r1.5_questions']) if st.session_state['r1.5_answers'].get(idx) and q['options'].index(st.session_state['r1.5_answers'][idx]) == q.get('correct_index'))
                st.session_state['r1.5_score'] = score
                st.session_state['test_stage'] = 'r2_active'
                st.rerun()

    elif st.session_state['test_stage'] == 'r2_active':
        st.success(f"Round 2 Complete! Score: {st.session_state['r1.5_score']}/{len(st.session_state['r1.5_questions'])}")
        st.subheader("💻 Round 3: Multi-Language Technical Coding")
        tabs = st.tabs([f"Problem {i+1}" for i in range(len(st.session_state['r2_questions']))])
        
        for i, tab in enumerate(tabs):
            q = st.session_state['r2_questions'][i]
            with tab:
                st.markdown(f"### {q['title']}\n{q['desc']}")
                st.info(f"**Example Input:** `{q['example_in']}` | **Output:** `{q['example_out']}`")
                
                lang = st.selectbox("Programming Language", ["Python", "C", "C++", "Java", "JavaScript", "PHP"], key=f"lang_{i}")
                code = st.text_area(f"Write your {lang} Code here:", height=200, key=f"code_{i}")
                
                if st.button(f"Submit Code {i+1}", key=f"sub_code_{i}"):
                    with st.spinner(f"Evaluating {lang} logic..."):
                        eval_res = test_bot.evaluate_code_submission(q['desc'], code, lang)
                        st.session_state['r2_responses'][i] = eval_res
                        st.success(f"Score: {eval_res.get('score', 0)}/10")
                        st.json(eval_res)
        
        st.divider()
        if st.button("🏁 Finish & Save Entire Test"):
            # --- DETAILED FEEDBACK STRING BUILDER ---
            detailed_fb = f"**🧠 Aptitude:** {st.session_state['r1_score']}/{len(st.session_state['r1_questions'])}\n\n"
            detailed_fb += f"**🧩 Logic Games:** {st.session_state['r1.5_score']}/{len(st.session_state['r1.5_questions'])}\n\n"
            detailed_fb += "**💻 Coding Performance:**\n"
            
            if not st.session_state['r2_responses']:
                detailed_fb += "- No coding problems were attempted.\n"
            else:
                for i, res in st.session_state['r2_responses'].items():
                    detailed_fb += f"- **Problem {i+1}:** Score: {res.get('score', 0)}/10 [{res.get('status', 'Unattempted')}]\n  > *Feedback: {res.get('feedback', 'No feedback')}*\n\n"
            
            test_doc = {
                "user": username,
                "type": "Test Exam",
                "score": f"Apt: {st.session_state['r1_score']}/{len(st.session_state['r1_questions'])}, Logic: {st.session_state['r1.5_score']}/{len(st.session_state['r1.5_questions'])}",
                "details": detailed_fb,
                "time": datetime.now()
            }
            
            st.session_state['history'].append(test_doc)
            
            if db_connect.sessions_collection is not None:
                db_connect.sessions_collection.insert_one(test_doc)
                
            st.success("Test saved successfully! Check the History tab.")
            st.session_state['test_stage'] = 'setup'
            time.sleep(1.5)
            st.rerun()

elif page == "📊 Resume & History":
    st.title("📊 Profile Analysis & History")
    
    # --- FIXED: SMART RESUME CHECK (IMAGE-PDF FALLBACK) ---
    if st.button("Analyze Uploaded Resume"):
        if uploaded_file is not None: # Directly checking if file exists, not just text
            eval_text = st.session_state.get('resume_text', '')
            
            # Agar PyPDF2 text nahi nikal paya (Image PDF), toh app crash ya error nahi degi
            if not eval_text.strip():
                eval_text = f"Candidate is applying for {target_role} at {target_company}. The uploaded resume is visual/image-based and text couldn't be extracted. Provide a strong general profile analysis and resume-building tips for this specific role."
            
            with st.spinner("Extracting insights using AI..."):
                st.session_state['resume_analysis'] = interview_bot.analyze_resume(eval_text)
        else:
            st.warning("⚠️ Please upload a resume from the sidebar first!")
            
    if st.session_state.get('resume_analysis'):
        st.markdown("### 📄 Resume Feedback")
        st.markdown(st.session_state['resume_analysis'])
        st.divider()
    
    st.subheader("Recent Activity (Database)")
    
    if db_connect.sessions_collection is not None:
        data = list(db_connect.sessions_collection.find({"user": username}).sort("time", -1).limit(15))
    else:
        data = reversed(st.session_state['history'])
        
    if not data:
        st.info(f"No activity recorded yet for {username}.")
    else:
        for d in data:
            with st.expander(f"{d.get('time').strftime('%d %b, %I:%M %p')} | {d.get('type')}"):
                if d.get('type') == "Interview":
                    st.write(f"**Q:** {d.get('q')}")
                    st.write(f"**A:** {d.get('a')}")
                    st.markdown(d.get('fb'))
                elif d.get('type') == "Test Exam":
                    st.write(f"**Total Score Overview:** {d.get('score')}")
                    st.divider()
                    st.markdown(d.get('details'))