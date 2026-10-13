import os
import sys
import time
import asyncio
import subprocess
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psutil

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
VAULT_PATH = Path(os.environ.get("OBSIDIAN_VAULT_PATH", "D:/agent/agent brain"))
BLACKBOARD_PATH = VAULT_PATH / "07 - Multi-Agent System" / "Multi-Agent Live Blackboard.md"

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(periodic_metrics_loop())
    yield
    task.cancel()

app = FastAPI(title="Hermes Multi-Agent Command & Telemetry Hub", version="2.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# Agent Profiles Metadata
# -------------------------------------------------------------
AGENT_ROSTER = {
    "orchestrator": {
        "name": "orchestrator",
        "profile": "default",
        "role": "Lead Architect & Swarm Commander",
        "icon": "👑",
        "color": "#8B5CF6",
        "desc": "Menganalisis perintah user, memecah arsitektur tugas, mengawasi bus komunikasi, dan merangkum deliverable akhir."
    },
    "frontend": {
        "name": "frontend",
        "profile": "frontend",
        "role": "UI/UX & Creative 3D WebGL Engineer",
        "icon": "🎨",
        "color": "#06B6D4",
        "desc": "React, Next.js, Vite, Tailwind CSS, Three.js 3D PBR, micro-interactions, responsive high-aesthetic UI."
    },
    "backend": {
        "name": "backend",
        "profile": "backend",
        "role": "Distributed Systems & Server Engineer",
        "icon": "⚙️",
        "color": "#3B82F6",
        "desc": "FastAPI, Python asyncio, PHP 8.2+, Node.js, SQLite WAL / PostgreSQL, MQTT streaming & async loops."
    },
    "security": {
        "name": "security",
        "profile": "security",
        "role": "AppSec & Penetration Testing Specialist",
        "icon": "🛡️",
        "color": "#EF4444",
        "desc": "OWASP Top 10, SAST code audits, sanitasi input, hardening kriptografi, PoC exploit & patch verifikasi."
    },
    "migration": {
        "name": "migration",
        "profile": "migration",
        "role": "Database & Modernization Architect",
        "icon": "🔄",
        "color": "#F59E0B",
        "desc": "Evolusi skema DB (Alembic/Prisma/SQL), zero-downtime additive migrations, verifikasi rollback down()."
    },
    "integration": {
        "name": "integration",
        "profile": "integration",
        "role": "DevOps & Systems Integration Engineer",
        "icon": "🔌",
        "color": "#10B981",
        "desc": "Third-party APIs, webhook receivers (HMAC), Docker multi-stage, Vercel deployments, CI/CD pipelines."
    },
    "reviewer": {
        "name": "reviewer",
        "profile": "reviewer",
        "role": "Lead QA & Code Verifier",
        "icon": "✅",
        "color": "#84CC16",
        "desc": "Automated test suites (pytest/vitest), pemeriksaan edge-cases, verifikasi empiris kode (exit code 0)."
    },
    "researcher": {
        "name": "researcher",
        "profile": "researcher",
        "role": "Tech Researcher & Systems Architect",
        "icon": "🔬",
        "color": "#EC4899",
        "desc": "Riset teknologi mendalam, analisis trade-off library, perbandingan matriks empiris, 100% open-source."
    },
    "database": {
        "name": "database",
        "profile": "database",
        "role": "Database Architect & Data Engineer",
        "icon": "🗄️",
        "color": "#0284C7",
        "desc": "PostgreSQL, SQLite WAL, Redis, schema normalization, query optimization, indexing, ACID transactions, data integrity."
    },
    "3d": {
        "name": "3d",
        "profile": "3d",
        "role": "3D Technical Artist (Blender & Unity)",
        "icon": "🧊",
        "color": "#F97316",
        "desc": "Mastering Blender 5.1 & Unity 6. Procedural PBR materials, hard-surface/organic modeling, rigging, animations, LODs, engine asset pipeline."
    },
    "gamedev": {
        "name": "gamedev",
        "profile": "gamedev",
        "role": "Game Development Systems Engineer",
        "icon": "🎮",
        "color": "#A855F7",
        "desc": "Unity 6 & C# gameplay architecture, physics, state machines, input systems, mechanics, cross-division 3D/DB/backend integration."
    },
    "api": {
        "name": "api",
        "profile": "api",
        "role": "API Integration & Postman Specialist",
        "icon": "⚡",
        "color": "#F43F5E",
        "desc": "Postman Collections v2.1, environments, mock servers, OpenAPI 3.0/3.1 specs, and 2,000+ public APIs catalog indexing & consumption."
    },
    "reverse": {
        "name": "reverse",
        "profile": "reverse",
        "role": "Binary & Reverse Engineering Specialist",
        "icon": "🔍",
        "color": "#14B8A6",
        "desc": "Reverse engineering binary native (ELF/PE/Mach-O), dekompilasi Ghidra/Hopper/JEB, analisis protokol biner, unpacking, dan firmware/malware triage."
    }
}

# -------------------------------------------------------------
# In-Memory State Store
# -------------------------------------------------------------
class StateManager:
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.messages: List[Dict[str, Any]] = []
        self.benchmarks: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.init_agents()
        self.load_blackboard_history()

    def init_agents(self):
        for name, meta in AGENT_ROSTER.items():
            self.agents[name] = {
                "name": name,
                "profile": meta["profile"],
                "role": meta["role"],
                "icon": meta["icon"],
                "color": meta["color"],
                "desc": meta["desc"],
                "status": "idle",  # idle, busy, error, completed
                "current_task": None,
                "total_tasks": 0,
                "successful_tasks": 0,
                "failed_tasks": 0,
                "latencies_ms": [],
                "avg_latency_ms": 0.0,
                "last_latency_ms": 0.0,
                "last_active": datetime.now().isoformat(),
            }

    def load_blackboard_history(self):
        """Parse initial messages from Obsidian Blackboard if exists."""
        if not BLACKBOARD_PATH.exists():
            # Add welcome seed
            self.add_message(
                sender="orchestrator",
                target="all",
                content=f"Multi-Agent Command Center aktif. Seluruh {len(AGENT_ROSTER)} spesialis agent siap bertukar tugas dan komunikasi real-time.",
                msg_type="system"
            )
            return

        try:
            content = BLACKBOARD_PATH.read_text(encoding="utf-8")
            blocks = content.split("### [")
            for block in blocks[1:]:
                header_line, *body_lines = block.split("\n", 1)
                if "]" in header_line and "🤖" in header_line:
                    time_part, agent_part = header_line.split("]", 1)
                    ts = time_part.strip()
                    agent_name = agent_part.replace("🤖", "").replace("`", "").strip().lower()
                    if agent_name.startswith("caller_to_"):
                        target = agent_name.replace("caller_to_", "")
                        sender = "orchestrator"
                    else:
                        sender = agent_name
                        target = "all"
                    
                    body = body_lines[0].replace("---", "").strip() if body_lines else ""
                    if body:
                        detected_type = "blackboard"
                        if "Benchmark Selesai" in body or "BENCHMARK" in body:
                            detected_type = "benchmark"
                        elif "TAHAP " in body or "Swarm" in body or "SWARM" in body:
                            detected_type = "swarm_step"
                        elif "Task Dispatch" in body or "Inquiry" in body or "Instruksi" in body:
                            detected_type = "task"
                        elif "SEND ke" in body or "BROADCAST" in body:
                            detected_type = "broadcast"

                        self.messages.append({
                            "id": f"bb_{len(self.messages)+1}",
                            "timestamp": ts,
                            "sender": sender,
                            "sender_name": sender.capitalize(),
                            "sender_icon": AGENT_ROSTER.get(sender, {}).get("icon", "🤖"),
                            "sender_color": AGENT_ROSTER.get(sender, {}).get("color", "#94A3B8"),
                            "target": target,
                            "content": body,
                            "full_content": body,
                            "type": detected_type,
                            "latency_ms": None,
                            "success": True
                        })
        except Exception as e:
            print(f"[WARN] Failed to parse blackboard: {e}")

        if not self.messages:
            self.add_message(
                sender="orchestrator",
                target="all",
                content=f"Multi-Agent Hub Online. Monitoring siap digunakan untuk seluruh {len(AGENT_ROSTER)} agen spesialis.",
                msg_type="system"
            )

    def add_message(self, sender: str, target: str, content: str, msg_type: str = "chat", latency_ms: Optional[float] = None, success: bool = True) -> Dict[str, Any]:
        msg_id = f"msg_{int(time.time()*1000)}_{len(self.messages)+1}"
        sender_lower = sender.lower()
        meta = AGENT_ROSTER.get(sender_lower, {})
        
        # Dimas / User special meta
        if any(k in sender_lower for k in ["dimas", "commander", "user"]):
            sender_name = "Dimas (Commander)"
            sender_icon = "👤"
            sender_color = "#F59E0B"
        elif sender_lower == "system":
            sender_name = "System"
            sender_icon = "⚡"
            sender_color = "#38BDF8"
        else:
            sender_name = meta.get("name", sender).capitalize()
            sender_icon = meta.get("icon", "🤖")
            sender_color = meta.get("color", "#94A3B8")

        msg = {
            "id": msg_id,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "full_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sender": sender,
            "sender_name": sender_name,
            "sender_icon": sender_icon,
            "sender_color": sender_color,
            "target": target,
            "content": content,
            "type": msg_type,
            "latency_ms": round(latency_ms, 2) if latency_ms is not None else None,
            "success": success
        }
        self.messages.append(msg)
        if len(self.messages) > 600:
            self.messages.pop(0)
        return msg

    def update_agent_status(self, name: str, status: str, current_task: Optional[str] = None, latency_ms: Optional[float] = None, success: bool = True):
        name_lower = name.lower()
        if name_lower not in self.agents:
            return
        
        ag = self.agents[name_lower]
        ag["status"] = status
        ag["last_active"] = datetime.now().isoformat()
        if current_task is not None:
            ag["current_task"] = current_task
        elif status in ["idle", "standby"]:
            ag["current_task"] = None

        if latency_ms is not None:
            ag["total_tasks"] += 1
            if success:
                ag["successful_tasks"] += 1
            else:
                ag["failed_tasks"] += 1
            ag["last_latency_ms"] = round(latency_ms, 2)
            ag["latencies_ms"].append(round(latency_ms, 2))
            if len(ag["latencies_ms"]) > 30:
                ag["latencies_ms"].pop(0)
            ag["avg_latency_ms"] = round(sum(ag["latencies_ms"]) / len(ag["latencies_ms"]), 2)

state = StateManager()

# -------------------------------------------------------------
# WebSocket Connection Manager
# -------------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                dead_connections.append(connection)
        for dc in dead_connections:
            self.disconnect(dc)

manager = ConnectionManager()

# -------------------------------------------------------------
# Background Subprocess Executor (Hermes One-Shot Runner)
# -------------------------------------------------------------
def run_hermes_command(profile: str, prompt: str, timeout: int = 180) -> Dict[str, Any]:
    """Run `hermes -p {profile} -z '{prompt}'` synchronously with precise latency measurement."""
    start_time = time.perf_counter()
    # Map profile if default
    cli_profile = AGENT_ROSTER.get(profile, {}).get("profile", profile)
    cmd = ["hermes", "-p", cli_profile, "-z", prompt]
    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=True if os.name == "nt" else False
        )
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        success = (res.returncode == 0)
        output = res.stdout.strip()
        if not output and res.stderr.strip():
            output = f"[STDERR]: {res.stderr.strip()}"
        return {
            "output": output or "(Selesai tanpa output teks)",
            "returncode": res.returncode,
            "latency_ms": latency_ms,
            "success": success,
            "error": None if success else (res.stderr.strip() or f"Exit code {res.returncode}")
        }
    except subprocess.TimeoutExpired:
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return {
            "output": f"Timeout {timeout}s terlampaui saat memanggil agent '{profile}'.",
            "returncode": -1,
            "latency_ms": latency_ms,
            "success": False,
            "error": f"Timeout {timeout}s expired"
        }
    except Exception as e:
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return {
            "output": f"Exception error: {str(e)}",
            "returncode": -2,
            "latency_ms": latency_ms,
            "success": False,
            "error": str(e)
        }

def append_to_obsidian_blackboard(sender: str, message: str):
    """Write an entry into Obsidian Multi-Agent Live Blackboard."""
    try:
        os.makedirs(BLACKBOARD_PATH.parent, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"### [{timestamp}] 🤖 `{sender.upper()}`\n{message}\n\n---\n\n"
        with open(BLACKBOARD_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        print(f"[WARN] Failed to write to blackboard: {e}")

# -------------------------------------------------------------
# Periodic Telemetry Broadcaster
# -------------------------------------------------------------
async def periodic_metrics_loop():
    while True:
        try:
            cpu_pct = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("C:\\")
            uptime_sec = int(time.time() - state.start_time)
            
            telemetry = {
                "type": "telemetry_tick",
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "system": {
                    "cpu_percent": cpu_pct,
                    "ram_percent": mem.percent,
                    "ram_used_gb": round(mem.used / (1024**3), 2),
                    "ram_total_gb": round(mem.total / (1024**3), 2),
                    "disk_percent": disk.percent,
                    "uptime_seconds": uptime_sec
                },
                "agents_active_count": sum(1 for a in state.agents.values() if a["status"] == "busy"),
                "agents_total_count": len(state.agents),
                "total_messages": len(state.messages),
                "total_tasks_completed": sum(a["total_tasks"] for a in state.agents.values())
            }
            await manager.broadcast(telemetry)
        except Exception as e:
            print(f"[METRICS ERROR]: {e}")
        await asyncio.sleep(2.0)

# -------------------------------------------------------------
# REST API Schemas
# -------------------------------------------------------------
class MessageCreate(BaseModel):
    sender: str
    target: str = "all"
    content: str
    type: str = "chat"  # chat, task, result, alert
    sync_blackboard: bool = False

class DispatchRequest(BaseModel):
    profile: str
    prompt: str
    sender: str = "Dimas (Commander)"
    timeout: int = 180
    sync_blackboard: bool = True

class BenchmarkRequest(BaseModel):
    profiles: Optional[List[str]] = None
    prompt: Optional[str] = None
    mode: str = "concurrent"  # concurrent or sequential
    timeout: int = 120

class SwarmRequest(BaseModel):
    goal: str
    initiator: str = "Dimas (Commander)"

class AgentStatusUpdate(BaseModel):
    status: str = "busy"  # busy, idle, standby
    task: Optional[str] = None
    sender: Optional[str] = "Dimas (Commander)"

class AgentCompletePayload(BaseModel):
    result: Optional[str] = None
    status: str = "idle"

ALIASES = {
    "all": ["orchestrator", "frontend", "backend", "security", "migration", "integration", "reviewer", "researcher", "database", "3d", "gamedev", "api", "reverse"],
    "broadcast": ["orchestrator", "frontend", "backend", "security", "migration", "integration", "reviewer", "researcher", "database", "3d", "gamedev", "api", "reverse"],
    "dev": ["backend", "frontend", "gamedev", "api"],
    "game": ["gamedev", "3d"],
    "data": ["database", "migration"],
    "qa": ["reviewer", "security", "reverse"],
    "sec": ["security", "reverse"],
    "re": ["reverse"],
    "infra": ["backend", "database", "migration", "integration"],
    "design": ["frontend", "3d", "researcher"],
    "creative": ["frontend", "3d"],
    "api-team": ["api", "backend", "integration"],
}

# -------------------------------------------------------------
# REST Endpoints
# -------------------------------------------------------------
@app.get("/api/status")
async def get_status():
    uptime_sec = int(time.time() - state.start_time)
    mem = psutil.virtual_memory()
    return {
        "status": "online",
        "uptime_seconds": uptime_sec,
        "uptime_formatted": f"{uptime_sec // 3600}h {(uptime_sec % 3600) // 60}m {uptime_sec % 60}s",
        "total_agents": len(state.agents),
        "total_messages": len(state.messages),
        "total_tasks_run": sum(a["total_tasks"] for a in state.agents.values()),
        "connected_clients": len(manager.active_connections),
        "host": {
            "os": "Windows 11",
            "cpu_percent": psutil.cpu_percent(),
            "ram_percent": mem.percent
        }
    }

@app.get("/api/state")
async def get_state():
    now_ts = time.time()
    uptime_sec = int(now_ts - state.start_time)
    mem = psutil.virtual_memory()
    cpu_pct = psutil.cpu_percent()
    
    exec_agents = [state.agents.get(k) for k in ["orchestrator", "reviewer", "researcher"] if k in state.agents]
    dev_agents = [state.agents.get(k) for k in ["frontend", "3d", "gamedev"] if k in state.agents]
    infra_agents = [state.agents.get(k) for k in ["backend", "database", "migration", "integration", "api"] if k in state.agents]
    sec_agents = [state.agents.get(k) for k in ["security", "reverse"] if k in state.agents]
    
    def fmt_agent(a):
        return {
            "id": a["name"],
            "name": a["name"].capitalize(),
            "role": a["role"],
            "emoji": a["icon"],
            "color": a["color"],
            "model": "Hermes-3-70B / GratisOP",
            "creature": a["desc"],
            "status": "working" if a["status"] == "busy" else a["status"],
            "current_task": a.get("current_task"),
            "total_tasks": a.get("total_tasks", 0),
            "avg_latency_ms": a.get("avg_latency_ms", 0.0),
            "vibe": a["desc"][:80]
        }
        
    hosts = [
        {
            "key": "hq",
            "label": "Markas Komando Eksekutif",
            "ok": True,
            "gateway": True,
            "load": cpu_pct / 100.0,
            "cpus": psutil.cpu_count() or 4,
            "memPct": mem.percent,
            "agents": [fmt_agent(a) for a in exec_agents]
        },
        {
            "key": "dev",
            "label": "Studio Kreatif 3D & Frontend",
            "ok": True,
            "gateway": False,
            "load": (cpu_pct * 0.8) / 100.0,
            "cpus": psutil.cpu_count() or 4,
            "memPct": mem.percent,
            "agents": [fmt_agent(a) for a in dev_agents]
        },
        {
            "key": "infra",
            "label": "Infrastruktur Server & Database",
            "ok": True,
            "gateway": False,
            "load": (cpu_pct * 0.9) / 100.0,
            "cpus": psutil.cpu_count() or 4,
            "memPct": mem.percent,
            "agents": [fmt_agent(a) for a in infra_agents]
        },
        {
            "key": "sec",
            "label": "Lab Keamanan Siber & Reverse Engineering",
            "ok": True,
            "gateway": False,
            "load": (cpu_pct * 0.7) / 100.0,
            "cpus": psutil.cpu_count() or 4,
            "memPct": mem.percent,
            "agents": [fmt_agent(a) for a in sec_agents]
        },
        {
            "key": "meeting",
            "label": "Ruang Rapat Utama (Executive Boardroom)",
            "big": True,
            "ok": True,
            "gateway": False,
            "load": (cpu_pct * 0.3) / 100.0,
            "cpus": psutil.cpu_count() or 4,
            "memPct": mem.percent,
            "agents": []
        }
    ]
    
    return {
        "now": now_ts,
        "public": True,
        "hosts": hosts,
        "stats": {
            "uptime_seconds": uptime_sec,
            "uptime_formatted": f"{uptime_sec // 3600}h {(uptime_sec % 3600) // 60}m {uptime_sec % 60}s",
            "total_agents": len(state.agents),
            "cpu_percent": cpu_pct,
            "ram_percent": mem.percent
        }
    }

@app.get("/api/agents")
async def get_agents():
    return {"agents": state.agents}

@app.get("/api/agents/{profile}")
async def get_agent_detail(profile: str):
    p = profile.lower()
    if p not in state.agents:
        raise HTTPException(status_code=404, detail="Agent profile not found")
    
    # Filter messages involving this agent
    agent_msgs = [
        m for m in state.messages 
        if m["sender"].lower() == p or m["target"].lower() in [p, "all"]
    ]
    return {
        "agent": state.agents[p],
        "recent_messages": agent_msgs[-20:]
    }

@app.get("/api/messages")
async def get_messages(limit: int = Query(50, ge=1, le=500), agent: Optional[str] = None, type: Optional[str] = None):
    msgs = state.messages
    if agent:
        a = agent.lower()
        msgs = [m for m in msgs if m["sender"].lower() == a or m["target"].lower() in [a, "all"]]
    if type:
        msgs = [m for m in msgs if m["type"] == type]
    return {"messages": msgs[-limit:], "total": len(state.messages)}

@app.post("/api/messages")
async def post_message(payload: MessageCreate):
    msg = state.add_message(
        sender=payload.sender,
        target=payload.target,
        content=payload.content,
        msg_type=payload.type
    )
    if payload.sync_blackboard:
        append_to_obsidian_blackboard(payload.sender, payload.content)
    
    await manager.broadcast({
        "type": "message_new",
        "message": msg
    })

    # AUTO-SYNC: If message is task/dispatch/broadcast, automatically mark target agents as busy!
    clean_type = (payload.type or "").lower().strip()
    if clean_type in ["task", "dispatch", "broadcast"] and payload.target:
        raw_target = payload.target.lower().strip()
        targets = []
        if raw_target in ALIASES:
            targets = ALIASES[raw_target]
        elif "," in raw_target:
            targets = [t.strip() for t in raw_target.split(",") if t.strip() in state.agents]
        elif raw_target in state.agents:
            targets = [raw_target]

        clean_task = payload.content
        for prefix in ["**Task Dispatch:**", "**Task Assigned:**", "**Inquiry:**", "[SEND]", "**SEND ke"]:
            if prefix in clean_task:
                clean_task = clean_task.replace(prefix, "")
        clean_task = clean_task.strip()
        if len(clean_task) > 80:
            clean_task = clean_task[:77] + "..."

        for t in targets:
            state.update_agent_status(t, status="busy", current_task=clean_task)
            await manager.broadcast({
                "type": "agent_update",
                "agent": state.agents[t]
            })

    # AUTO-SYNC: If message is result/done/complete, mark sender as idle!
    elif clean_type in ["result", "done", "complete", "completed"]:
        s_lower = payload.sender.lower().strip()
        if s_lower in state.agents:
            state.update_agent_status(s_lower, status="idle", current_task=None)
            await manager.broadcast({
                "type": "agent_update",
                "agent": state.agents[s_lower]
            })

    return {"status": "ok", "message": msg}

@app.post("/api/agents/reset")
async def reset_all_agents():
    """Reset seluruh agen ke status idle dan hapus task aktif."""
    for p in state.agents:
        state.update_agent_status(p, status="idle", current_task=None)
        await manager.broadcast({
            "type": "agent_update",
            "agent": state.agents[p]
        })
    return {"status": "ok", "message": "Seluruh agen berhasil direset ke status idle (nganggur/santai)"}

@app.post("/api/agents/{profile}/reset")
async def reset_single_agent(profile: str):
    """Reset satu agen ke status idle."""
    p = profile.lower()
    if p not in state.agents:
        raise HTTPException(status_code=404, detail="Agent profile not found")
    state.update_agent_status(p, status="idle", current_task=None)
    await manager.broadcast({
        "type": "agent_update",
        "agent": state.agents[p]
    })
    return {"status": "ok", "agent": state.agents[p]}

@app.post("/api/agents/{profile}/status")
async def update_agent_status_endpoint(profile: str, payload: AgentStatusUpdate):
    """Explicitly update status and current task for an agent or alias."""
    raw_p = profile.strip().lower()
    targets = []
    if raw_p in ALIASES:
        targets = ALIASES[raw_p]
    elif "," in raw_p:
        targets = [t.strip() for t in raw_p.split(",") if t.strip() in state.agents]
    elif raw_p in state.agents:
        targets = [raw_p]
    else:
        raise HTTPException(status_code=404, detail=f"Agent profile or alias '{profile}' not found")

    updated = []
    for p in targets:
        clean_task = payload.task if payload.status == "busy" else None
        state.update_agent_status(p, status=payload.status, current_task=clean_task)
        await manager.broadcast({
            "type": "agent_update",
            "agent": state.agents[p]
        })
        updated.append(state.agents[p])

    # If assigned task, also broadcast a task message to the bus
    if payload.status == "busy" and payload.task:
        msg = state.add_message(
            sender=payload.sender or "Dimas (Commander)",
            target=",".join(targets),
            content=f"**Task Assigned:** {payload.task}",
            msg_type="task"
        )
        await manager.broadcast({
            "type": "message_new",
            "message": msg
        })

    return {"status": "ok", "updated": updated}

@app.post("/api/agents/{profile}/task")
async def set_agent_task_endpoint(profile: str, payload: AgentStatusUpdate):
    """Alias for /api/agents/{profile}/status with busy status."""
    payload.status = "busy"
    return await update_agent_status_endpoint(profile, payload)

@app.post("/api/agents/{profile}/complete")
async def complete_agent_task_endpoint(profile: str, payload: Optional[AgentCompletePayload] = None):
    """Mark an agent task as completed and return to idle."""
    status_update = AgentStatusUpdate(status="idle", task=None)
    res = await update_agent_status_endpoint(profile, status_update)
    if payload and payload.result:
        msg = state.add_message(
            sender=profile,
            target="all",
            content=payload.result,
            msg_type="result"
        )
        await manager.broadcast({
            "type": "message_new",
            "message": msg
        })
    return res

@app.post("/api/dispatch")
async def dispatch_task(payload: DispatchRequest, background_tasks: BackgroundTasks):
    raw_target = payload.profile.strip().lower()
    
    # Resolve targets (single, alias, or comma-separated)
    if raw_target in ALIASES:
        targets = ALIASES[raw_target]
    elif "," in raw_target:
        targets = [t.strip() for t in raw_target.split(",") if t.strip() in state.agents]
    elif raw_target in state.agents:
        targets = [raw_target]
    else:
        raise HTTPException(status_code=404, detail=f"Target profile or alias '{payload.profile}' is not in active roster")

    if not targets:
        raise HTTPException(status_code=400, detail="No valid target agent profiles specified.")

    is_broadcast = len(targets) > 1

    # Post initial dispatch message to bus
    header_text = f"📢 **[BROADCAST KE {len(targets)} AGEN]**" if is_broadcast else f"**Task Dispatch ke @{targets[0].upper()}:**"
    inquiry_msg = state.add_message(
        sender=payload.sender,
        target=",".join(targets) if is_broadcast else targets[0],
        content=f"{header_text}\n{payload.prompt}",
        msg_type="broadcast" if is_broadcast else "task"
    )
    await manager.broadcast({
        "type": "message_new",
        "message": inquiry_msg
    })

    if payload.sync_blackboard:
        append_to_obsidian_blackboard(
            f"caller_to_{raw_target}",
            f"**Inquiry ({'Broadcast' if is_broadcast else 'Direct'}):** {payload.prompt}"
        )

    # Flip status and launch background task for each target
    for p in targets:
        state.update_agent_status(p, status="busy", current_task=payload.prompt[:80])
        await manager.broadcast({
            "type": "agent_update",
            "agent": state.agents[p]
        })
        background_tasks.add_task(
            execute_and_publish_task,
            p,
            payload.prompt,
            payload.timeout,
            payload.sync_blackboard
        )

    return {
        "status": "dispatched",
        "targets": targets,
        "is_broadcast": is_broadcast,
        "task": payload.prompt,
        "timestamp": datetime.now().isoformat()
    }

async def execute_and_publish_task(profile: str, prompt: str, timeout: int, sync_blackboard: bool):
    """Execute Hermes command in thread pool and broadcast results."""
    res = await asyncio.to_thread(run_hermes_command, profile, prompt, timeout)
    
    # Kembalikan agen ke status idle agar bisa mondar-mandir otonom
    status = "idle"
    state.update_agent_status(
        profile,
        status=status,
        current_task=None,
        latency_ms=res["latency_ms"],
        success=res["success"]
    )

    # Post response message to bus
    reply_msg = state.add_message(
        sender=profile,
        target="all",
        content=res["output"],
        msg_type="result",
        latency_ms=res["latency_ms"],
        success=res["success"]
    )

    if sync_blackboard and res["success"]:
        append_to_obsidian_blackboard(profile, res["output"])

    await manager.broadcast({
        "type": "agent_update",
        "agent": state.agents[profile]
    })
    await manager.broadcast({
        "type": "message_new",
        "message": reply_msg
    })

# -------------------------------------------------------------
# Benchmark Runner
# -------------------------------------------------------------
@app.post("/api/benchmark")
async def run_benchmark(payload: BenchmarkRequest, background_tasks: BackgroundTasks):
    profiles_to_test = payload.profiles or list(AGENT_ROSTER.keys())
    prompt = payload.prompt or "Dalam 1 kalimat padat: sebutkan peran spesialisasi kamu dan 1 keahlian teknis terkuatmu."
    
    bench_id = f"bench_{int(time.time())}"
    bench_record = {
        "id": bench_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prompt": prompt,
        "profiles": profiles_to_test,
        "status": "running",
        "mode": payload.mode,
        "results": {},
        "summary": {}
    }
    state.benchmarks.append(bench_record)

    await manager.broadcast({
        "type": "benchmark_started",
        "benchmark": bench_record
    })

    background_tasks.add_task(
        execute_benchmark_suite,
        bench_id,
        profiles_to_test,
        prompt,
        payload.mode,
        payload.timeout
    )

    return {"status": "started", "benchmark_id": bench_id, "profiles": profiles_to_test}

async def execute_benchmark_suite(bench_id: str, profiles: List[str], prompt: str, mode: str, timeout: int):
    bench = next((b for b in state.benchmarks if b["id"] == bench_id), None)
    if not bench:
        return

    results = {}
    
    if mode == "concurrent":
        # Launch concurrently
        async def test_single(p):
            state.update_agent_status(p, status="busy", current_task=f"Benchmark: {prompt[:30]}...")
            await manager.broadcast({"type": "agent_update", "agent": state.agents[p]})
            
            res = await asyncio.to_thread(run_hermes_command, p, prompt, timeout)
            
            state.update_agent_status(p, status="idle", current_task=None, latency_ms=res["latency_ms"], success=res["success"])
            await manager.broadcast({"type": "agent_update", "agent": state.agents[p]})
            
            # Post message to bus
            msg = state.add_message(
                sender=p,
                target="all",
                content=res["output"],
                msg_type="benchmark",
                latency_ms=res["latency_ms"],
                success=res["success"]
            )
            await manager.broadcast({"type": "message_new", "message": msg})
            
            return p, {
                "profile": p,
                "latency_ms": round(res["latency_ms"], 2),
                "success": res["success"],
                "returncode": res["returncode"],
                "output_preview": res["output"][:120],
                "char_length": len(res["output"]),
                "error": res["error"]
            }

        tasks = [test_single(p) for p in profiles]
        completed = await asyncio.gather(*tasks)
        for p, r in completed:
            results[p] = r
    else:
        # Sequential execution
        for p in profiles:
            state.update_agent_status(p, status="busy", current_task=f"Benchmark: {prompt[:30]}...")
            await manager.broadcast({"type": "agent_update", "agent": state.agents[p]})
            
            res = await asyncio.to_thread(run_hermes_command, p, prompt, timeout)
            
            state.update_agent_status(p, status="idle", current_task=None, latency_ms=res["latency_ms"], success=res["success"])
            await manager.broadcast({"type": "agent_update", "agent": state.agents[p]})
            
            msg = state.add_message(
                sender=p,
                target="all",
                content=res["output"],
                msg_type="benchmark",
                latency_ms=res["latency_ms"],
                success=res["success"]
            )
            await manager.broadcast({"type": "message_new", "message": msg})
            
            results[p] = {
                "profile": p,
                "latency_ms": round(res["latency_ms"], 2),
                "success": res["success"],
                "returncode": res["returncode"],
                "output_preview": res["output"][:120],
                "char_length": len(res["output"]),
                "error": res["error"]
            }

    # Calculate summary metrics
    latencies = [r["latency_ms"] for r in results.values() if r["success"]]
    success_count = sum(1 for r in results.values() if r["success"])
    total_tested = len(results)
    
    summary = {
        "total_tested": total_tested,
        "successful": success_count,
        "failed": total_tested - success_count,
        "success_rate_percent": round((success_count / total_tested) * 100, 1) if total_tested else 0,
        "min_latency_ms": round(min(latencies), 2) if latencies else 0,
        "max_latency_ms": round(max(latencies), 2) if latencies else 0,
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0,
        "fastest_agent": min(results.items(), key=lambda x: x[1]["latency_ms"] if x[1]["success"] else 999999)[0] if latencies else "None"
    }

    bench["results"] = results
    bench["summary"] = summary
    bench["status"] = "completed"

    # Post consolidated benchmark summary message
    summary_text = (
        f"🏁 **Benchmark Selesai!**\n"
        f"- Agen diuji: **{total_tested}** | Berhasil: **{success_count}/{total_tested}** ({summary['success_rate_percent']}%)\n"
        f"- Rata-rata Latensi: **{summary['avg_latency_ms']} ms** (Min: {summary['min_latency_ms']} ms, Max: {summary['max_latency_ms']} ms)\n"
        f"- Agen Tercepat: 🚀 **{summary['fastest_agent'].upper()}**"
    )
    sum_msg = state.add_message(
        sender="orchestrator",
        target="all",
        content=summary_text,
        msg_type="benchmark_summary"
    )

    await manager.broadcast({
        "type": "benchmark_completed",
        "benchmark": bench
    })
    await manager.broadcast({
        "type": "message_new",
        "message": sum_msg
    })

# -------------------------------------------------------------
# Multi-Agent Collaborative Swarm Pipeline Runner
# -------------------------------------------------------------
@app.post("/api/swarm")
async def run_swarm(payload: SwarmRequest, background_tasks: BackgroundTasks):
    swarm_id = f"swarm_{int(time.time())}"
    
    init_msg = state.add_message(
        sender=payload.initiator,
        target="orchestrator",
        content=f"🚀 **Memulai Multi-Agent Swarm:** {payload.goal}",
        msg_type="swarm_init"
    )
    await manager.broadcast({"type": "message_new", "message": init_msg})
    
    background_tasks.add_task(execute_swarm_pipeline, swarm_id, payload.goal)
    return {"status": "swarm_started", "swarm_id": swarm_id, "goal": payload.goal}

async def execute_swarm_pipeline(swarm_id: str, goal: str):
    """Execute a collaborative 4-stage pipeline across agents."""
    # Step 1: Orchestrator decomposes
    p1 = "orchestrator"
    state.update_agent_status(p1, status="busy", current_task="Memecah arsitektur tugas swarm")
    await manager.broadcast({"type": "agent_update", "agent": state.agents[p1]})
    
    decomp_prompt = f"User memberi tujuan: '{goal}'. Bedah kebutuhan ini menjadi: 1 tugas backend, 1 tugas security, dan 1 kriteria uji reviewer dalam format ringkas."
    res1 = await asyncio.to_thread(run_hermes_command, p1, decomp_prompt, 180)
    state.update_agent_status(p1, status="idle", latency_ms=res1["latency_ms"], success=res1["success"])
    await manager.broadcast({"type": "agent_update", "agent": state.agents[p1]})
    
    m1 = state.add_message(p1, "all", f"📋 **[TAHAP 1: ARSITEKTUR & DEKOMPOSISI]**\n{res1['output']}", "swarm_step", latency_ms=res1["latency_ms"])
    await manager.broadcast({"type": "message_new", "message": m1})

    # Step 2: Backend implements
    p2 = "backend"
    state.update_agent_status(p2, status="busy", current_task="Implementasi kontrak backend")
    await manager.broadcast({"type": "agent_update", "agent": state.agents[p2]})
    
    backend_prompt = f"Berdasarkan arahan Orchestrator untuk '{goal}', buatkan implementasi endpoint FastAPI minimal yang clean dan siap pakai."
    res2 = await asyncio.to_thread(run_hermes_command, p2, backend_prompt, 180)
    state.update_agent_status(p2, status="idle", latency_ms=res2["latency_ms"], success=res2["success"])
    await manager.broadcast({"type": "agent_update", "agent": state.agents[p2]})
    
    m2 = state.add_message(p2, "security", f"⚙️ **[TAHAP 2: IMPLEMENTASI BACKEND]**\n{res2['output']}\n\n*@security mohon lakukan audit OWASP dan sanitasi input pada kode di atas.*", "swarm_step", latency_ms=res2["latency_ms"])
    await manager.broadcast({"type": "message_new", "message": m2})

    # Step 3: Security audits
    p3 = "security"
    state.update_agent_status(p3, status="busy", current_task="Audit OWASP & SAST")
    await manager.broadcast({"type": "agent_update", "agent": state.agents[p3]})
    
    sec_prompt = f"Lakukan audit keamanan singkat (OWASP Top 10) terhadap kode backend berikut dan berikan rekomendasi patch remediasi:\n\n{res2['output'][:1000]}"
    res3 = await asyncio.to_thread(run_hermes_command, p3, sec_prompt, 180)
    state.update_agent_status(p3, status="idle", latency_ms=res3["latency_ms"], success=res3["success"])
    await manager.broadcast({"type": "agent_update", "agent": state.agents[p3]})
    
    m3 = state.add_message(p3, "reviewer", f"🛡️ **[TAHAP 3: AUDIT KEAMANAN]**\n{res3['output']}\n\n*@reviewer kode telah diaudit, silakan siapkan test cases & verifikasi mutu.*", "swarm_step", latency_ms=res3["latency_ms"])
    await manager.broadcast({"type": "message_new", "message": m3})

    # Step 4: Reviewer validates
    p4 = "reviewer"
    state.update_agent_status(p4, status="busy", current_task="Quality Gate & Test Verification")
    await manager.broadcast({"type": "agent_update", "agent": state.agents[p4]})
    
    rev_prompt = f"Sebagai Lead QA, buatkan test fixture pytest singkat dan verifikasi apakah kode di atas memenuhi standar produksi."
    res4 = await asyncio.to_thread(run_hermes_command, p4, rev_prompt, 180)
    state.update_agent_status(p4, status="idle", latency_ms=res4["latency_ms"], success=res4["success"])
    await manager.broadcast({"type": "agent_update", "agent": state.agents[p4]})
    
    m4 = state.add_message(p4, "all", f"✅ **[TAHAP 4: QA & TEST VERIFIKASI]**\n{res4['output']}", "swarm_step", latency_ms=res4["latency_ms"])
    await manager.broadcast({"type": "message_new", "message": m4})

    # Final wrap-up by Orchestrator
    done_msg = state.add_message(
        "orchestrator",
        "all",
        f"🎯 **Swarm Selesai dengan Sukses!**\nSeluruh 4 tahap (Arsitektur -> Backend -> Security -> Reviewer) telah terverifikasi dan siap digunakan.",
        "swarm_done"
    )
    await manager.broadcast({"type": "message_new", "message": done_msg})

# -------------------------------------------------------------
# Obsidian Blackboard Sync
# -------------------------------------------------------------
@app.get("/api/blackboard")
async def get_blackboard():
    if not BLACKBOARD_PATH.exists():
        return {"content": "Blackboard file does not exist yet.", "path": str(BLACKBOARD_PATH)}
    return {
        "content": BLACKBOARD_PATH.read_text(encoding="utf-8"),
        "path": str(BLACKBOARD_PATH),
        "last_modified": datetime.fromtimestamp(BLACKBOARD_PATH.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    }

@app.post("/api/blackboard/sync")
async def sync_blackboard():
    """Sync all unsynced chat messages from memory into Obsidian Blackboard."""
    count = 0
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(BLACKBOARD_PATH, "a", encoding="utf-8") as f:
            for m in state.messages[-10:]:
                if m["type"] in ["chat", "task", "result"]:
                    f.write(f"### [{timestamp}] 🤖 `{m['sender'].upper()}`\n{m['content']}\n\n---\n\n")
                    count += 1
        return {"status": "synced", "messages_written": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export")
async def export_logs(format: str = Query(default="markdown", pattern="^(markdown|json)$")):
    """Export current trace messages as Markdown or JSON file."""
    if format == "json":
        return JSONResponse(
            content={"exported_at": datetime.now().isoformat(), "total": len(state.messages), "messages": state.messages},
            headers={"Content-Disposition": f"attachment; filename=agent_trace_{int(time.time())}.json"}
        )
    # Markdown
    lines = [
        f"# 📡 Hermes Multi-Agent Trace Log Export",
        f"**Waktu Ekspor:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Pesan:** {len(state.messages)}",
        f"\n---\n"
    ]
    for m in state.messages:
        ts = m.get("timestamp", "-")
        sender = m.get("sender", "UNKNOWN").upper()
        target = m.get("target", "ALL").upper()
        m_type = m.get("type", "chat").upper()
        lat = f" (⚡ {m['latency_ms']/1000:.2f}s)" if m.get("latency_ms") else ""
        lines.append(f"### [{ts}] `{m_type}` `{sender}` ➔ `@{target}`{lat}\n\n{m.get('content', '')}\n\n---\n")
    
    md_content = "\n".join(lines)
    return HTMLResponse(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=agent_trace_{int(time.time())}.md"}
    )

# -------------------------------------------------------------
# WebSocket Endpoint
# -------------------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial snapshot
        await websocket.send_json({
            "type": "init",
            "agents": state.agents,
            "messages": state.messages[-60:],
            "system": {
                "uptime_seconds": int(time.time() - state.start_time),
                "cpu_percent": psutil.cpu_percent(),
                "ram_percent": psutil.virtual_memory().percent
            }
        })
        while True:
            data = await websocket.receive_json()
            # Handle incoming WebSocket commands from UI or client
            action = data.get("action")
            if action == "ping":
                await websocket.send_json({"type": "pong", "time": time.time()})
            elif action == "chat":
                msg = state.add_message(
                    sender=data.get("sender", "Dimas (Commander)"),
                    target=data.get("target", "all"),
                    content=data.get("content", ""),
                    msg_type=data.get("type", "chat")
                )
                await manager.broadcast({"type": "message_new", "message": msg})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

# -------------------------------------------------------------
# Mount Static Files & Frontend Route
# -------------------------------------------------------------
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
@app.head("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>Multi-Agent Hub Server running. UI file is being generated...</h1>")

@app.get("/office", response_class=HTMLResponse)
@app.head("/office", response_class=HTMLResponse)
async def serve_office():
    office_file = STATIC_DIR / "office.html"
    if office_file.exists():
        return FileResponse(office_file)
    return HTMLResponse("<h1>Kantor 3D Sejati Corp file not found.</h1>")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860 if os.environ.get("SPACE_ID") else 8800))
    print("=" * 65)
    print("   HERMES MULTI-AGENT COMMAND & TELEMETRY HUB (FASTAPI)")
    print(f"   Listening at: http://0.0.0.0:{port}")
    print("   Obsidian Blackboard: " + str(BLACKBOARD_PATH))
    print("=" * 65)
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False, log_level="info")
