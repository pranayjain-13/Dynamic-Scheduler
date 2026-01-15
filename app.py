import streamlit as st
import time

# --- Page Config ---
st.set_page_config(page_title="Pro-Task Scheduler", layout="wide", page_icon="📅")

# ---CSS---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .task-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .priority-High { border-left-color: #ff4b4b; }
    .priority-Medium { border-left-color: #ffa500; }
    .priority-Low { border-left-color: #00d4ff; }
    .duration-pill {
        background: #f1f3f5;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        color: #1a1c23;
    }
    </style>
    """, unsafe_allow_html=True)

# --- State Management ---
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "total_minutes" not in st.session_state:
    st.session_state.total_minutes = 120

# --- Sidebar---
with st.sidebar:
    st.header("📝 Add New Task")
    with st.form("task_form", clear_on_submit=True):
        t_title = st.text_input("Task Name", placeholder="e.g. Coding")
        t_priority = st.selectbox("Priority Level", ["High", "Medium", "Low"], index=1)
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            t_ideal = st.number_input("Ideal (min)", min_value=1, value=30)
        with col_t2:
            t_min = st.number_input("Min (min)", min_value=1, value=15)
        
        if st.form_submit_button("➕ Add to Schedule"):
            if t_min > t_ideal:
                st.error("Min > Ideal!")
            elif t_title:
                st.session_state.tasks.append({
                    "id": time.time(), "title": t_title, 
                    "priority": t_priority, "ideal": t_ideal, "min": t_min
                })
                st.rerun()

    st.divider()
    st.header("⚙️ Settings")
    st.session_state.total_minutes = st.number_input(
        "Total Available Time (mins)", value=st.session_state.total_minutes, step=15
    )
    
    if st.button("🔥 Chaos Mode (-30m)", use_container_width=True):
        st.session_state.total_minutes = max(0, st.session_state.total_minutes - 30)
        st.rerun()
        
    if st.button("🗑️ Clear All Tasks", use_container_width=True, type="secondary"):
        st.session_state.tasks = []
        st.rerun()

def calculate_schedule(tasks, total_mins):
    schedule = [{**t, "current": t["ideal"]} for t in tasks]
    current_total = sum(t["current"] for t in schedule)
    
    # Priority shrinking
    for p in ["Low", "Medium", "High"]:
        for task in schedule:
            if current_total <= total_mins: break
            if task["priority"] == p:
                reduction = task["ideal"] - task["min"]
                task["current"] = task["min"]
                current_total -= reduction
    return schedule

# --- Main Interface ---
st.title("⚡ Dynamic Scheduler")

# Top Metrics Row
min_req = sum(t["min"] for t in st.session_state.tasks)
ideal_req = sum(t["ideal"] for t in st.session_state.tasks)

m1, m2, m3 = st.columns(3)
m1.metric("Available Time", f"{st.session_state.total_minutes}m")
m2.metric("Minimum Required", f"{min_req}m", delta=st.session_state.total_minutes - min_req, delta_color="normal")
m3.metric("Tasks Count", len(st.session_state.tasks))

# Notification
if st.session_state.tasks:
    if st.session_state.total_minutes < min_req:
        st.error(f"🚨 **Critical:** You are short by {min_req - st.session_state.total_minutes} minutes!")
    elif st.session_state.total_minutes < ideal_req:
        st.warning("⚠️ **Note:** Shrinking lower priority tasks to fit your schedule.")
    else:
        st.success("✨ **Perfect:** All tasks can be completed at their ideal duration!")

# Display Schedule
st.subheader("Your Optimized Timeline")

if not st.session_state.tasks:
    st.info("No tasks yet. Use the sidebar to add your first task!")
else:
    final_schedule = calculate_schedule(st.session_state.tasks, st.session_state.total_minutes)
    
    for t in final_schedule:
        # Visual Task Cards
        st.markdown(f"""
            <div class="task-card priority-{t['priority']}">
                <div>
                    <div style="font-size: 1.1rem; font-weight: 700;">{t['title']}</div>
                    <div style="color: #666; font-size: 0.85rem;">Priority: {t['priority']} 
                        | <span style="text-decoration: line-through;">{t['ideal']}m</span> → {t['current']}m
                    </div>
                </div>
                <div class="duration-pill">
                    {t['current']} mins
                </div>
            </div>
        """, unsafe_allow_html=True)