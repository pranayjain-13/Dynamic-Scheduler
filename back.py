import streamlit as st
import time
from supabase import create_client

# --- 1. CONFIG & CONNECTIONS ---
SUPABASE_URL = "https://dynamic-scheduler.supabase.co/"
SUPABASE_KEY = "9328299912"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Pro-Task Scheduler", layout="wide")

# --- CSS Styling ---
st.markdown("""
    <style>
    .task-card { background-color: white; padding: 1.2rem; border-radius: 12px; border-left: 8px solid #e0e0e0; margin-bottom: 0.5rem; }
    .completed-task { opacity: 0.6; border-left-color: #28a745 !important; border-style: dashed; }
    .priority-High { border-left-color: #ff4b4b; }
    .priority-Medium { border-left-color: #ffa500; }
    .priority-Low { border-left-color: #00d4ff; }
    .strike { text-decoration: line-through; color: #999; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION UI ---
if "user" not in st.session_state:
    st.session_state.user = None

def auth_page():
    st.title("🔐 Pro-Task Login")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        pw = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login", type="primary"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                st.session_state.user = res.user
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")

    with tab2:
        s_email = st.text_input("Email", key="reg_email")
        s_pw = st.text_input("Password", type="password", key="reg_pw")
        if st.button("Create Account"):
            try:
                supabase.auth.sign_up({"email": s_email, "password": s_pw})
                st.success("Check your email for confirmation!")
            except Exception as e:
                st.error(f"Sign up failed: {e}")

# --- 3. MAIN SCHEDULER LOGIC ---
if st.session_state.user is None:
    auth_page()
else:
    # --- State Setup ---
    user_id = st.session_state.user.id
    if "active_task" not in st.session_state: st.session_state.active_task = None
    if "timer_running" not in st.session_state: st.session_state.timer_running = False

    # --- Sidebar & Task Creation ---
    with st.sidebar:
        st.write(f"Logged in as: **{st.session_state.user.email}**")
        if st.button("Logout"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()
        
        st.divider()
        with st.form("add_task"):
            title = st.text_input("Task Name")
            prio = st.selectbox("Priority", ["High", "Medium", "Low"])
            ideal = st.number_input("Ideal (min)", value=30)
            t_min = st.number_input("Min (min)", value=15)
            if st.form_submit_button("Add Task"):
                task_id = str(time.time())
                # DB Insert
                supabase.table("tasks").insert({
                    "id": task_id, "user_id": user_id, "title": title,
                    "priority": prio, "ideal_min": ideal, "min_min": t_min,
                    "remaining_seconds": ideal * 60
                }).execute()
                st.rerun()

    # --- Fetch and Display ---
    st.title("⚡ My Optimized Schedule")
    # Fetch user-specific data
    data = supabase.table("tasks").select("*").eq("user_id", user_id).execute().data
    
    if not data:
        st.info("No tasks yet.")
    else:
        # Priority Logic
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        sorted_tasks = sorted(data, key=lambda x: priority_order[x['priority']])
        
        for t in sorted_tasks:
            is_active = st.session_state.active_task == t['id']
            card_class = f"task-card priority-{t['priority']}"
            if t['is_completed']: card_class += " completed-task"
            
            st.markdown(f'<div class="{card_class}"><b>{t["title"]}</b> ({t["priority"]})</div>', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                mins, secs = divmod(t['remaining_seconds'], 60)
                st.write(f"Time: {mins:02d}:{secs:02d}")
            with c2:
                if not t['is_completed']:
                    if not is_active:
                        if st.button("Start", key=f"s_{t['id']}", type="primary"):
                            st.session_state.active_task = t['id']
                            st.session_state.timer_running = True
                            st.rerun()
                    else:
                        if st.button("Pause", key=f"p_{t['id']}"):
                            st.session_state.timer_running = False
                            # Sync to DB on pause
                            supabase.table("tasks").update({"remaining_seconds": t['remaining_seconds']}).eq("id", t['id']).execute()
                            st.rerun()
            with c3:
                if st.button("Delete", key=f"d_{t['id']}"):
                    supabase.table("tasks").delete().eq("id", t['id']).execute()
                    st.rerun()

    # --- Timer Execution ---
    if st.session_state.active_task and st.session_state.timer_running:
        active_id = st.session_state.active_task
        task_ref = next(x for x in data if x['id'] == active_id)
        if task_ref['remaining_seconds'] > 0:
            time.sleep(1)
            # Update local list for visual smooth countdown
            task_ref['remaining_seconds'] -= 1
            st.rerun()
        else:
            supabase.table("tasks").update({"is_completed": True, "remaining_seconds": 0}).eq("id", active_id).execute()
            st.session_state.active_task = None
            st.session_state.timer_running = False
            st.balloons()
            st.rerun()
