import React, { useState, useEffect } from "react";
import "./App.css";

export default function App() {
  const [tasks, setTasks] = useState(() => {
    const saved = localStorage.getItem("scheduler_tasks");
    return saved ? JSON.parse(saved) : [];
  });
  const [totalMinutes, setTotalMinutes] = useState(0);
  const [form, setForm] = useState({
    title: "",
    priority: "Low",
    ideal: "",
    min: "",
  });

  useEffect(() => {
    localStorage.setItem("scheduler_tasks", JSON.stringify(tasks));
  }, [tasks]);

  const addTask = (e) => {
    e.preventDefault();
    if (parseInt(form.min) > parseInt(form.ideal)) {
      alert("Min duration cannot exceed Ideal duration!");
      return;
    }
    setTasks([...tasks, { ...form, id: Date.now() }]);
    setForm({ title: "", priority: "Low", ideal: "", min: "" });
  };

  const calculateSchedule = () => {
    // 1. Calculate the absolute minimum time needed for all tasks
    const absoluteMinNeeded = tasks.reduce(
      (sum, t) => sum + parseInt(t.min),
      0
    );

    // 2. Check if available time is less than the total minimum
    if (totalMinutes > 0 && totalMinutes < absoluteMinNeeded) {
      alert(
        `Warning: Available time (${totalMinutes}m) is less than the minimum required (${absoluteMinNeeded}m) for all tasks!`
      );
    }
    let schedule = tasks.map((t) => ({
      ...t,
      currentDuration: parseInt(t.ideal),
    }));
    let currentTotal = schedule.reduce((sum, t) => sum + t.currentDuration, 0);

    const shrinkOrder = ["Low", "Medium", "High"];

    for (const p of shrinkOrder) {
      for (let i = 0; i < schedule.length; i++) {
        if (currentTotal <= totalMinutes) break;
        if (schedule[i].priority === p) {
          const reduction =
            parseInt(schedule[i].ideal) - parseInt(schedule[i].min);
          schedule[i].currentDuration = parseInt(schedule[i].min);
          currentTotal -= reduction;
        }
      }
    }
    return schedule;
  };
  const clearAll = () => {
    if (window.confirm("Are you sure you want to clear all tasks?")) {
      setTasks([]);
      localStorage.removeItem("scheduler_tasks");
    }
  };

  const minRequired = tasks.reduce((sum, t) => sum + (parseInt(t.min) || 0), 0);
  const isScheduleValid = totalMinutes >= minRequired && tasks.length > 0;

  return (
    <div className="container">
      <h2>
        <u>Dynamic Scheduler</u>
      </h2>
      <form onSubmit={addTask} className="task-group">
        <input
          placeholder="Task Title"
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
          required
        />
        <select
          value={form.priority}
          onChange={(e) => setForm({ ...form, priority: e.target.value })}
        >
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>
        <input
          type="number"
          placeholder="Ideal Time (mins)"
          value={form.ideal}
          onChange={(e) => setForm({ ...form, ideal: e.target.value })}
          required
        />
        <input
          type="number"
          placeholder="Min Time (mins)"
          value={form.min}
          onChange={(e) => setForm({ ...form, min: e.target.value })}
          required
        />
        <button type="submit" className="btn-add">
          Add Task
        </button>
      </form>

      <div className="task-group">
        <label>
          <b>Total Available Minutes:</b>
        </label>
        <input
          type="number"
          value={totalMinutes}
          onChange={(e) => setTotalMinutes(parseInt(e.target.value) || 0)}
        />
        <button
          className="chaos-btn"
          onClick={() => setTotalMinutes((prev) => Math.max(0, prev - 30))}
        >
          Chaos Button (-30 min)
        </button>
        <button
          onClick={clearAll}
          style={{
            background: "#6c757d",
            color: "white",
            border: "none",
            padding: "10px",
            borderRadius: "8px",
            marginLeft: "0px",
          }}
        >
          Clear All
        </button>
      </div>
      {totalMinutes > 0 &&
        totalMinutes < tasks.reduce((sum, t) => sum + parseInt(t.min), 0) && (
          <div
            style={{
              color: "red",
              fontWeight: "bold",
              marginBottom: "10px",
              padding: "10px",
              background: "#ffe6e6",
              borderRadius: "8px",
            }}
          >
            ⚠️ Not enough time to meet minimum requirements!
          </div>
        )}

      {isScheduleValid && (
        <div
          style={{
            color: "#155724",
            backgroundColor: "#d4edda",
            border: "1px solid #c3e6cb",
            padding: "10px",
            borderRadius: "8px",
            marginBottom: "20px",
            textAlign: "center",
            fontWeight: "bold",
          }}
        >
          ✅ Success: Your schedule fits within the available time!
        </div>
      )}

      <hr />

      <h3>
        <u>Schedule</u>
      </h3>

      {calculateSchedule().map((task) => (
        <div key={task.id} className={`task-card priority-${task.priority}`}>
          <div>
            <strong>{task.title}</strong>
            <br />
            <small>Priority: {task.priority}</small>
          </div>
          <div className="duration-text">{task.currentDuration} mins</div>
        </div>
      ))}
    </div>
  );
}
