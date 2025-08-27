# FastPluggy Task Runner

A powerful and extensible **task execution framework** for Python, built on top of [FastPluggy](https://fastpluggy.xyz).  
Easily register, run, monitor, and schedule background tasks with full support for retries, logging, live WebSocket updates, and notifications.

---

## ✨ Features

- 🔧 Task registration with metadata, retries, scheduling, and custom parameters
- 🧠 Dynamic form generation from metadata
- 📡 Live logs and WebSocket updates
- 📅 CRON-based scheduler with optional notification rules
- 🔁 Retry logic with auto-link to parent task
- 🔒 Non-concurrent task execution with lock tracking
- 🧩 Extensible notifier system (Console, Slack, Webhook...)
- 📊 Admin UI to manage tasks, schedules, locks, and reports
- 💾 Persistent task context and rehydration
- 📈 Task metrics from process/thread info

---

## 🛠️ How It Works

```python
from ..task_registry import task_registry

@task_registry.register(
    description="Sync data every 5 mins",
    schedule="*/5 * * * *",
    max_retries=3,
    allow_concurrent=False
)
def sync_data_task():
    print("Sync running...")
```

For detailed instructions on creating tasks and triggering them from JavaScript, see the [Task Creation and JS Triggering Guide](docs/task_creation_and_js_triggering.md).

For information about Jinja template global variables available for task triggering, see the [Jinja Template Globals documentation](docs/jinja_template_globals.md).

---

## 📋 Roadmap

### ✅ Completed / In Progress

- [x] Task registration with metadata (`description`, `tags`, `max_retries`, `schedule`, `allow_concurrent`)
- [x] Dynamic task form rendering via metadata
- [x] Notification system with:
  - Console / webhook / Slack (optional)
  - Selectable events: `task_started`, `task_failed`, `logs`, etc.
- [x] Context/report tracking in DB
- [x] Task retry linking via `parent_task_id`
- [x] CRON-based scheduler loop
- [x] Web UI for:
  - Task logs
  - Task reports
  - Scheduled tasks
  - Locks
  - Running task status
- [x] Lock manager (`TaskLockManager`) with DB tracking
- [x] Cancel button for live-running tasks

---

### 📌 Upcoming Features

#### 🔁 Task Queue Enhancements
- [ ] Priority & rate-limit execution
- [ ] Per-user concurrency limits
- [ ] Task dependencies / DAG runner

#### 🧠 Task Registry & Detection
- [x] Auto-discovery of task definitions from modules
- [x] Celery-style shared task detection
- [ ] Dynamic execution via `run_by_name("slug", kwargs)`

#### 💾 Persistence & Rehydration
- [ ] Save function reference + args for replay/retry
- [x] Task dependency tree and retry visualization

#### 🌐 Remote Workers
- [ ] Register and manage remote workers
- [ ] Assign tasks based on tags/strategies
- [ ] Remote heartbeat & health monitoring

#### 📈 Observability
- [ ] Task metrics via `psutil` (CPU, memory, threads)
- [ ] UI views for thread/process diagnostics

---

## 📦 Tech Stack

- FastAPI + FastPluggy
- SQLAlchemy + SQLite/PostgreSQL
- WTForms + Jinja2 + Bootstrap (Tabler)
- WebSockets for real-time feedback
- Plugin-ready & modular architecture

---

## 🧠 Philosophy

This runner is built to be:

- **Introspective**: auto-generate UIs from functions
- **Composable**: integrate with your FastPluggy app
- **Scalable**: support single-machine and multi-worker environments
- **Extensible**: notifiers, hooks, CRON, logs

---

## 📎 License

MIT – Use freely and contribute 💙

---

## 🚀 Contributions Welcome!

Open issues, send PRs, share ideas —  
Let’s build the most pluggable Python task runner together.

### Warning:
Does not work with SQLite due to JSONB field requirements.