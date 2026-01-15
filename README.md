# ⚡ Pro-Task Dynamic Scheduler

A high-performance, modern task management web application built with **Python** and **Streamlit**. This tool goes beyond a simple "To-Do" list by dynamically recalculating your schedule durations based on your available time and task priorities.

---

## ✨ Key Features
1. Priority-Weighted Scaling: Automatically reduces task durations from "Ideal" to "Minimum" starting with Low-priority items first.
2. Real-time Analytics: A header dashboard displays "Available Time," "Minimum Required," and "Task Count" with live delta calculations.
3. Chaos Mode: A one-click simulation to see how your schedule handles a sudden loss of 30 minutes.
4. Modern UI/UX: <br>
 • Sidebar Inputs: Keeps the workspace clutter-free. <br>
 • Color-Coded Cards: High (Red), Medium (Orange), and Low (Blue) visual identifiers.<br>
 • Status Alerts: Smart notifications that warn you if your goals are mathematically impossible.
5. Session Persistence: Maintains your task list during the current browser session.

## 🧠 Scheduling Logic
The application uses a Tiered Reduction Algorithm:
1. Initial State: All tasks are set to their Ideal Duration.
2. Constraint Check: If Total Time > Available Time, the system enters "Shrink Mode."
3. Tiered Compression:<br>
• Phase 1: Reduce all Low priority tasks to their Minimum.<br>
• Phase 2: If still over available time, reduce all Medium priority tasks to Minimum.<br>
• Phase 3: If still over available time, reduce all High priority tasks to Minimum.
4. Validation: If the total time is still exceeded after all phases, a critical warning is triggered.

## Application Architecture
``` mermaid
graph TD
    subgraph Client_Browser
    UI[Web Interface]
    end

    subgraph Streamlit_Backend
    SS[Session State: tasks, total_minutes]
    Logic{Reduction Algorithm}
    
    subgraph Logic_Steps
    L1[Start: All tasks at Ideal]
    L2[Shrink Low Priority]
    L3[Shrink Medium Priority]
    L4[Shrink High Priority]
    end
    end

    UI -->|Input Task| SS
    UI -->|Adjust Total Available Time| SS
    SS --> Logic
    Logic --> L1
    L1 --> L2
    L2 --> L3
    L3 --> L4
    L4 -->|Calculated Schedule| UI
    
    style SS fill:#f9f,stroke:#333,stroke-width:2px
    style Logic fill:#bbf,stroke:#333,stroke-width:2px
```
## Implementation Code
``` mermaid
graph TD
    A[User Input] -->|Add Task/Set Time| B(Streamlit Session State)
    B --> C{Total Time > Budget?}
    C -- No --> D[Render Ideal Times]
    C -- Yes --> E[Reduction Logic]
    
    E --> F[1. Shrink Low Priority]
    F --> G{Check Budget}
    G -- Still Over --> H[2. Shrink Medium Priority]
    H --> I{Check Available Time}
    I -- Still Over --> J[3. Shrink High Priority]
    
    J --> K[Final Rendered UI]
    D --> K
    G -- Requirements Met --> K
    I -- Requirements Met --> K
```

## 🏃‍♂️ Setup Instructions
1. Clone the repo: `git clone https://github.com/pranayjain-13/Dynamic-Scheduler.git`
2. Install dependencies: `pip install streamlit`
3. Launch: `streamlit run app.py`

## 🔗Screen Recording
https://drive.google.com/drive/folders/1lUTEROPvlJnWNd5R5ePRZ7abGXMUaITK

