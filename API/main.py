"""
FastAPI Backend for TypeX
REST API endpoints for typing test data
"""

import streamlit as st
import time
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from src.db import TypingDB
    from src.logic import TypingLogic
except Exception as e:
    st.error(f"Failed to import modules: {e}")
    st.info("Make sure src/__init__.py exists")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Typing Speed Tester",
    page_icon="⌨️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and logic
try:
    db = TypingDB()
    logic = TypingLogic()
except Exception as e:
    st.error("🔴 Database Connection Failed!")
    st.error(str(e))
    st.stop()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'test_started' not in st.session_state:
    st.session_state.test_started = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'test_text' not in st.session_state:
    st.session_state.test_text = ""
if 'difficulty' not in st.session_state:
    st.session_state.difficulty = "medium"
if 'custom_text' not in st.session_state:
    st.session_state.custom_text = ""
if 'typed_text' not in st.session_state:
    st.session_state.typed_text = ""

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stat-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .test-text {
        font-size: 1.2rem;
        line-height: 1.6;
        padding: 1rem;
        background-color: #f9f9f9;
        border-radius: 10px;
        border: 2px solid #ddd;
        font-family: 'Courier New', monospace;
        color: #1a1a1a; /* ensure high contrast on light background */
        white-space: pre-wrap; /* keep formatting if text has line breaks */
        max-height: 180px; /* keep the box compact */
        overflow-y: auto; /* scroll if text is long */
    }
    .correct-char {
        color: green;
        background-color: #d4edda;
    }
    .incorrect-char {
        color: red;
        background-color: #f8d7da;
        text-decoration: underline;
    }
    .pending-char {
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== HELPER FUNCTIONS ====================

def login_user():
    """Handle user login/registration"""
    st.sidebar.header("👤 User Login")
    
    with st.sidebar.form(key="login_form"):
        email = st.text_input("Email", key="login_email", placeholder="your@email.com")
        name = st.text_input("Name", key="login_name", placeholder="Your Name")
        submit = st.form_submit_button("Login / Register", use_container_width=True)
        
        if submit:
            if not email or not name:
                st.error("Please provide both email and name")
            else:
                with st.spinner("Processing..."):
                    try:
                        # Check if user exists
                        user = db.get_user_by_email(email)
                        
                        if user:
                            # User exists - login
                            st.session_state.user = user
                            st.success(f"Welcome back, {user['name']}!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            # Create new user
                            user = db.create_user(name, email)
                            if user:
                                st.session_state.user = user
                                st.success(f"Account created! Welcome, {name}!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("Failed to create account")
                                st.warning("Please run: python test_connection.py")
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"Error: {error_msg}")
                        
                        if "permission denied" in error_msg.lower() or "row level security" in error_msg.lower():
                            st.warning("⚠️ Solution: Disable Row Level Security in Supabase")
                            st.code("ALTER TABLE users DISABLE ROW LEVEL SECURITY;")
                        elif "does not exist" in error_msg.lower():
                            st.warning("⚠️ Solution: Run setup_supabase.sql in Supabase SQL Editor")

def logout_user():
    """Handle user logout"""
    st.session_state.user = None
    st.session_state.test_started = False
    st.rerun()

def start_test():
    """Start a new typing test"""
    st.session_state.test_started = True
    st.session_state.start_time = time.time()
    st.session_state.typed_text = ""
    
    # Get test text
    if st.session_state.custom_text.strip():
        st.session_state.test_text = st.session_state.custom_text.strip()
    else:
        st.session_state.test_text = logic.get_random_text(st.session_state.difficulty)

def reset_test():
    """Reset the typing test"""
    st.session_state.test_started = False
    st.session_state.start_time = None
    st.session_state.typed_text = ""
    st.session_state.test_text = ""

def render_colored_text(original, typed):
    """Render text with color coding"""
    html = '<div class="test-text">'
    
    for i, char in enumerate(original):
        if i < len(typed):
            if char == typed[i]:
                html += f'<span class="correct-char">{char}</span>'
            else:
                html += f'<span class="incorrect-char">{char}</span>'
        else:
            html += f'<span class="pending-char">{char}</span>'
    
    html += '</div>'
    return html

def on_type_change():
    """Ensure live updates while typing by syncing session state and triggering rerun"""
    st.session_state.typed_text = st.session_state.get("typing_area", "")

def save_test_result(wpm, accuracy):
    """Save test result to database"""
    if st.session_state.user:
        result = db.save_typing_test(
            st.session_state.user['user_id'],
            wpm,
            accuracy
        )
        return result is not None
    return False

# ==================== MAIN APP ====================

def main():
    # Header
    st.markdown('<div class="main-header">⌨️ Typing Speed Tester</div>', unsafe_allow_html=True)
    st.markdown("### Improve your typing speed and accuracy!")
    
    # Sidebar - User Management
    if not st.session_state.user:
        login_user()
        st.info("👈 Please login to access the typing test")
    else:
        st.sidebar.header(f"👤 {st.session_state.user['name']}")
        st.sidebar.write(f"📧 {st.session_state.user['email']}")
        
        if st.sidebar.button("Logout", use_container_width=True):
            logout_user()
        
        st.sidebar.markdown("---")
        
        # User Stats
        st.sidebar.subheader("📊 Your Stats")
        stats = db.get_user_average_stats(st.session_state.user['user_id'])
        best = db.get_user_best_score(st.session_state.user['user_id'])
        rank = db.get_user_rank(st.session_state.user['user_id'])
        
        if stats['total_tests'] > 0:
            st.sidebar.metric("Total Tests", stats['total_tests'])
            st.sidebar.metric("Average WPM", f"{stats['avg_wpm']:.1f}")
            st.sidebar.metric("Average Accuracy", f"{stats['avg_accuracy']:.1f}%")
            
            if best:
                st.sidebar.metric("🏆 Best WPM", f"{best['wpm']:.1f}")
            
            if rank:
                st.sidebar.metric("🌟 Global Rank", f"#{rank}")
        else:
            st.sidebar.info("Take your first test to see stats!")
    
    # Main content tabs
    tab1, tab2 = st.tabs(["🎯 Typing Test", "🏆 Leaderboard"])
    
    # ==================== TAB 1: TYPING TEST ====================
    with tab1:
        if not st.session_state.user:
            st.warning("Please login to take a typing test")
            return
        
        # Two-column layout: typing area (left), settings (right)
        col1, col2 = st.columns([2, 1])
        with col2:
            st.subheader("⚙️ Test Settings")
            difficulty = st.selectbox(
                "Difficulty Level",
                ["easy", "medium", "hard"],
                index=1,
                key="difficulty_select"
            )
            st.session_state.difficulty = difficulty
            
            st.write("**Or use custom text:**")
            custom = st.text_area(
                "Custom Text",
                height=100,
                key="custom_input",
                placeholder="Paste your own text here..."
            )
            st.session_state.custom_text = custom
            
            if not st.session_state.test_started:
                if st.button("🚀 Start New Test", use_container_width=True, type="primary"):
                    start_test()
                    st.rerun()
            else:
                if st.button("🔄 Reset Test", use_container_width=True):
                    reset_test()
                    st.rerun()
        
        with col1:
            if st.session_state.test_started:
                st.subheader("📝 Type the text below:")
                
                # Display original text with color coding
                if st.session_state.typed_text:
                    st.markdown(
                        render_colored_text(
                            st.session_state.test_text,
                            st.session_state.typed_text
                        ),
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(f'<div class="test-text">{st.session_state.test_text}</div>', unsafe_allow_html=True)
                
                # Typing area
                typed = st.text_area(
                    "Type here:",
                    height=150,
                    key="typing_area",
                    on_change=on_type_change,
                    label_visibility="collapsed"
                )
                st.session_state.typed_text = typed
                
                # Real-time stats
                if st.session_state.start_time:
                    # Live metrics update on each input rerun
                    elapsed = time.time() - st.session_state.start_time
                    
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.markdown(f"""
                        <div class="stat-box">
                            <div class="stat-value">⏱️ {logic.format_time(elapsed)}</div>
                            <div class="stat-label">Time Elapsed</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_b:
                        progress = (len(typed) / len(st.session_state.test_text)) * 100
                        progress = min(progress, 100)
                        st.markdown(f"""
                        <div class="stat-box">
                            <div class="stat-value">📊 {progress:.0f}%</div>
                            <div class="stat-label">Progress</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_c:
                        current_wpm = logic.calculate_wpm(len(typed), elapsed) if elapsed > 0 else 0
                        st.markdown(f"""
                        <div class="stat-box">
                            <div class="stat-value">⚡ {current_wpm:.1f}</div>
                            <div class="stat-label">Current WPM</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Finish test button
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✅ Finish Test", use_container_width=True, type="primary"):
                    if not st.session_state.typed_text:
                        st.error("Please type something before finishing!")
                    else:
                        # Calculate results
                        elapsed = time.time() - st.session_state.start_time
                        wpm = logic.calculate_wpm(len(st.session_state.typed_text), elapsed)
                        accuracy, correct, total = logic.calculate_accuracy(
                            st.session_state.test_text,
                            st.session_state.typed_text
                        )
                        
                        # Save to database
                        saved = save_test_result(wpm, accuracy)
                        
                        # Display results
                        st.success("🎉 Test Complete!")
                        
                        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                        
                        with col_r1:
                            st.metric("WPM", f"{wpm:.1f}")
                        with col_r2:
                            st.metric("Accuracy", f"{accuracy:.1f}%")
                        with col_r3:
                            st.metric("Time", logic.format_time(elapsed))
                        with col_r4:
                            st.metric("Correct Chars", f"{correct}/{total}")
                        
                        # Performance rating
                        rating = logic.get_performance_rating(wpm, accuracy)
                        st.info(f"**Rating:** {rating}")
                        
                        # Tips section removed per request
                        
                        if saved:
                            st.success("Result saved to your profile!")
                        
                        # Reset for next test
                        if st.button("Take Another Test"):
                            reset_test()
                            st.rerun()
            
            else:
                st.info("Select a difficulty (easy / medium / hard) and click 'Start New Test' to get a random passage.")
    
    # ==================== TAB 2: LEADERBOARD ====================
    with tab2:
        st.subheader("Global Leaderboard")
        
        leaderboard = db.get_leaderboard(limit=10)
        
        if not leaderboard:
            st.info("No data available yet. Be the first to take a test!")
            return
        
        # Display leaderboard (top 10 scores)
        for idx, entry in enumerate(leaderboard, 1):
            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
            
            with col1:
                if idx == 1:
                    st.markdown("### 🥇")
                elif idx == 2:
                    st.markdown("### 🥈")
                elif idx == 3:
                    st.markdown("### 🥉")
                else:
                    st.markdown(f"### {idx}")
            
            with col2:
                # Highlight current user
                if st.session_state.user and entry['user_id'] == st.session_state.user['user_id']:
                    st.markdown(f"**{entry['name']} (You)**")
                else:
                    st.markdown(f"{entry['name']}")
            
            with col3:
                # Show the score's WPM
                wpm_value = entry.get('wpm') or entry.get('max_wpm', 0)
                st.metric("WPM", f"{wpm_value:.1f}")
            
            with col4:
                acc_value = entry.get('accuracy') or entry.get('best_accuracy', 0)
                st.metric("Accuracy", f"{acc_value:.1f}%")
            
            st.markdown("---")
    
    # About tab removed per request

if __name__ == "__main__":
    main()