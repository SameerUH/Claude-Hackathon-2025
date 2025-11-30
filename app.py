import streamlit as st
import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime, timedelta
import base64
import tempfile

load_dotenv()

st.set_page_config(
    page_title="LearnWell - Personalized Learning",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# MODERN ACCESSIBLE CSS
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #2563EB;
        --primary-dark: #1D4ED8;
        --secondary: #7C3AED;
        --success: #059669;
        --warning: #D97706;
        --danger: #DC2626;
        --bg-light: #F8FAFC;
        --bg-card: #FFFFFF;
        --text-primary: #1E293B;
        --text-secondary: #64748B;
        --border: #E2E8F0;
        --shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
    }
    
    /* Base Styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 50%, #F0FDFA 100%) !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Hero Section */
    .hero-container {
        background: linear-gradient(135deg, #1E40AF 0%, #7C3AED 50%, #2563EB 100%);
        border-radius: 24px;
        padding: 48px;
        margin-bottom: 32px;
        color: white;
        text-align: center;
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.3; }
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 16px;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        opacity: 0.9;
        max-width: 600px;
        margin: 0 auto;
        position: relative;
        z-index: 1;
    }
    
    /* Card Styles */
    .card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: var(--shadow);
        border: 1px solid var(--border);
        margin-bottom: 16px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
    }
    
    .card-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
    }
    
    .card-icon-blue { background: #DBEAFE; }
    .card-icon-purple { background: #EDE9FE; }
    .card-icon-green { background: #D1FAE5; }
    .card-icon-orange { background: #FEF3C7; }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: var(--shadow);
        border-left: 4px solid var(--primary);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary);
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin-top: 4px;
    }
    
    /* Progress Bar */
    .progress-container {
        background: #E2E8F0;
        border-radius: 100px;
        height: 12px;
        overflow: hidden;
        margin: 16px 0;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 100px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        transition: width 0.5s ease;
    }
    
    /* Step Indicator */
    .step-indicator {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-bottom: 32px;
    }
    
    .step-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #CBD5E1;
        transition: all 0.3s;
    }
    
    .step-dot.active {
        background: var(--primary);
        transform: scale(1.2);
    }
    
    .step-dot.completed {
        background: var(--success);
    }
    
    /* Form Styles */
    .form-section {
        background: white;
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: var(--shadow);
    }
    
    .form-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 8px;
    }
    
    .form-description {
        color: var(--text-secondary);
        margin-bottom: 24px;
    }
    
    /* Input Enhancements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 2px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        font-size: 16px !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Button Styles */
    .stButton > button {
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.2s !important;
        border: none !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
        color: white !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    /* Selectbox Fix */
    .stSelectbox > div > div {
        border: 2px solid var(--border) !important;
        border-radius: 12px !important;
        min-height: 56px !important;
    }
    
    div[data-baseweb="popover"] {
        z-index: 999999 !important;
    }
    
    ul[role="listbox"] {
        border-radius: 12px !important;
        box-shadow: var(--shadow-lg) !important;
        border: 2px solid var(--border) !important;
    }
    
    li[role="option"] {
        padding: 12px 16px !important;
        font-size: 16px !important;
    }
    
    li[role="option"]:hover {
        background: var(--primary) !important;
        color: white !important;
    }
    
    /* Slider Styles */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
    }
    
    /* Alert Boxes */
    .alert {
        padding: 16px 20px;
        border-radius: 12px;
        margin: 16px 0;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    
    .alert-info {
        background: #DBEAFE;
        border: 1px solid #93C5FD;
        color: #1E40AF;
    }
    
    .alert-success {
        background: #D1FAE5;
        border: 1px solid #6EE7B7;
        color: #065F46;
    }
    
    .alert-warning {
        background: #FEF3C7;
        border: 1px solid #FCD34D;
        color: #92400E;
    }
    
    /* Wellbeing Card */
    .wellbeing-card {
        background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #A7F3D0;
        margin: 16px 0;
    }
    
    .wellbeing-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.125rem;
        font-weight: 600;
        color: #065F46;
        margin-bottom: 12px;
    }
    
    /* Material Card */
    .material-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 12px;
        border: 2px solid var(--border);
        transition: all 0.2s;
    }
    
    .material-card:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow);
    }
    
    .material-card.completed {
        border-color: var(--success);
        background: #F0FDF4;
    }
    
    /* Audio Button */
    .audio-btn {
        background: linear-gradient(135deg, #7C3AED, #A78BFA) !important;
        color: white !important;
        border: none !important;
        padding: 12px 20px !important;
        border-radius: 100px !important;
        font-weight: 600 !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 8px !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 8px;
        border-radius: 16px;
        box-shadow: var(--shadow);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary) !important;
        color: white !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white !important;
        border-radius: 12px !important;
        border: 2px solid var(--border) !important;
        font-weight: 600 !important;
    }
    
    /* Accessibility */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* Focus Visible */
    *:focus-visible {
        outline: 3px solid var(--primary) !important;
        outline-offset: 2px !important;
    }
    
    /* High Contrast Mode */
    @media (prefers-contrast: high) {
        .card, .form-section {
            border: 3px solid black !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HELPER FUNCTIONS
# ============================================

def text_to_speech(text):
    """Text to speech with UK voice"""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='en', slow=False, tld='co.uk')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_file = fp.name
        tts.save(temp_file)
        with open(temp_file, 'rb') as f:
            audio = f.read()
        try:
            os.unlink(temp_file)
        except:
            pass
        return audio
    except:
        return None

def speak_button(text, key, label="🔊 Listen"):
    """Accessible audio button"""
    if st.button(label, key=f"speak_{key}", help="Click to hear this text read aloud"):
        with st.spinner("Creating audio..."):
            audio = text_to_speech(text)
            if audio:
                st.audio(audio, format='audio/mp3', autoplay=True)
            else:
                st.warning("Audio not available. Please try again.")

def render_hero(title, subtitle):
    """Render hero section"""
    st.markdown(f"""
    <div class="hero-container">
        <h1 class="hero-title">{title}</h1>
        <p class="hero-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def render_stats(stats):
    """Render stats grid"""
    cols = st.columns(len(stats))
    for i, (label, value, icon) in enumerate(stats):
        with cols[i]:
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>
                <div class="stat-value">{value}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

def render_step_indicator(current_step, total_steps):
    """Render step dots"""
    dots_html = ""
    for i in range(1, total_steps + 1):
        if i < current_step:
            dots_html += '<div class="step-dot completed"></div>'
        elif i == current_step:
            dots_html += '<div class="step-dot active"></div>'
        else:
            dots_html += '<div class="step-dot"></div>'
    
    st.markdown(f"""
    <div class="step-indicator">{dots_html}</div>
    """, unsafe_allow_html=True)

def render_alert(message, alert_type="info", icon="💡"):
    """Render alert box"""
    st.markdown(f"""
    <div class="alert alert-{alert_type}">
        <span style="font-size: 1.5rem;">{icon}</span>
        <div>{message}</div>
    </div>
    """, unsafe_allow_html=True)

def get_wellness_message(user):
    """Generate personalized wellness message"""
    anxiety = user.get('anxiety', 5)
    stress = user.get('stress', 5)
    sleep = user.get('sleep_hours', 7)
    
    messages = []
    
    if anxiety >= 7:
        messages.append("Remember to take deep breaths. You're doing great! 🌟")
    if stress >= 7:
        messages.append("Consider taking a 5-minute break every 25 minutes. 🧘")
    if sleep < 6:
        messages.append("Try to get more rest tonight. Sleep helps learning! 😴")
    
    if not messages:
        messages.append("You're in a great headspace for learning today! 💪")
    
    return messages

# ============================================
# MAIN PLATFORM CLASS
# ============================================

class LearnWell:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.use_mock = not self.api_key or self.api_key == 'your_api_key_here'
        if not self.use_mock:
            try:
                self.client = Anthropic(api_key=self.api_key)
                self.model = "claude-sonnet-4-20250514"
            except:
                self.use_mock = True
        self.users_file = "users_database.json"
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
    
    def load_users(self):
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_user(self, user_data):
        users = self.load_users()
        users[user_data['student_id']] = user_data
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def get_user(self, student_id, name):
        users = self.load_users()
        user = users.get(student_id)
        if user and user['name'].lower().strip() == name.lower().strip():
            return user
        return None
    
    def build_student_context(self, student):
        """Build comprehensive student context for AI"""
        context = f"""
## STUDENT PROFILE

**Basic Info:**
- Name: {student['name']}
- Age: {student['age']}
- Subject: {student['subject']} (Year {student['year']})
- Learning Style: {student.get('learning_style', 'Mixed')}
- Best Study Time: {student.get('study_time', 'Flexible')}
- Weekly Study Hours: {student.get('study_hours', 15)}

**Current Wellbeing:**
- Anxiety: {student.get('anxiety', 5)}/10
- Stress: {student.get('stress', 5)}/10
- Motivation: {student.get('motivation', 5)}/10
- Sleep: {student.get('sleep_hours', 7)} hours ({student.get('sleep_quality', 'Fair')})
"""
        
        if student.get('challenge', {}).get('has_challenge'):
            ch = student['challenge']
            context += f"""
**Learning Challenges:**
- Types: {', '.join(ch.get('types', ['Not specified']))}
- Impact: {ch.get('severity', 'Moderate')}
- What Helps: {ch.get('what_helps', 'Not specified')}
"""
        
        context += f"""
**Goals & Barriers:**
- Main Goal: {student.get('goal', 'Academic success')}
- Barriers: {', '.join(student.get('barriers', ['None specified']))}
- Accessibility Needs: {', '.join(student.get('accessibility', ['None']))}
"""
        return context
    
    def teach_pdf(self, student, file_name, pdf_content):
        """Generate personalized lesson from PDF"""
        if self.use_mock:
            return self._mock_lesson(student, file_name)
        
        try:
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            student_context = self.build_student_context(student)
            
            # Adjust complexity based on student state
            anxiety = student.get('anxiety', 5)
            complexity = "simple and reassuring" if anxiety >= 7 else "clear and engaging"
            
            prompt = f"""You are a skilled, empathetic tutor. Read this PDF and create a personalized lesson for this student.

{student_context}

## TEACHING APPROACH

Based on this student's profile:
- Use {complexity} language (Grade 8 reading level)
- Keep paragraphs short (2-3 sentences max)
- Include frequent encouragement
- Match their learning style: {student.get('learning_style', 'Mixed')}
- Consider their {student.get('study_hours', 15)} hours/week availability

## LESSON STRUCTURE

Create a complete lesson with:

# 📚 [Topic Title]

## 🎯 What You'll Learn
A brief, encouraging overview (2-3 sentences)

## 💡 Why This Matters
Connect to their goal: "{student.get('goal', 'success')}"
Make it relevant to {student['subject']}

## 📖 Key Concepts

### Concept 1: [Name]
**The Simple Version:**
Plain explanation in everyday language

**Picture This:**
A vivid analogy or mental image

**Try It:**
A quick practice question with answer

### Concept 2: [Name]
[Same structure...]

[Continue for ALL major concepts in the PDF]

## ✅ Quick Review
- Key point 1
- Key point 2  
- Key point 3

## 🚀 Your Action Plan
Based on {student.get('study_hours', 15)} hours/week:
- **Today (15 min):** [Specific task]
- **This Week:** [Study plan]
- **Remember:** [Encouraging note about their goal]

---
💙 You're making progress, {student['name']}! Take breaks when needed.
"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_base64}},
                        {"type": "text", "text": prompt}
                    ]
                }]
            )
            return response.content[0].text
            
        except Exception as e:
            st.error(f"Error generating lesson: {e}")
            return self._mock_lesson(student, file_name)
    
    def generate_study_plan(self, student, materials):
        """Generate a weekly study plan"""
        if self.use_mock or not materials:
            return self._mock_study_plan(student)
        
        try:
            context = self.build_student_context(student)
            material_list = "\n".join([f"- {m['name']}" for m in materials if not m.get('done')])
            
            prompt = f"""Create a personalized weekly study plan for this student. 

{context}

**Materials to Study:**
{material_list if material_list else "No pending materials"}

Create a realistic, supportive plan considering:
- Their {student.get('study_hours', 15)} available hours/week
- Best study time: {student.get('study_time', 'Flexible')}
- Anxiety level: {student.get('anxiety', 5)}/10
- Include breaks and self-care reminders

Format as a simple, clear weekly schedule."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
    
    
            
        except Exception as e:
            return self._mock_study_plan(student)
        
    # ADD THIS NEW METHOD HERE:
    def _mock_project_ideas(self, student, material):
        subject = student['subject']
        
        # Add some variety based on subject
        project_ideas = {
            "Computer Science": [
                ("Algorithm Visualizer", "Build an interactive web tool that visualizes sorting algorithms", "JavaScript, Data Structures, UI Design"),
                ("API Integration Project", "Create an app that pulls data from public APIs and displays it creatively", "REST APIs, Data Processing, Frontend Development"),
                ("Chrome Extension", "Build a productivity extension for Chrome browser", "JavaScript, Browser APIs, Problem Solving")
            ],
            "Mathematics": [
                ("Math Problem Generator", "Create a tool that generates practice problems with solutions", "Python, Problem Design, Teaching"),
                ("Data Visualization Dashboard", "Build interactive charts showing mathematical concepts", "Statistics, Data Viz, Communication"),
                ("Calculator App", "Design a specialized calculator for specific math domains", "Programming, Math Logic, UX Design")
            ],
            "Engineering": [
                ("CAD Model Portfolio", "Create 3D models of mechanical designs", "CAD Software, Design Thinking, Documentation"),
                ("Arduino Project", "Build a working prototype using Arduino/Raspberry Pi", "Electronics, Programming, Problem Solving"),
                ("Engineering Blog", "Write technical articles explaining engineering concepts", "Technical Writing, Research, Communication")
            ]
        }
        
        # Get subject-specific projects or default
        projects = project_ideas.get(subject, [
            ("Portfolio Website", "Showcase your academic work and projects", "Web Dev, Design, Personal Branding"),
            ("Study Tracker", "Track and analyze your learning patterns", "Data Analysis, Self-Monitoring, Automation"),
            ("Tutorial Series", "Create tutorials teaching concepts from your material", "Communication, Teaching, Content Creation")
        ])
        
        import random
        selected = random.sample(projects, min(3, len(projects)))
        
        output = f"""# 🚀 Project Ideas Based on "{material['name']}"

    **Note:** These are sample ideas. Connect your API key to get personalized projects based on your PDF content!

    ---
    """
        
        for i, (title, desc, skills) in enumerate(selected, 1):
            output += f"""
    ## Project {i}: {title}

    **What You'll Build:**
    {desc}

    **Skills You'll Gain:**
    {skills}

    **Time Estimate:** 2-4 weeks ({student.get('study_hours', 15)}-20 hours total)

    **Difficulty:** Intermediate

    **Why This Matters:**
    Demonstrates hands-on application of {subject} concepts and builds your portfolio.

    **Getting Started:**
    1. Research existing examples in this space
    2. Sketch out your approach and required features
    3. Start with a minimum viable version

    ---
    """
        
        output += f"""
    ## 💡 Want PDF-Specific Projects?

    These are generic examples. To get project ideas tailored to "{material['name']}" content:
    1. Add your Anthropic API key to `.env` file
    2. Add API credits at https://console.anthropic.com
    3. Click "Generate New Ideas" again

    Your projects will be customized based on what's actually in your PDF!

    ---
    💪 Current goal: {student.get('goal', 'Success!')}
    """
        
        return output
        
    def generate_project_ideas(self, student, material):
        """Generate real-world project ideas based on material"""
        if self.use_mock:
            return self._mock_project_ideas(student, material)
        
        try:
            context = self.build_student_context(student)
            
            # If we have the PDF content, use it. Otherwise use lesson summary
            prompt_content = []
            
            # Check if we stored the PDF content
            if 'pdf_content' in material:
                pdf_base64 = material['pdf_content']
                prompt_content.append({
                    "type": "document", 
                    "source": {
                        "type": "base64", 
                        "media_type": "application/pdf", 
                        "data": pdf_base64
                    }
                })
            
            prompt_text = f"""Generate 3-5 creative, real-world project ideas based on this learning material that the student can build outside of university.

    {context}

    **Learning Material:** {material['name']}

    Generate project ideas that:
    1. Apply concepts from the PDF material to real-world problems
    2. Match the student's skill level and available time ({student.get('study_hours', 15)} hours/week)
    3. Build transferable skills relevant to {student['subject']}
    4. Can be completed in 2-6 weeks
    5. Could be portfolio pieces or used for job applications
    6. Consider their goal: "{student.get('goal', 'career development')}"
    7. Are DIFFERENT each time - provide fresh, creative ideas

    For each project idea, provide:
    - **Project Title**: Clear, engaging name
    - **What You'll Build**: 2-3 sentence description
    - **Skills You'll Gain**: List of transferable skills
    - **Time Estimate**: Realistic timeframe
    - **Difficulty**: Beginner/Intermediate/Advanced
    - **Why This Matters**: How it relates to career/portfolio
    - **Getting Started**: First 3 concrete steps

    Make the projects exciting, achievable, and career-relevant! Think creatively and provide diverse project types."""

            prompt_content.append({"type": "text", "text": prompt_text})
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2500,
                messages=[{"role": "user", "content": prompt_content}]
            )
            return response.content[0].text
            
        except Exception as e:
            return self._mock_project_ideas(student, material)
        
    def _mock_lesson(self, student, file_name):
        return f"""# 📚 Learning: {file_name}

## 🎯 What You'll Learn

This lesson covers key concepts from your {student['subject']} material.
We'll go step by step, making everything clear and manageable.

## 💡 Why This Matters

This connects directly to your goal: "{student.get('goal', 'academic success')}"
Understanding this will help you build a strong foundation.

## 📖 Key Concepts

### Concept 1: The Foundation

**The Simple Version:**
Every topic has a starting point. This is yours.
Think of it as learning the alphabet before reading books.

**Picture This:**
Imagine building a house. You need the foundation first.
Without it, nothing else can stand properly.

**Try It:**
Question: What's the first step in learning any new topic?
Answer: Understanding the basic building blocks!

### Concept 2: Putting It Together

**The Simple Version:**
Now we combine what we learned.
This is where things start to click.

**Picture This:**
Like cooking a recipe - you gather ingredients, then combine them.
Each step builds on the last.

**Try It:**
Question: How do basics help with advanced topics?
Answer: They give you the tools to understand bigger ideas!

### Concept 3: Real-World Application

**The Simple Version:**
Knowledge is most powerful when we use it.
Let's see how this applies to real situations.

**Picture This:**
You learned to ride a bike, now you can go anywhere.
Skills become freedom.

**Try It:**
Question: Why practice applying what you learn?
Answer: It makes the knowledge stick and become useful!

## ✅ Quick Review

- Start with the basics - they're your foundation
- Build up step by step - don't rush
- Apply what you learn - that's when it clicks

## 🚀 Your Action Plan

Based on your schedule:
- **Today (15 min):** Review the key concepts above
- **This Week:** Try explaining one concept to someone else
- **Remember:** "{student.get('goal', 'You can do this!')}"

---
💙 Great work, {student['name']}! Every step forward counts.
"""
    
    def _mock_study_plan(self, student):
        return f"""# 📅 Your Weekly Study Plan

## Overview
Based on your {student.get('study_hours', 15)} hours/week availability

### Best Times for You
{student.get('study_time', 'Flexible scheduling')}

---

## Monday - Wednesday
**Focus:** Review and understand
- 30 min: Read through materials
- 15 min: Take notes on key points
- 5 min: Quick break (stretch, water)
- 10 min: Review notes

## Thursday - Friday  
**Focus:** Practice and apply
- 20 min: Try practice questions
- 20 min: Work through examples
- 10 min: Note any confusion areas

## Weekend
**Focus:** Consolidate and rest
- Saturday: 30 min light review
- Sunday: Rest! Your brain needs it 🧠

---

## Daily Reminders
- 💧 Stay hydrated
- 🧘 Take breaks every 25 minutes
- 😴 Aim for {student.get('sleep_hours', 7)}+ hours of sleep
- 🎯 Keep your goal in mind: {student.get('goal', 'Success!')}

---
💙 You've got this, {student['name']}!
"""

# ============================================
# INITIALIZE SESSION STATE
# ============================================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'platform' not in st.session_state:
    st.session_state.platform = LearnWell()
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'data' not in st.session_state:
    st.session_state.data = {}
if 'page' not in st.session_state:
    st.session_state.page = None

platform = st.session_state.platform

# ============================================
# MAIN APP LOGIC
# ============================================

if not st.session_state.logged_in:
    # ========== LANDING PAGE ==========
    if st.session_state.page is None:
        render_hero(
            "🎓 LearnWell",
            "Personalized learning that adapts to you. We understand that everyone learns differently."
        )
        
        # Feature cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="card">
                <div class="card-header">
                    <div class="card-icon card-icon-blue">🎯</div>
                    <span class="card-title">Personalized</span>
                </div>
                <p>Lessons adapt to your learning style, pace, and goals.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="card">
                <div class="card-header">
                    <div class="card-icon card-icon-purple">🔊</div>
                    <span class="card-title">Accessible</span>
                </div>
                <p>Audio support, simple language, and accommodations built-in.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="card">
                <div class="card-header">
                    <div class="card-icon card-icon-green">💚</div>
                    <span class="card-title">Supportive</span>
                </div>
                <p>We consider your wellbeing, not just your grades.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        st.write("")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            st.markdown("### 👋 Returning Student")
            st.write("Welcome back! Login to continue learning.")
            if st.button("🔐 Login to My Account", use_container_width=True, type="primary"):
                st.session_state.page = 'login'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            st.markdown("### ✨ New Here?")
            st.write("Create your personalized learning profile.")
            if st.button("📝 Create Free Account", use_container_width=True, type="primary"):
                st.session_state.page = 'signup'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== LOGIN PAGE ==========
    elif st.session_state.page == 'login':
        st.markdown("## 🔐 Welcome Back!")
        
        render_alert(
            "Enter your Student ID and Name to login. These are what you saved when you created your account.",
            "info", "💡"
        )
        speak_button("Enter your Student ID and Name to login.", "login_help", "🔊 Hear Instructions")
        
        with st.form("login_form"):
            st.markdown("### Your Student ID")
            st.caption("Example: STU20250001")
            login_id = st.text_input("Student ID", placeholder="STU20250001", label_visibility="collapsed")
            
            st.markdown("### Your Name")
            st.caption("The name you used when signing up")
            login_name = st.text_input("Name", placeholder="John Smith", label_visibility="collapsed")
            
            st.write("")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                back = st.form_submit_button("← Back")
            with col2:
                submit = st.form_submit_button("Login →", type="primary")
            
            if back:
                st.session_state.page = None
                st.rerun()
            
            if submit:
                if login_id and login_name:
                    user = platform.get_user(login_id.strip(), login_name.strip())
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.success(f"Welcome back, {user['name']}! 🎉")
                        st.rerun()
                    else:
                        st.error("We couldn't find an account with that ID and name. Please check and try again.")
                else:
                    st.warning("Please fill in both fields.")
    
    # ========== SIGNUP FLOW ==========
    elif st.session_state.page == 'signup':
        total_steps = 4
        current_step = st.session_state.step
        
        st.markdown(f"## ✨ Create Your Account")
        render_step_indicator(current_step, total_steps)
        
        # Progress bar
        progress = current_step / total_steps
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-fill" style="width: {progress * 100}%;"></div>
        </div>
        <p style="text-align: center; color: var(--text-secondary);">Step {current_step} of {total_steps}</p>
        """, unsafe_allow_html=True)
        
        # ===== STEP 1: Basic Info =====
        if current_step == 1:
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            st.markdown("### 👤 Tell Us About You")
            st.markdown("Let's start with the basics.")
            
            name = st.text_input("What's your name?", placeholder="e.g., John Smith")
            email = st.text_input("Your email address", placeholder="e.g., john@email.com")
            
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Your age", min_value=16, max_value=100, value=20)
            with col2:
                year = st.selectbox("Year of study", [1, 2, 3, 4, 5])
            
            subject = st.selectbox("What are you studying?", [
                "Computer Science", "Engineering", "Business", "Psychology",
                "Biology", "Mathematics", "Medicine", "Law", "Education",
                "Nursing", "Physics", "Chemistry", "Art & Design", 
                "English Literature", "History", "Other"
            ])
            
            if subject == "Other":
                subject = st.text_input("Please specify your subject", placeholder="e.g., Environmental Science")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("← Cancel"):
                    st.session_state.page = None
                    st.session_state.step = 1
                    st.session_state.data = {}
                    st.rerun()
            with col2:
                if st.button("Continue →", type="primary"):
                    if name and email and '@' in email and subject:
                        st.session_state.data.update({
                            'name': name, 'email': email, 'age': age,
                            'year': year, 'subject': subject
                        })
                        st.session_state.step = 2
                        st.rerun()
                    else:
                        st.error("Please fill in all fields correctly.")
        
        # ===== STEP 2: Learning Preferences =====
        elif current_step == 2:
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            st.markdown("### 📚 How Do You Learn Best?")
            st.markdown("This helps us create content that works for you.")
            
            learning_style = st.radio(
                "Which describes you best?",
                [
                    "👁️ Visual - I learn best with pictures, diagrams, and videos",
                    "👂 Auditory - I learn best by listening and discussing",
                    "📖 Reading/Writing - I learn best by reading and taking notes",
                    "🤲 Kinesthetic - I learn best by doing and practicing"
                ]
            )
            
            study_time = st.select_slider(
                "When do you study best?",
                options=["🌅 Early Morning", "☀️ Mid Morning", "🌤️ Afternoon", "🌆 Evening", "🌙 Night"]
            )
            
            study_hours = st.slider(
                "How many hours per week can you dedicate to studying?",
                min_value=5, max_value=40, value=15,
                help="Be realistic - it's better to underestimate"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("← Back"):
                    st.session_state.step = 1
                    st.rerun()
            with col2:
                if st.button("Continue →", type="primary"):
                    st.session_state.data.update({
                        'learning_style': learning_style,
                        'study_time': study_time,
                        'study_hours': study_hours
                    })
                    st.session_state.step = 3
                    st.rerun()
        
        # ===== STEP 3: Wellbeing & Challenges =====
        elif current_step == 3:
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            st.markdown("### 💚 Your Wellbeing Matters")
            
            render_alert(
                "This information helps us support you better. Be honest - there are no wrong answers, and everything is confidential.",
                "info", "💙"
            )
            speak_button("This information helps us support you better and is completely confidential.", "wellbeing_help")
            
            st.markdown("#### How are you feeling about your studies?")
            
            col1, col2 = st.columns(2)
            with col1:
                anxiety = st.slider("Anxiety level", 1, 10, 5, help="1 = Not anxious, 10 = Very anxious")
                stress = st.slider("Stress level", 1, 10, 5, help="1 = Low stress, 10 = High stress")
            with col2:
                motivation = st.slider("Motivation level", 1, 10, 5, help="1 = Low, 10 = Very motivated")
                depression = st.slider("Mood (feeling down)", 1, 10, 3, help="1 = Rarely, 10 = Often")
            
            st.markdown("#### Sleep")
            col1, col2 = st.columns(2)
            with col1:
                sleep_hours = st.slider("Hours of sleep per night", 3, 12, 7)
            with col2:
                sleep_quality = st.select_slider("Sleep quality", ["Very Poor", "Poor", "Fair", "Good", "Excellent"])
            
            st.markdown("---")
            st.markdown("#### Learning Challenges")
            
            has_challenge = st.checkbox("I have learning differences or disabilities")
            
            challenge_data = {'has_challenge': False}
            if has_challenge:
                challenge_types = st.multiselect(
                    "What type? (Select all that apply)",
                    [
                        "ADHD", "Dyslexia", "Dyscalculia", "Dysgraphia",
                        "Autism Spectrum", "Anxiety Disorder", "Depression",
                        "Visual Impairment", "Hearing Impairment", 
                        "Chronic Pain/Illness", "Other"
                    ]
                )
                
                severity = st.select_slider(
                    "How much does this affect your studying?",
                    ["Very Little", "Somewhat", "Moderate", "Significant", "Severe"]
                )
                
                specific_challenges = st.text_area(
                    "Tell us more about your specific challenges",
                    placeholder="e.g., I have trouble focusing for more than 10 minutes, I get overwhelmed by long texts..."
                )
                
                what_helps = st.text_area(
                    "What strategies or accommodations help you?",
                    placeholder="e.g., Extra time, quiet environment, frequent breaks, audio content..."
                )
                
                challenge_data = {
                    'has_challenge': True,
                    'types': challenge_types,
                    'severity': severity,
                    'specific_challenges': specific_challenges,
                    'what_helps': what_helps
                }
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("← Back"):
                    st.session_state.step = 2
                    st.rerun()
            with col2:
                if st.button("Continue →", type="primary"):
                    st.session_state.data.update({
                        'anxiety': anxiety,
                        'stress': stress,
                        'motivation': motivation,
                        'depression': depression,
                        'sleep_hours': sleep_hours,
                        'sleep_quality': sleep_quality,
                        'challenge': challenge_data
                    })
                    st.session_state.step = 4
                    st.rerun()
        
        # ===== STEP 4: Goals & Finish =====
        elif current_step == 4:
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            st.markdown("### 🎯 Your Goals")
            st.markdown("What do you want to achieve?")
            
            goal = st.text_area(
                "What's your main academic goal?",
                placeholder="e.g., Pass all my exams, Get a First in my dissertation, Understand statistics better...",
                height=100
            )
            
            barriers = st.multiselect(
                "What are your biggest challenges?",
                [
                    "Focus & concentration", "Time management", "Test anxiety",
                    "Procrastination", "Understanding material", "Memory",
                    "Motivation", "Health issues", "Personal problems",
                    "Financial stress", "Language barriers"
                ]
            )
            
            accessibility = st.multiselect(
                "Any accessibility needs?",
                [
                    "Larger text", "High contrast", "Screen reader support",
                    "Color blind friendly", "Audio/captions", "Simplified language",
                    "Frequent breaks", "None needed"
                ]
            )
            
            additional_info = st.text_area(
                "Anything else we should know?",
                placeholder="e.g., I work part-time, I'm a parent, English isn't my first language...",
                height=80
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("← Back"):
                    st.session_state.step = 3
                    st.rerun()
            with col2:
                if st.button("🎉 Create My Account", type="primary"):
                    if not goal:
                        st.error("Please tell us your main goal.")
                    else:
                        # Save all data
                        st.session_state.data.update({
                            'goal': goal,
                            'barriers': barriers,
                            'accessibility': accessibility,
                            'additional_info': additional_info
                        })
                        
                        # Generate student ID
                        users = platform.load_users()
                        student_id = f"STU{datetime.now().year}{len(users) + 1:04d}"
                        
                        # Create user
                        user_data = {
                            **st.session_state.data,
                            'student_id': student_id,
                            'created': datetime.now().isoformat(),
                            'materials': [],
                            'completed': 0,
                            'study_streak': 0,
                            'last_study': None
                        }
                        
                        platform.save_user(user_data)
                        
                        # Success!
                        st.balloons()
                        
                        st.markdown(f"""
                        <div class="alert alert-success" style="text-align: center; padding: 32px;">
                            <div>
                                <h2 style="margin: 0 0 16px 0;">🎉 Welcome to LearnWell!</h2>
                                <p style="font-size: 1.125rem; margin-bottom: 24px;">
                                    Your account has been created, {user_data['name']}!
                                </p>
                                <div style="background: white; padding: 20px; border-radius: 12px; margin: 16px 0;">
                                    <p style="margin: 0; font-weight: 600;">Save Your Login Details:</p>
                                    <p style="font-size: 1.5rem; margin: 8px 0;"><strong>Student ID:</strong> {student_id}</p>
                                    <p style="font-size: 1.25rem; margin: 0;"><strong>Name:</strong> {user_data['name']}</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        speak_button(f"Your student ID is {student_id}. Please write this down.", "save_id")
                        
                        st.session_state.step = 1
                        st.session_state.data = {}
                        
                        if st.button("Go to Login →", type="primary"):
                            st.session_state.page = 'login'
                            st.rerun()

# ============================================
# LOGGED IN - DASHBOARD
# ============================================
else:
    user = st.session_state.user
    materials = user.get('materials', [])
    
    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"## 👋 Welcome back, {user['name']}!")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
    
    # Wellness check
    wellness_messages = get_wellness_message(user)
    for msg in wellness_messages:
        st.markdown(f"""
        <div class="wellbeing-card">
            <div class="wellbeing-title">💚 Daily Wellness</div>
            <p style="margin: 0;">{msg}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Stats
    completed = sum(1 for m in materials if m.get('done'))
    render_stats([
        ("Materials", len(materials), "📚"),
        ("Completed", completed, "✅"),
        ("In Progress", len(materials) - completed, "📖"),
        ("Study Hours", user.get('study_hours', 15), "⏰")
    ])
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "📚 My Materials", "📅 Study Plan", "👤 Profile"])
    
    # ===== UPLOAD TAB =====
    with tab1:
        st.markdown("### 📤 Upload Learning Material")
        
        render_alert(
            "Upload a PDF and I'll create a personalized lesson just for you, based on your learning style and needs.",
            "info", "📚"
        )
        
        uploaded = st.file_uploader("Choose a PDF file", type=['pdf'], help="Maximum file size: 10MB")
        
        if uploaded:
            st.success(f"✅ Ready: **{uploaded.name}**")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                if st.button("🎓 Create My Lesson", type="primary", use_container_width=True):
                    with st.spinner("Reading your PDF and creating a personalized lesson..."):
                        pdf_bytes = uploaded.read()
                        lesson = platform.teach_pdf(user, uploaded.name, pdf_bytes)
                        
                        # Save material
                        user['materials'].append({
                            'name': uploaded.name,
                            'lesson': lesson,
                            'pdf_content': base64.b64encode(pdf_bytes).decode('utf-8'),  # ← ADD THIS LINE
                            'date': datetime.now().isoformat(),
                            'done': False
                        })
    
    # ===== MATERIALS TAB =====
    with tab2:
        st.markdown("### 📚 Your Learning Materials")
        
        if not materials:
            render_alert("No materials yet! Upload your first PDF in the Upload tab.", "info", "📤")
        else:
            # Filter options
            filter_option = st.radio(
                "Show:",
                ["All", "In Progress", "Completed"],
                horizontal=True
            )
            
            filtered = materials
            if filter_option == "In Progress":
                filtered = [m for m in materials if not m.get('done')]
            elif filter_option == "Completed":
                filtered = [m for m in materials if m.get('done')]
            
            for idx, mat in enumerate(filtered):
                is_done = mat.get('done', False)
                status_icon = "✅" if is_done else "📖"
                
                with st.expander(f"{status_icon} {mat['name']}", expanded=False):
                    st.caption(f"Uploaded: {mat['date'][:10]}")
                    
                    # ADD 4 COLUMNS INSTEAD OF 3
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("🔊 Listen", key=f"audio_{idx}"):
                            audio = text_to_speech(mat['lesson'][:1000])
                            if audio:
                                st.audio(audio, format='audio/mp3')
                    with col2:
                        st.download_button(
                            "💾 Download",
                            mat['lesson'],
                            f"lesson_{idx}.md",
                            key=f"dl_{idx}"
                        )
                    with col3:
                    # ADD THIS NEW BUTTON
                        if st.button("🚀 Project Ideas", key=f"btn_projects_{idx}"):
                            with st.spinner("Generating fresh project ideas based on your material..."):
                                projects = platform.generate_project_ideas(user, mat)
                                st.session_state[f'projects_{idx}'] = projects
                                # Force a unique timestamp to ensure fresh generation
                                st.session_state[f'projects_timestamp_{idx}'] = datetime.now().isoformat()
                                st.rerun()

                # SHOW PROJECTS IF GENERATED (moved outside col4)
                if f'projects_{idx}' in st.session_state:
                    st.markdown("---")
                    st.markdown("### 🚀 Real-World Project Ideas")
                    
                    # Get the projects content
                    projects_content = st.session_state[f'projects_{idx}']
                    
                    # Show when it was generated
                    if f'projects_timestamp_{idx}' in st.session_state:
                        timestamp = st.session_state[f'projects_timestamp_{idx}']
                        st.caption(f"Generated: {timestamp[:19].replace('T', ' ')}")
                    
                    # Display the projects
                    st.markdown(projects_content)
                    
                    col_audio, col_download, col_refresh = st.columns(3)
                    with col_audio:
                        if st.button("🔊 Listen to Projects", key=f"listen_proj_{idx}"):
                            audio = text_to_speech(projects_content[:500])
                            if audio:
                                st.audio(audio, format='audio/mp3', autoplay=True)
                    with col_download:
                        # Make sure projects_content is a string before downloading
                        if isinstance(projects_content, str):
                            st.download_button(
                                "💾 Download Project Ideas",
                                projects_content,
                                f"projects_{mat['name']}.md",
                                key=f"dl_proj_{idx}"
                            )
                    with col_refresh:
                        if st.button("🔄 Generate New Ideas", key=f"refresh_proj_{idx}"):
                            with st.spinner("Generating fresh project ideas..."):
                                projects = platform.generate_project_ideas(user, mat)
                                st.session_state[f'projects_{idx}'] = projects
                                st.session_state[f'projects_timestamp_{idx}'] = datetime.now().isoformat()
                                st.rerun()
                    with col4:
                        if not is_done:
                            if st.button("✅ Mark Complete", key=f"done_{idx}"):
                                mat['done'] = True
                                user['completed'] = user.get('completed', 0) + 1
                                platform.save_user(user)
                                st.success("Marked complete!")
                                st.rerun()
                    st.markdown("### 📖 Your Lesson")
                    st.markdown(mat['lesson'])
    
    # ===== STUDY PLAN TAB =====
    with tab3:
        st.markdown("### 📅 Your Study Plan")
        
        if st.button("🔄 Generate New Plan", type="primary"):
            with st.spinner("Creating your personalized study plan..."):
                plan = platform.generate_study_plan(user, materials)
                st.session_state.study_plan = plan
        
        if 'study_plan' in st.session_state:
            st.markdown(st.session_state.study_plan)
            speak_button(st.session_state.study_plan[:500], "study_plan", "🔊 Listen to Plan")
        else:
            render_alert("Click 'Generate New Plan' to create a personalized weekly study schedule.", "info", "📅")
    
    # ===== PROFILE TAB =====
    with tab4:
        st.markdown("### 👤 Your Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="card">
                <h4>📋 Basic Info</h4>
                <p><strong>Name:</strong> {user['name']}</p>
                <p><strong>Email:</strong> {user['email']}</p>
                <p><strong>Student ID:</strong> {user['student_id']}</p>
                <p><strong>Subject:</strong> {user['subject']} (Year {user['year']})</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="card">
                <h4>📊 Progress</h4>
                <p><strong>Materials:</strong> {len(materials)}</p>
                <p><strong>Completed:</strong> {completed}</p>
                <p><strong>Weekly Hours:</strong> {user.get('study_hours', 15)}</p>
                <p><strong>Goal:</strong> {user.get('goal', 'Not set')[:50]}...</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="card">
            <h4>🎯 Learning Preferences</h4>
            <p><strong>Style:</strong> {user.get('learning_style', 'Not set')}</p>
            <p><strong>Best Time:</strong> {user.get('study_time', 'Flexible')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if user.get('challenge', {}).get('has_challenge'):
            ch = user['challenge']
            st.markdown(f"""
            <div class="card">
                <h4>💚 Support Needs</h4>
                <p><strong>Challenges:</strong> {', '.join(ch.get('types', ['Not specified']))}</p>
                <p><strong>What Helps:</strong> {ch.get('what_helps', 'Not specified')}</p>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); padding: 16px;">
    💙 LearnWell - Learning Made Accessible for Everyone
</div>
""", unsafe_allow_html=True)