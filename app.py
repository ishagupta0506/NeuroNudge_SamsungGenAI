import streamlit as st
import time
import random
from datetime import datetime, timedelta
import os
import glob
import random
from db import *

import sqlite3

sound_patterns = {
    "Rain": "rain",
    "Forest": "forest",
    "Cafe": "cafe",
    "WhiteNoise": "whitenoise",
    "Bird": "bird",
    "Fire": "fire",
    "Nature": "nature"}

audio_folder = "assets/audio"
audio_files = glob.glob(f"{audio_folder}/*.mp3")
def update_current_audio():
    if st.session_state.sound != "None":
        matching_files = [
            file for file in audio_files
            if sound_patterns[st.session_state.sound].lower() in file.lower()
        ]
        
        if matching_files:
            selected_file = random.choice(matching_files)
            st.session_state.current_audio = selected_file
    # st.rerun()
# Connect to the SQLite database
connection = sqlite3.connect("neuronudge.db",timeout=1000000)
cursor = connection.cursor()

# Create tables for emotion history
cursor.execute("""
CREATE TABLE IF NOT EXISTS emotion_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    emotion TEXTs
)
""")



# Create table for tasks
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    task_name TEXT
)
""")

# Create a new table for subtasks with a foreign key reference to tasks
cursor.execute("""
CREATE TABLE IF NOT EXISTS subtasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    subtask_order INTEGER, 
    subtask_name TEXT, 
    completed INTEGER DEFAULT 0,
    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
)
""")
connection.commit()

import os
# os.environ["OPENAI_API_KEY"]  = "YOUR_OPENAI_API_KEY"




# Define sound categories and their patterns

# Set page configuration
st.set_page_config(
    page_title="NeuroNudge: AI Focus Companion for ADHD",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if not os.environ.get("OPENAI_API_KEY"):
    with st.form("api_key_form",border=True):
        api_key = st.text_input("Enter your OpenAI API Key:", key="api_key_input")
        
        submit = st.form_submit_button("Submit")
        st.link_button("Get your API Key", "https://platform.openai.com/account/api-keys")
        if submit:
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
            else:
                st.warning("Please enter your OpenAI API Key to use the app.")
                st.stop()
        else:
            st.warning("Please enter your OpenAI API Key to use the app.")
            
            st.stop()
from llm import generate_task_plan,generate_nudge,get_emotion_llm,get_music
# Custom CSS with space theme
st.markdown("""
<style>
    :root {
        --cosmic-blue: #0a0e2a;
        --stardust: #1a1f4b;
        --plum-purple: #8a2be2;
        --focus-red: #ff4d4d;
        --star-yellow: #ffd700;
        --break-pink: #ff2a6d;
        --ai-blue: #05d9e8;
        --progress-green: #00cc66;
        --cosmic-text: #ffffff;
    }
    header {
            display: none !important;
    }
    div[data-testid="stMainBlockContainer"]{
            padding-top: 1rem;
            padding-bottom: 0 !important;
    }
    .stApp {
        background-color: var(--cosmic-blue);
        color: var(--cosmic-text);
        font-family: 'Montserrat', sans-serif;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(255, 215, 0, 0.1) 0%, transparent 20%),
            radial-gradient(circle at 90% 60%, rgba(138, 43, 226, 0.1) 0%, transparent 20%),
            radial-gradient(circle at 40% 80%, rgba(255, 42, 109, 0.1) 0%, transparent 20%);
    }

    .main-header {
        font-family: 'Press Start 2P', cursive;
        font-size: 2.5rem;
        color: var(--star-yellow);
        text-shadow: 0 0 10px var(--star-yellow);
        margin-bottom: 1rem;
    }

    .main-header span {
        color: var(--ai-blue);
    }

    .feature-card {
        background: rgba(26, 31, 75, 0.6);
        border-radius: 20px;
        padding: 30px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        height: 100%;
        transition: all 0.3s ease;
    }

    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
        border-color: rgba(5, 217, 232, 0.3);
    }

    .demo-panel {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
    }

    .nudge-container {
        padding: 15px;
        background: rgba(5, 217, 232, 0.1);
        border-radius: 15px;
        border-left: 4px solid var(--ai-blue);
        margin-top: 20px;
    }

    .task-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .task-checkbox {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 2px solid var(--ai-blue);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }
    div
    .task-checkbox.checked {
        background-color: var(--progress-green);
        border-color: var(--progress-green);
    }

    .task-text.completed {
        text-decoration: line-through;
        opacity: 0.7;
    }

    .timer-display {
        font-size: 3rem;
        text-align: center;
        margin: 20px 0;
        font-weight: 800;
        color: var(--star-yellow);
    }

    .stButton > button {
        background: linear-gradient(45deg, var(--plum-purple), var(--ai-blue));
        color: white;
        border-radius: 30px;
        font-weight: 600;
        padding: 16px 40px;
        border: none;
        box-shadow: 0 5px 15px rgba(138, 43, 226, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(138, 43, 226, 0.6);
    }

    .nav-button {
        background: rgba(26, 31, 75, 0.6) !important;
        margin-bottom: 10px;
    }

    .nav-button:hover {
        background: rgba(26, 31, 75, 0.8) !important;
    }

    .sound-button {
        background: rgba(138, 43, 226, 0.3) !important;
        margin-bottom: 5px;
    }

    .sound-button:hover {
        background: rgba(138, 43, 226, 0.5) !important;
    }

    .progress-bar {
        height: 24px;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        margin: 12px 0;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--ai-blue), var(--progress-green)) !important;
        border-radius: 12px;
        text-align: center;
        color: var(--cosmic-text);
        line-height: 24px;
        transition: width 0.5s;
        font-weight: 500;
    }

    .companion {
        text-align: center;
        font-size: 50px;
        color: var(--progress-green);
        animation: gentle-pulse 2s infinite;
    }

    @keyframes gentle-pulse {
        0% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.03); opacity: 1; }
        100% { transform: scale(1); opacity: 0.8; }
    }

    @keyframes fadeUp {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .fade-up {
        opacity: 0;
        transform: translateY(30px);
        animation: fadeUp 1s ease forwards;
    }
    .element-container div[data-testid="stMarkdownContainer"] p{
                color: var(--cosmic-text);}
            
    button[kind="secondaryFormSubmit"]{
      background-color: rgba(151, 166, 195, 0.15) !important;
    }
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&family=Press+Start+2P&display=swap');
</style>
""", unsafe_allow_html=True)

# Initialize all session state variables
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'tasks' not in st.session_state:
    st.session_state.tasks = [
        {"id": 1, "text": "Research project requirements", "completed": False},
        {"id": 2, "text": "Create project outline", "completed": True},
        {"id": 3, "text": "Draft initial content", "completed": False},
        {"id": 4, "text": "Review and refine", "completed": False}
    ]
    tasks =  fetch_latest_task_with_subtasks(connection, cursor)
    if tasks and ("subtasks" in tasks):
        st.session_state.tasks = tasks["subtasks"]

emotions = {
"sadness" :"😢",
"joy" :"😃",
"love" :"🥰",
"anger" :"😡",
"fear" :"😱",
"surprise" :"😯"}
if 'mood' not in st.session_state:
    st.session_state.mood =fetch_latest_emotion(connection, cursor) or "joy"
if 'timer_active' not in st.session_state:
    st.session_state.timer_active = False
if 'timer_end' not in st.session_state:
    st.session_state.timer_end = None
if 'current_nudge' not in st.session_state:
    st.session_state.current_nudge = ""

if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'companion_level' not in st.session_state:
    st.session_state.companion_level = 1
if 'sound' not in st.session_state:
    st.session_state.sound = "None"
if 'timer_duration' not in st.session_state:
    st.session_state.timer_duration = 25 * 60  # 25 minutes in seconds
if 'current_audio' not in st.session_state:
    st.session_state.current_audio = "None"
if st.session_state.sound != "None" and st.session_state.current_audio is None:
    update_current_audio()
# Mood analysis function
def analyze_mood(text):
    return get_emotion_llm(text)
    # positive_words = ["good", "great", "happy", "excited", "ready", "focus", "productive", "energetic"]
    # negative_words = ["tired", "sad", "anxious", "stressed", "overwhelmed", "exhausted", "drained"]
    
    # if any(word in text.lower() for word in positive_words):
    #     return "positive"
    # elif any(word in text.lower() for word in negative_words):
    #     return "negative"
    # return "neutral"

# Get nudge message based on mood
def get_nudge_message(mood):
    positive_nudges = [
        "You're doing great! Keep up the momentum! 🌟",
        "Your progress is amazing! Let's keep going! 💪",
        "Wow, you're on fire! Ready for the next step? 🔥",
        "Your focus is impressive! Keep shining! ✨"
    ]
    
    neutral_nudges = [
        "Let's take this one step at a time. You've got this! 👍",
        "Breaking things down makes them more manageable. Ready to continue? 📋",
        "Focus on just this one thing right now. You can do it! ✨",
        "Every task completed brings you closer to your goals. Keep going! 🌟"
    ]
    
    negative_nudges = [
        "It's okay to feel overwhelmed. Let's just focus on one small thing. 🌱",
        "Be kind to yourself. How about we try a shorter focus session? 🕊",
        "Remember to breathe. You're doing better than you think. 💚",
        "Progress, not perfection. Small steps are still steps forward. 🌈"
    ]
    
    if mood == "positive":
        return random.choice(positive_nudges)
    elif mood == "negative":
        return random.choice(negative_nudges)
    else:
        return random.choice(neutral_nudges)

# Function to generate subtasks with LLM
def generate_subtasks_with_llm(task_description):
    """
    Generate subtasks using an LLM (ChatGPT API)
    This is a placeholder implementation - you'll need to add your actual API integration
    """
    return generate_task_plan(task_description)
    task_lower = task_description.lower()
    
    if any(word in task_lower for word in ["write", "paper", "essay", "article"]):
        return [
            "Research the topic and gather sources",
            "Create an outline with main points",
            "Write the first draft",
            "Revise and edit for clarity",
            "Format and add citations",
            "Proofread for errors"
        ]
    elif any(word in task_lower for word in ["clean", "organize", "tidy"]):
        return [
            "Gather all necessary cleaning supplies",
            "Declutter surfaces and put items in their places",
            "Dust all surfaces and furniture",
            "Vacuum or sweep floors",
            "Clean windows and mirrors",
            "Take out trash and recycling"
        ]
    elif any(word in task_lower for word in ["study", "learn", "review"]):
        return [
            "Review previous notes and materials",
            "Read and highlight key concepts",
            "Create summary notes or flashcards",
            "Practice with sample questions",
            "Teach the concepts to someone else",
            "Review areas of difficulty"
        ]
    else:
        # Generic breakdown for any task
        return [
            "Research and gather information",
            "Plan your approach",
            "Execute the main components",
            "Review and refine your work",
            "Prepare for next steps",
            "Celebrate completion!"
        ]

# Navigation buttons
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🏠 Home", key="home_btn", use_container_width=True):
        st.session_state.page = "Home"
with col2:
    if st.button("✨ Features", key="features_btn", use_container_width=True):
        st.session_state.page = "Features"
with col3:
    if st.button("🎮 Demo", key="demo_btn", use_container_width=True):
        st.session_state.page = "Demo"
with col4:
    if st.button("💡 Benefits", key="benefits_btn", use_container_width=True):
        st.session_state.page = "Benefits"
with col5:
    if st.button("🚀 Get Started", key="getstarted_btn", use_container_width=True):
        st.session_state.page = "Get Started"

# Home Page
if st.session_state.page == "Home":
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="fade-up">', unsafe_allow_html=True)
        st.markdown('<div class="main-header">Neuro<span>Nudge</span></div>', unsafe_allow_html=True)
        st.markdown("# Focus Made Friendly for ADHD Brains")
        st.markdown("NeuroNudge is your AI-powered focus companion that adapts to your brain's unique rhythm with gentle guidance, not pressure.")
        
        if st.button("Start Your Journey", key="start_journey_btn"):
            st.session_state.page = "Get Started"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div style="text-align: center; font-size: 120px; color: var(--ai-blue);">🤖</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: center; font-size: 100px; color: var(--progress-green);">🌱</div>', unsafe_allow_html=True)

# Features Page
elif st.session_state.page == "Features":
    st.markdown('<div class="main-header">Neuro<span>Nudge</span></div>', unsafe_allow_html=True)
    st.header("Intelligent Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 2.5rem; margin-bottom: 20px; color: var(--ai-blue);">🧠</div>', unsafe_allow_html=True)
        st.subheader("Personalized Focus & Mood Adaptation")
        st.markdown("Lightweight ML learns your optimal work/break intervals and uses sentiment analysis to adjust reminder tone for an empathetic experience.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 2.5rem; margin-bottom: 20px; color: var(--ai-blue);">📋</div>', unsafe_allow_html=True)
        st.subheader("Intelligent Task Decomposition")
        st.markdown("Our integrated LLM breaks down complex tasks into actionable, digestible sub-tasks, transforming overwhelming goals into manageable steps.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 2.5rem; margin-bottom: 20px; color: var(--ai-blue);">🎮</div>', unsafe_allow_html=True)
        st.subheader("Gentle & Gamified Engagement")
        st.markdown("Calm audio alerts, large font reminders, and emoji-based encouragement. Your visual 'Progress Companion' grows with completed sessions.")
        st.markdown('</div>', unsafe_allow_html=True)

# Demo Page
elif st.session_state.page == "Demo":
    if st.session_state.current_nudge == "":
        with st.spinner("AI is generating a nudge for you..."):
            st.session_state.current_nudge = generate_nudge(st.session_state.mood)
            pass
          
    st.markdown('<div class="main-header">Neuro<span>Nudge</span></div>', unsafe_allow_html=True)
    st.header("How NeuroNudge Works")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="demo-panel">', unsafe_allow_html=True)
        st.subheader("Task Breakdown")
        
        # Task input for user
        new_task = st.text_input("Enter a task you'd like to break down:", 
                                placeholder="e.g., Write a research paper on climate change")
        
        # Button to generate subtasks using LLM
        if st.button("Generate Subtasks with AI", key="generate_subtasks_btn"):
            if new_task:
                with st.spinner("AI is breaking down your task..."):
                    # Call function to generate subtasks using LLM
                    generated_subtasks = generate_subtasks_with_llm(new_task)
                    if generated_subtasks:
                        _,st.session_state.tasks = insert_task_with_subtasks(connection, cursor, new_task, generated_subtasks)
                        st.success("AI has generated subtasks for you!")
                    else:
                        st.error("Failed to generate subtasks. Please try again.")
            else:
                st.warning("Please enter a task first.")
        
        # Display subtasks
        if st.session_state.tasks:
            st.markdown("### Your Subtasks:")
            for i, task in enumerate(st.session_state.tasks):
                col_a, col_b = st.columns([1, 10])
                with col_a: 
                    if st.checkbox(" ", value=task["completed"], key=f"task_{task['id']}"):
                        st.session_state.tasks[i]["completed"] = True
                        update_subtask_status(connection, cursor, task["id"], True)
                    else:
                        st.session_state.tasks[i]["completed"] = False
                with col_b:
                    if task["completed"]:
                        st.markdown(f'<div class="task-text completed">{task["text"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="task-text">{task["text"]}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="nudge-container">', unsafe_allow_html=True)
        st.markdown('<p class="nudge-text">"You\'ve made great progress on your outline! Would breaking the content drafting into two 25-minute sessions help?"</p>', unsafe_allow_html=True)
        st.markdown('<div class="nudge-author"><span>🤖</span><span>Your NeuroNudge Assistant</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="demo-panel">', unsafe_allow_html=True)
        st.subheader("Focus Timer")
        
        # Timer duration selection
        timer_minutes = st.slider("Select focus duration (minutes):", 5, 60, 25, key="timer_duration_slider")
        st.session_state.timer_duration = timer_minutes * 60
        
        # Timer state management
        if 'paused_time' not in st.session_state:
            st.session_state.paused_time = None

        # Timer logic
        if st.session_state.timer_active:
            current_time = datetime.now()
            
            # Calculate time remaining
            time_remaining = max(0, (st.session_state.timer_end - current_time).total_seconds())
            minutes, seconds = divmod(int(time_remaining), 60)
            
            # Display timer
            st.markdown(f'<div class="timer-display">{minutes:02d}:{seconds:02d}</div>', unsafe_allow_html=True)
            
            # Timer control buttons
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button("⏸️ Pause", key="pause_btn", use_container_width=True):
                    st.session_state.timer_active = False
                    st.session_state.paused_time = time_remaining
                    st.session_state.current_audio = None
                    st.rerun()
            with col_b:
                if st.button("⏹️ Stop", key="stop_btn", use_container_width=True):
                    st.session_state.timer_active = False
                    st.session_state.paused_time = None
                    st.rerun()
            
            # Check if timer has ended
            if time_remaining <= 0:
                st.session_state.timer_active = False
                st.session_state.current_nudge = "Time's up! Take a break before your next session."
                if st.session_state.sound != "None":
                    st.balloons()
                st.rerun()
            
            # Update every second
            time.sleep(1)
            st.rerun()

        else:
            # Show paused time or selected duration
            if st.session_state.paused_time is not None:
                minutes, seconds = divmod(int(st.session_state.paused_time), 60)
            else:
                minutes, seconds = divmod(st.session_state.timer_duration, 60)
            
            st.markdown(f'<div class="timer-display">{minutes:02d}:{seconds:02d}</div>', unsafe_allow_html=True)
            
            # Timer control buttons when inactive
            col_a, col_b = st.columns([1, 1])
            with col_a:
                start_text = "▶️ Resume" if st.session_state.paused_time is not None else "▶️ Start Focus"
                if st.button(start_text, key="start_focus_btn", use_container_width=True):
                    st.session_state.timer_active = True           
                    
                    if st.session_state.paused_time is not None:
                        st.session_state.timer_end = datetime.now() + timedelta(seconds=st.session_state.paused_time)
                        st.session_state.paused_time = None
                    else:
                        st.session_state.timer_end = datetime.now() + timedelta(seconds=st.session_state.timer_duration)
                    
                    st.rerun()
            with col_b:
                if st.button("⏯️ Take Break", key="break_btn", use_container_width=True):
                    st.session_state.timer_active = True
                    st.session_state.timer_end = datetime.now() + timedelta(minutes=5)
                    st.session_state.current_nudge = "Enjoy your break! You've earned it."
                    st.session_state.paused_time = None
                    st.rerun()


        # Add spacing
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Enhanced Nudge Section inside the timer panel
        with st.container():
            st.markdown(f"""
                <div style="margin-top: 20px; padding: 20px; background: rgba(5, 217, 232, 0.05); border-radius: 15px;">
                    <h3 style="color: var(--ai-blue); margin-bottom: 15px; text-align: center;">✨ Mindful Motivation</h3>
                    <div class="nudge-container" style="padding: 25px; background: rgba(5, 217, 232, 0.15); border-radius: 15px; margin: 15px 0;">
                        <p style="font-size: 1.2em; line-height: 1.6; margin-bottom: 15px; color: var(--cosmic-text); text-align: center;">
                            "{st.session_state.current_nudge}"
                        </p>
                        <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 15px;">
                            <span style="font-size: 1.5em;">🌱</span>
                            <span style="color: var(--ai-blue); font-weight: 600;">Your Progress Companion</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Generate New Nudge button
            if st.button("🎯 Generate New Nudge", key="nudge_btn", use_container_width=True):
                if st.spinner("Generating a new nudge..."):
                    st.session_state.current_nudge = generate_nudge(st.session_state.mood)
                    st.rerun()
                

        st.markdown('</div>', unsafe_allow_html=True)

    # End of Demo page layout

# Benefits Page
elif st.session_state.page == "Benefits":
    st.markdown('<div class="main-header">Neuro<span>Nudge</span></div>', unsafe_allow_html=True)
    st.header("Why It Works for ADHD")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 3rem; margin-bottom: 20px; color: var(--progress-green);">😌</div>', unsafe_allow_html=True)
        st.subheader("Reduces Overwhelm")
        st.markdown("Breaking tasks into manageable steps prevents paralysis and makes starting easier.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 3rem; margin-bottom: 20px; color: var(--progress-green);">⏱</div>', unsafe_allow_html=True)
        st.subheader("Adapts to Your Rhythm")
        st.markdown("Custom work/break intervals that match your natural focus cycles, not rigid schedules.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 3rem; margin-bottom: 20px; color: var(--progress-green);">🎯</div>', unsafe_allow_html=True)
        st.subheader("Gentle Accountability")
        st.markdown("Supportive nudges instead of stressful reminders that create anxiety.")
        st.markdown('</div>', unsafe_allow_html=True)

# Get Started Page
elif st.session_state.page == "Get Started":
    st.markdown('<div class="main-header">Neuro<span>Nudge</span></div>', unsafe_allow_html=True)
    st.header("Ready to Transform Your Productivity?")
    st.markdown("Join the NeuroNudge community and discover a kinder approach to focus designed for neurodiverse brains.")
    
    # Mood input
    with st.form("mood_form",clear_on_submit=False):
        mood_input = st.text_area("How are you feeling today?", placeholder="I'm feeling...", key="mood_input")
        mood_submitted = st.form_submit_button("Analyze Mood")
    
    if mood_submitted and mood_input:
        st.session_state.mood = analyze_mood(mood_input)
        mood_emoji = emotions.get(st.session_state.mood, "🙂")
        insert_emotion(connection, cursor, st.session_state.mood)
        st.write(f"Detected mood: {st.session_state.mood} {mood_emoji}")
    # Form for user signup
    with st.form("get_started_form",clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name")
            email = st.text_input("Email")
        
        with col2:
            focus_areas = st.multiselect(
                "What areas do you want to focus on?",
                ["Work", "Study", "Creative Projects", "Household Tasks", "Personal Goals"]
            )
            adhd_type = st.selectbox(
                "ADHD Type (optional)",
                ["", "Primarily Inattentive", "Primarily Hyperactive-Impulsive", "Combined Type", "Not diagnosed but relate to symptoms"]
            )
        
        submitted = st.form_submit_button("Get NeuroNudge")
        
        if submitted:
            st.success("Thanks for your interest! We'll be in touch soon.")
            st.balloons()
    
    # Progress companion
    st.markdown("---")
    st.subheader("Your Progress Companion")
    companion_emojis = ["🌱", "🌿", "🌳", "🌺", "🌷", "🌸", "🍀", "🎋", "✨", "🦋"]
    companion_index = min(st.session_state.companion_level - 1, len(companion_emojis) - 1)
    st.markdown(f'<div class="companion">{companion_emojis[companion_index]}</div>', unsafe_allow_html=True)
    st.write(f"Level {st.session_state.companion_level}")
    
    # Progress bar
    progress_percent = min(st.session_state.progress, 100)
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress_percent}%;">{progress_percent}%</div>
    </div>
    """, unsafe_allow_html=True)



sound_options = ["None"]
for sound, pattern in sound_patterns.items():
    if any(pattern in file.lower() for file in audio_files):
        sound_options.append(sound)

# Only show sound options on Demo page
if st.session_state.page == "Demo":
    # Sound options section
    st.markdown("---")
    st.subheader("🎵 Calming Sounds")

    sound_cols = st.columns(len(sound_patterns),vertical_alignment='center')

    for idx, (col, sound) in enumerate(zip(sound_cols, sound_options)):
        with col:
            if st.button(sound, key=f"sound_{sound.lower().replace(' ', '_')}", use_container_width=True):
                st.session_state.sound = sound
                update_current_audio()
                

if st.session_state.sound != "None" and st.session_state.current_audio != None:
# Randomly select a matching audio file
    # st.info(f"Playing {st.session_state.current_audio}...")

    # Play the selected file using Streamlit's audio player
    st.audio(st.session_state.current_audio, format="audio/mp3",loop=True,autoplay=True)

# Footer
st.markdown("---")
st.markdown('<div style="text-align: center; color: var(--cosmic-text);">© 2025 NeuroNudge. Designed with ❤ for ADHD brains.</div>', unsafe_allow_html=True)

# Auto-refresh for timer
if st.session_state.timer_active:
    time.sleep(1)
    st.rerun()
