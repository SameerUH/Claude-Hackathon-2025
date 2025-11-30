import streamlit as st
import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go

load_dotenv()

st.set_page_config(
    page_title="Personal Learning Assistant",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(120deg, #2E86AB 0%, #A23B72 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .challenge-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
    }
    .warning-box {
        background-color: #FFF3CD;
        border-left: 5px solid #FFC107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

class PersonalAssistant:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.use_mock = not self.api_key or self.api_key == 'your_api_key_here'
        
        if not self.use_mock:
            try:
                self.client = Anthropic(api_key=self.api_key)
                self.model = "claude-sonnet-4-20250514"
            except Exception as e:
                st.warning(f"API error: {e}. Using mock mode.")
                self.use_mock = True
    
    def load_profile(self, filename="student_profile.json"):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            st.error("❌ Profile not found! Run: `python generate_student_profile.py`")
            return None
    
    def get_personalized_support(self, student, area):
        """Get AI support for specific area"""
        
        if self.use_mock:
            return self._mock_support(student, area)
        
        challenge = student.get('challenge', {})
        
        prompt = f"""You are a compassionate AI assistant supporting a university student with challenges. Provide empathetic, practical guidance.

Student: {student['name']}
Challenge: {challenge.get('type', 'Various challenges')} - {challenge.get('description', '')}
Severity: {challenge.get('severity', 'Moderate')}
Current GPA: {student['gpa']}/4.0

Wellbeing:
- Stress: {student['wellbeing']['stress_level']}/10
- Anxiety: {student['wellbeing']['anxiety_level']}/10
- Motivation: {student['wellbeing']['motivation_level']}/10
- Sleep: {student['wellbeing']['sleep_hours_avg']} hours

Academic Struggles:
{chr(10).join(['- ' + s for s in student['specific_struggles']])}

Red Flags:
{chr(10).join(['- ' + k.replace('_', ' ').title() for k, v in student['red_flags'].items() if v])}

Focus Area: {area}

Provide:
1. Empathetic acknowledgment of their challenges
2. 3-5 specific, actionable strategies
3. Campus resources to use
4. Small first steps they can take TODAY
5. Encouragement and hope

Be warm, understanding, and practical. Avoid being preachy."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            st.error(f"Error: {e}")
            return self._mock_support(student, area)
    
    def _mock_support(self, student, area):
        name = student['name']
        challenge = student.get('challenge', {}).get('type', 'your challenges')
        
        return f"""## Support for {name} - {area}

### 💙 I See You

Managing {challenge} while keeping up with university is incredibly challenging, {name}. Your stress level of {student['wellbeing']['stress_level']}/10 and {student['wellbeing']['sleep_hours_avg']} hours of sleep show you're really struggling right now. That's okay - you're not alone.

### 🎯 Let's Address {area}

**Strategy 1: Break It Down**
Instead of looking at everything at once, focus on the next 24 hours. What's ONE thing you can accomplish today? Just one.

**Strategy 2: Use Your Accommodations**
You're entitled to: {', '.join(student['challenge']['accommodations_needed'][:2])}. Have you registered these? If not, that's your priority.

**Strategy 3: Connect with Support**
- Visit Counseling Services (free sessions available)
- Register with Disability Services if you haven't
- Join a support group for students with {challenge}

**Strategy 4: Protect Your Sleep**
Your {student['wellbeing']['sleep_hours_avg']} hours isn't enough. Aim for just 30 minutes more tonight. Better sleep = better focus = better grades.

**Strategy 5: Be Kind to Yourself**
You're managing a {student['challenge']['severity']} case of {challenge} AND maintaining a {student['gpa']} GPA. That's actually impressive.

### 📞 Resources to Use This Week

1. **Counseling Center**: Call for appointment
2. **Disability Services**: Register accommodations  
3. **Academic Advisor**: Discuss reduced course load
4. **Peer Support**: Find others who understand

### ✨ Your Action for TODAY

Pick ONE:
- [ ] Email your hardest professor about accommodations
- [ ] Schedule one counseling appointment
- [ ] Get 7 hours sleep tonight
- [ ] Attend one class you've been avoiding
- [ ] Complete one small assignment

### 💪 You've Got This

{name}, you're showing up despite {challenge}. That takes real strength. Progress isn't linear. Some days will be hard. That's okay. Keep taking it one step at a time. 🌟

Remember: Asking for help isn't weakness - it's wisdom."""

# Initialize
if 'assistant' not in st.session_state:
    st.session_state.assistant = PersonalAssistant()
if 'student' not in st.session_state:
    st.session_state.student = st.session_state.assistant.load_profile()

st.markdown('<div class="main-header">🎓 Your Personal Learning Assistant</div>', unsafe_allow_html=True)

if st.session_state.assistant.use_mock:
    st.info("ℹ️ Running in mock mode. Add API credits for personalized AI support.")

if not st.session_state.student:
    st.stop()

student = st.session_state.student

# Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {student['name']}")
    st.write(f"**{student['subject']}** • Year {student['year']}")
    st.write(f"📧 {student['email']}")
    
    st.divider()
    
    # Challenge badge
    if student.get('challenge'):
        ch = student['challenge']
        st.markdown(f'<div class="challenge-badge">{ch["type"]}</div>', unsafe_allow_html=True)
        st.caption(f"Severity: {ch['severity']}")
    
    st.divider()
    
    # Quick metrics
    st.metric("GPA", f"{student['gpa']}/4.0")
    st.metric("Average", f"{student['average_grade']}%")
    
    wb = student['wellbeing']
    stress_emoji = "🔴" if wb['stress_level'] > 7 else "🟡" if wb['stress_level'] > 5 else "🟢"
    st.metric("Stress", f"{wb['stress_level']}/10 {stress_emoji}")
    
    sleep_emoji = "🔴" if wb['sleep_hours_avg'] < 6 else "🟡" if wb['sleep_hours_avg'] < 7 else "🟢"
    st.metric("Sleep", f"{wb['sleep_hours_avg']}h {sleep_emoji}")

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Overview",
    "🏥 My Challenge",
    "📚 Academics",
    "🧠 Wellbeing",
    "💬 Get Help"
])

with tab1:
    st.header("Your Dashboard")
    
    # Red flags
    active_flags = [k.replace('_', ' ').title() for k, v in student['red_flags'].items() if v]
    if active_flags:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("### ⚠️ Areas Needing Attention")
        for flag in active_flags:
            st.write(f"• {flag}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 GPA", f"{student['gpa']}/4.0")
        st.metric("📅 Attendance", f"{student['behavioral_patterns']['attendance_rate']}%")
    
    with col2:
        st.metric("📝 Completion", f"{student['behavioral_patterns']['assignment_completion_rate']}%")
        st.metric("⏰ Late Work", student['behavioral_patterns']['late_submissions_this_semester'])
    
    with col3:
        st.metric("❌ Missed Classes", student['behavioral_patterns']['missed_classes_this_semester'])
        st.metric("🙋 Participation", student['behavioral_patterns']['participation_level'])
    
    st.divider()
    
    # Module grades chart
    st.subheader("📖 Your Grades")
    modules = student['modules']
    
    fig = px.bar(
        x=list(modules.values()),
        y=list(modules.keys()),
        orientation='h',
        labels={'x': 'Grade (%)', 'y': 'Module'},
        color=list(modules.values()),
        color_continuous_scale='RdYlGn',
        range_color=[0, 100]
    )
    fig.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Strengths
    st.subheader("💪 Your Strengths")
    cols = st.columns(2)
    for idx, strength in enumerate(student['personal_strengths']):
        cols[idx % 2].write(f"✓ {strength}")

with tab2:
    st.header("Understanding Your Challenge")
    
    if student.get('challenge'):
        ch = student['challenge']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {ch['type']}")
            st.write(ch['description'])
            
            st.markdown("**Severity:** " + ch['severity'])
            st.markdown(f"**Diagnosed:** {'Yes ✓' if ch['diagnosed'] else 'No'}")
            st.markdown(f"**Accommodations Registered:** {'Yes ✓' if ch['accommodations_registered'] else 'No ⚠️'}")
            st.markdown(f"**Medication:** {'Yes' if ch['medication'] else 'No'}")
        
        with col2:
            # Impact visualization
            impact_areas = ch['impact_areas']
            fig = go.Figure(data=[go.Pie(
                labels=impact_areas,
                values=[1]*len(impact_areas),
                hole=.3
            )])
            fig.update_layout(
                title="Impact Areas",
                showlegend=True,
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        st.subheader("🛠️ Your Accommodations")
        st.info("These accommodations can help you succeed:")
        for acc in ch['accommodations_needed']:
            st.write(f"✓ {acc}")
        
        if not ch['accommodations_registered']:
            st.warning("⚠️ You haven't registered these accommodations yet! Visit Disability Services to set them up.")
        
        st.divider()
        
        st.subheader("⚠️ How This Affects You")
        for struggle in student['specific_struggles']:
            st.write(f"• {struggle}")

with tab3:
    st.header("Academic Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Current Grades")
        for module, grade in sorted(student['modules'].items(), key=lambda x: x[1], reverse=True):
            if grade >= 70:
                st.success(f"✓ {module}: **{grade}%**")
            elif grade >= 60:
                st.warning(f"⚠️ {module}: **{grade}%**")
            else:
                st.error(f"❌ {module}: **{grade}%** - Needs attention")
    
    with col2:
        st.subheader("📚 Study Habits")
        sh = student['study_habits']
        st.write(f"**Hours/Week:** {sh['study_hours_per_week']}")
        st.write(f"**Consistency:** {sh['study_consistency']}")
        st.write(f"**Best Time:** {sh['preferred_study_time']}")
        st.write(f"**Environment:** {sh['study_environment']}")
        st.write(f"**Procrastination:** {sh['procrastination_level']}")
    
    st.divider()
    
    st.subheader("🎯 Your Academic Goals")
    for goal in student['goals']['academic']:
        st.write(f"• {goal}")

with tab4:
    st.header("Wellbeing & Mental Health")
    
    wb = student['wellbeing']
    
    # Wellbeing metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Stress Level", f"{wb['stress_level']}/10")
        st.progress(wb['stress_level'] / 10)
    
    with col2:
        st.metric("Anxiety Level", f"{wb['anxiety_level']}/10")
        st.progress(wb['anxiety_level'] / 10)
    
    with col3:
        st.metric("Motivation", f"{wb['motivation_level']}/10")
        st.progress(wb['motivation_level'] / 10)
    
    with col4:
        st.metric("Social Connection", f"{wb['social_connection']}/10")
        st.progress(wb['social_connection'] / 10)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("😴 Sleep & Self-Care")
        st.metric("Average Sleep", f"{wb['sleep_hours_avg']} hours")
        st.write(f"**Quality:** {wb['sleep_quality']}")
        st.write(f"**Self-Care Rating:** {wb['self_care_rating']}/10")
    
    with col2:
        st.subheader("🏥 Support Status")
        st.write(f"**In Therapy:** {'Yes ✓' if wb['currently_in_therapy'] else 'No'}")
        st.write(f"**Seeking Help:** {'Yes ✓' if wb['seeking_help'] else 'No ⚠️'}")
        st.write(f"**Depression Score:** {wb['depression_indicators']}/10")
    
    st.divider()
    
    st.subheader("📞 Support Services You're Using")
    sa = student['support_accessed']
    
    cols = st.columns(3)
    services = list(sa.items())
    for idx, (service, accessed) in enumerate(services):
        with cols[idx % 3]:
            if accessed:
                st.success(f"✓ {service.replace('_', ' ').title()}")
            else:
                st.info(f"○ {service.replace('_', ' ').title()}")

with tab5:
    st.header("Get Personalized Support")
    
    st.write(f"Hi {student['name']}! I'm here to help. What do you need support with?")
    
    focus_areas = [
        "Managing my anxiety/stress",
        "Improving my grades",
        "Dealing with missed assignments",
        "Time management and organization",
        "Motivation and energy",
        "Using my accommodations",
        "Building better study habits",
        "Balancing mental health and academics",
        "Getting back on track after falling behind"
    ]
    
    selected_area = st.selectbox("I need help with:", focus_areas)
    
    if st.button("🤖 Get Personalized Advice", type="primary", use_container_width=True):
        with st.spinner("Creating personalized support for you..."):
            advice = st.session_state.assistant.get_personalized_support(student, selected_area)
            
            st.markdown("---")
            st.markdown(advice)
            
            st.download_button(
                label="📥 Download This Advice",
                data=advice,
                file_name=f"support_{selected_area.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

# Footer
st.divider()
st.caption("💙 You're not alone. We're here to support you through your journey.")