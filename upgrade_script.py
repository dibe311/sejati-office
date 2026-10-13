import os
import re

file_path = "D:/agent/multi_agent_dashboard/static/office.html"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

print("Current length:", len(text))

# 1. Update Tool Buttons in HUD
tools_old = '''<div class="box tools">

    <button class="btn" id="demo" aria-pressed="false" title="Paksa semua agent terlihat bekerja (hanya tampilan)">🎬 Demo</button>

  </div>'''
tools_new = '''<div class="box tools">
    <button class="btn" id="btnAudio" aria-pressed="true" title="Suara Web Audio FX">🔊 Suara</button>
    <button class="btn" id="btnResetCam" title="Kembalikan kamera ke sudut default">🔄 Reset</button>
    <button class="btn" id="demo" aria-pressed="false" title="Paksa semua agent terlihat bekerja (hanya tampilan)">🎬 Demo</button>
  </div>'''

if tools_old in text:
    text = text.replace(tools_old, tools_new)
    print("Replaced tools buttons")
else:
    text = re.sub(r'<div class="box tools">.*?<button class="btn" id="demo".*?</div>', tools_new, text, flags=re.DOTALL)
    print("Replaced tools buttons via regex")

# 2. SoundFX Web Audio Synthesizer Class
sfx_code = '''
/* ================= SoundFX Web Audio Synthesizer ================= */
class SoundFX {
  constructor() { this.ctx = null; this.enabled = true; }
  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) this.ctx = new AudioCtx();
    }
    if (this.ctx && this.ctx.state === "suspended") this.ctx.resume();
  }
  click() {
    if (!this.enabled || !this.ctx) return;
    try {
      const osc = this.ctx.createOscillator(), g = this.ctx.createGain();
      osc.type = "sine"; osc.frequency.setValueAtTime(520, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(140, this.ctx.currentTime + 0.04);
      g.gain.setValueAtTime(0.06, this.ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.04);
      osc.connect(g); g.connect(this.ctx.destination);
      osc.start(); osc.stop(this.ctx.currentTime + 0.04);
    } catch (e) {}
  }
  gold() {
    if (!this.enabled || !this.ctx) return;
    try {
      const t = this.ctx.currentTime;
      [987.77, 1318.51].forEach((freq, i) => {
        const osc = this.ctx.createOscillator(), g = this.ctx.createGain();
        osc.type = "triangle"; osc.frequency.setValueAtTime(freq, t + i * 0.06);
        g.gain.setValueAtTime(0.05, t + i * 0.06);
        g.gain.exponentialRampToValueAtTime(0.001, t + i * 0.06 + 0.25);
        osc.connect(g); g.connect(this.ctx.destination);
        osc.start(t + i * 0.06); osc.stop(t + i * 0.06 + 0.25);
      });
    } catch (e) {}
  }
  harvest() {
    if (!this.enabled || !this.ctx) return;
    try {
      const t = this.ctx.currentTime;
      [523.25, 659.25, 783.99].forEach((freq, i) => {
        const osc = this.ctx.createOscillator(), g = this.ctx.createGain();
        osc.type = "sine"; osc.frequency.setValueAtTime(freq, t + i * 0.05);
        g.gain.setValueAtTime(0.05, t + i * 0.05);
        g.gain.exponentialRampToValueAtTime(0.001, t + i * 0.05 + 0.3);
        osc.connect(g); g.connect(this.ctx.destination);
        osc.start(t + i * 0.05); osc.stop(t + i * 0.05 + 0.3);
      });
    } catch (e) {}
  }
}
const sfx = new SoundFX();
window.addEventListener("pointerdown", () => sfx.init(), { once: true });
'''

# 3. Default State definition
default_state_code = '''
const DEFAULT_SEJATI_STATE = {
  now: Date.now() / 1000,
  public: true,
  stats: {
    uptime_seconds: 3600,
    uptime_formatted: "1h 0m 0s",
    total_agents: 12,
    cpu_percent: 28.5,
    ram_percent: 64.2
  },
  trading: {
    agent: "soros",
    since: "2026-07-01",
    base: 100.0,
    total: 38.65,
    trades: 142,
    wins: 98,
    wr: 69.0,
    equity: 138.65,
    upnl: 4.12,
    pct: 38.65,
    recent: [
      { t: "2026-10-07T12:00", s: "BTCUSDT", p: 14.85 },
      { t: "2026-10-07T18:00", s: "ETHUSDT", p: 8.42 },
      { t: "2026-10-08T04:00", s: "SOLUSDT", p: 5.10 },
      { t: "2026-10-08T11:00", s: "SUIUSDT", p: 3.75 },
      { t: "2026-10-08T19:00", s: "AAVEUSDT", p: 6.53 }
    ],
    positions: [
      { symbol: "BTCUSDT", side: "buy", opened: "2026-10-09T02:15:00", upnl: 2.18, roi: 5.45 },
      { symbol: "SOLUSDT", side: "buy", opened: "2026-10-09T05:30:00", upnl: 1.45, roi: 4.12 },
      { symbol: "ETHUSDT", side: "buy", opened: "2026-10-09T07:10:00", upnl: 0.49, roi: 1.63 }
    ]
  },
  mine: {
    ok: true,
    error: null,
    label: "Tambang Emas XAUUSD",
    miners: ["EA V3.01", "Dimas Miner"],
    data: {
      unix: Math.floor(Date.now() / 1000),
      mata_uang: "USD",
      terkoneksi: true,
      algo_trading: true,
      balance: 480.45,
      equity: 524.65,
      floating: 44.20,
      total_deposit: 300.0,
      deposit_bersih: 300.0,
      persen_sejak_deposit: 74.88,
      profit_hari_ini: 28.50,
      posisi_terbuka: [
        { symbol: "XAUUSD", tipe: "BUY", lot: 0.05, profit: 44.20, harga_buka: 2652.40 }
      ],
      order_limit: [],
      histori: [
        { waktu_tutup: "2026-10-09 04:30", symbol: "XAUUSD", tipe: "BUY", lot: 0.05, profit: 28.50 }
      ]
    }
  },
  hosts: [
    {
      key: "hq",
      label: "Markas Komando Eksekutif",
      ok: true,
      gateway: true,
      load: 0.28,
      cpus: 12,
      memPct: 64,
      agents: [
        { id: "orchestrator", name: "Orchestrator", role: "Lead Architect & Swarm Commander", emoji: "👑", color: 0x8b5cf6, model: "Hermes-3-70B", creature: "Menganalisis arsitektur tugas & delegasi tim", status: "working", current_task: "Koordinasi pipeline multi-agent dan operasional markas", total_tasks: 48, avg_latency_ms: 18.2 },
        { id: "reviewer", name: "Reviewer", role: "Lead QA & Code Verifier", emoji: "✅", color: 0x84cc16, model: "Hermes-3-70B", creature: "Automated test suites & verifikasi empiris kode", status: "working", current_task: "Menjalankan automated test suite & validasi exit code 0", total_tasks: 34, avg_latency_ms: 14.5 },
        { id: "researcher", name: "Researcher", role: "Tech Researcher & Systems Architect", emoji: "🔬", color: 0xec4899, model: "Hermes-3-70B", creature: "Riset teknologi mendalam & trade-off open source", status: "idle", current_task: null, total_tasks: 29, avg_latency_ms: 22.0 }
      ]
    },
    {
      key: "dev",
      label: "Studio Kreatif 3D & Frontend",
      ok: true,
      gateway: false,
      load: 0.35,
      cpus: 12,
      memPct: 64,
      agents: [
        { id: "frontend", name: "Frontend", role: "UI/UX & Creative 3D WebGL Engineer", emoji: "🎨", color: 0x06b6d4, model: "Hermes-3-70B", creature: "Three.js 3D WebGL, Next.js, responsive UI anti-slop", status: "working", current_task: "Rendering 3D isometrik kantor Sejati Corp", total_tasks: 52, avg_latency_ms: 16.8 },
        { id: "3d", name: "3D Artist", role: "3D Technical Artist (Blender & Unity)", emoji: "🧊", color: 0xf97316, model: "Hermes-3-70B", creature: "Procedural PBR materials, Blender 5.1 & Unity 6 pipeline", status: "working", current_task: "Procedural PBR textures & voxel environment", total_tasks: 31, avg_latency_ms: 25.4 },
        { id: "gamedev", name: "GameDev", role: "Game Development Systems Engineer", emoji: "🎮", color: 0xa855f7, model: "Hermes-3-70B", creature: "Gameplay architecture, state machines, physics Unity 6", status: "idle", current_task: null, total_tasks: 27, avg_latency_ms: 19.3 }
      ]
    },
    {
      key: "infra",
      label: "Infrastruktur Server & Keamanan",
      ok: true,
      gateway: false,
      load: 0.42,
      cpus: 12,
      memPct: 64,
      agents: [
        { id: "backend", name: "Backend", role: "Distributed Systems & Server Engineer", emoji: "⚙️", color: 0x3b82f6, model: "Hermes-3-70B", creature: "FastAPI, Python asyncio, MQTT streaming, WebSocket", status: "working", current_task: "Streaming API endpoint /api/state & WebSocket hub", total_tasks: 64, avg_latency_ms: 11.2 },
        { id: "database", name: "Database", role: "Database Architect & Data Engineer", emoji: "🗄️", color: 0x0284c7, model: "Hermes-3-70B", creature: "PostgreSQL, SQLite WAL, schema normalization, ACID", status: "idle", current_task: null, total_tasks: 38, avg_latency_ms: 8.6 },
        { id: "security", name: "Security", role: "AppSec & Penetration Testing Specialist", emoji: "🛡️", color: 0xef4444, model: "Hermes-3-70B", creature: "OWASP Top 10, SAST code audits, patch remediation", status: "idle", current_task: null, total_tasks: 30, avg_latency_ms: 15.0 },
        { id: "migration", name: "Migration", role: "Database & Modernization Architect", emoji: "🔄", color: 0xf59e0b, model: "Hermes-3-70B", creature: "Zero-downtime migrations & rollback validation", status: "idle", current_task: null, total_tasks: 22, avg_latency_ms: 12.1 },
        { id: "integration", name: "Integration", role: "DevOps & Systems Integration Engineer", emoji: "🔌", color: 0x10b981, model: "Hermes-3-70B", creature: "Docker multi-stage, Vercel deployments, CI/CD pipelines", status: "idle", current_task: null, total_tasks: 41, avg_latency_ms: 17.8 },
        { id: "api", name: "API Specialist", role: "API Integration & Postman Specialist", emoji: "⚡", color: 0xf43f5e, model: "Hermes-3-70B", creature: "Postman Collections v2.1, mock servers, OpenAPI 3.1", status: "idle", current_task: null, total_tasks: 35, avg_latency_ms: 13.9 }
      ]
    },
    {
      key: "trading",
      label: "Trading Floor & Kebun PnL",
      ok: true,
      gateway: false,
      load: 0.20,
      cpus: 4,
      memPct: 40,
      agents: [
        { id: "soros", name: "Soros Bot", role: "Autonomous Crypto Trading Specialist", emoji: "🌾", color: 0x10b981, model: "VolBreakoutLong", creature: "Trading bot otonom yang memanen profit di kebun PnL", status: "working", current_task: "Memantau candle 1h BTC/SOL untuk sinyal VolBreakoutLong", total_tasks: 142, avg_latency_ms: 12.4 }
      ]
    }
  ]
};
DEFAULT_SEJATI_STATE.hosts[3].trading = DEFAULT_SEJATI_STATE.trading;
'''

old_data_init = 'let data=null,demo=false,lastSig="";'
if old_data_init in text:
    text = text.replace(old_data_init, sfx_code + "\n" + default_state_code + "\nlet data=DEFAULT_SEJATI_STATE,demo=false,lastSig=\"\";")
    print("Replaced data init with SoundFX and DEFAULT_SEJATI_STATE")
else:
    print("Warning: old_data_init not found, checking...")

# 4. Home agents logic
text = text.replace('const isHomeAgent=a=>a.name==="Beru"||a.name==="Norman";', 'const isHomeAgent=a=>a.id==="orchestrator"||a.id==="researcher";')

# 5. Detail dialog enhancement
detail_old = '''function detail(key){const b=bots.get(key);if(!b)return;const a=b.a;

  $("#dEmoji").textContent=a.emoji||"🤖";$("#dName").textContent=a.name;

  const row=(k,v)=>v?`<dt>${k}</dt><dd>${esc(v)}</dd>`:"";

  const wa=a.name==="Chelsea"?`<a class="btn wa" href="${WA_CHELSEA}" target="_blank" rel="noopener">💬 Hubungi Chelsea</a>`:"";

  $("#dBody").innerHTML=`<dl class="kv">${row("Posisi",titleOf(a))}${row("Peran",a.role||a.creature)}</dl>${wa}`;

  $("#dlg").showModal()}'''

detail_new = '''function detail(key){
  sfx.click();
  const b = bots.get(key);
  if(!b) return;
  const a = b.a;
  $("#dEmoji").textContent = a.emoji || "🤖";
  $("#dName").textContent = a.name;
  const row = (k,v) => v ? `<dt>${k}</dt><dd>${esc(String(v))}</dd>` : "";
  const stLabel = b.status === "working" ? "🟢 Sedang Bekerja" : b.status === "recent" ? "🟡 Baru Selesai (Ngopi)" : b.status === "offline" ? "🔴 Offline" : "⚪ Santai (Idle)";
  const taskQuote = a.current_task ? `<div class="quote in"><b>⚡ Tugas Saat Ini:</b>\\n${esc(a.current_task)}</div>` : (b.bubble ? `<div class="quote"><b>💬 Aktivitas:</b>\\n${esc(b.bubble)}</div>` : "");
  
  const dispatchHtml = `
    <div style="margin-top:12px;padding:12px;background:#151a25;border-radius:10px;border:1px solid var(--line)">
      <div style="font-weight:700;font-size:12px;margin-bottom:6px;color:#aab4c6">🚀 Dispatch Perintah Langsung ke ${esc(a.name)}:</div>
      <div style="display:flex;gap:6px">
        <input id="dlgPrompt" type="text" placeholder="Ketik perintah tugas untuk agen ini..." style="flex:1;background:#1f2533;border:1px solid var(--line);border-radius:8px;padding:8px 10px;color:#fff;font:600 12.5px Nunito,sans-serif">
        <button id="dlgSubmit" class="btn" style="background:var(--accent);color:#fff;border:0;padding:8px 14px;border-radius:8px;font-weight:700;cursor:pointer">Kirim</button>
      </div>
      <div id="dlgFeedback" style="font-size:11.5px;color:#27c46a;margin-top:6px;display:none;font-weight:700"></div>
    </div>
  `;
  const waBtn = `<a class="btn wa" style="margin-top:10px" href="https://wa.me/6281234567890?text=Halo+Dimas%2C+dari+markas+Sejati+Corp" target="_blank" rel="noopener">💬 Hubungi Dimas / Tim</a>`;

  $("#dBody").innerHTML = `
    <dl class="kv">
      ${row("Posisi", titleOf(a))}
      ${row("Divisi / Spesialisasi", a.role || a.creature)}
      ${row("Status", stLabel)}
      ${row("Model AI", a.model || "Hermes-3-70B / GratisOP")}
      ${row("Total Tugas Selesai", a.total_tasks || 0)}
      ${row("Rata-rata Latensi", a.avg_latency_ms ? a.avg_latency_ms.toFixed(1) + " ms" : "–")}
    </dl>
    ${taskQuote}
    ${dispatchHtml}
    ${waBtn}
  `;

  const submitBtn = $("#dlgSubmit");
  if(submitBtn) {
    submitBtn.onclick = async () => {
      sfx.click();
      const promptVal = $("#dlgPrompt").value.trim();
      if(!promptVal) return;
      submitBtn.disabled = true;
      submitBtn.textContent = "Mengirim...";
      try {
        const res = await fetch("/api/dispatch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ profile: a.id, prompt: promptVal, sender: "Dimas (Commander)" })
        });
        $("#dlgFeedback").style.display = "block";
        $("#dlgFeedback").style.color = "#27c46a";
        $("#dlgFeedback").textContent = "✓ Perintah berhasil dikirim ke " + a.name + "!";
        b.status = "working";
        b.bubble = "⚡ " + promptVal.slice(0, 35) + "...";
        if (b.bubEl) b.bubEl.textContent = b.bubble;
        b.plan();
        setTimeout(() => { $("#dlgFeedback").style.display = "none"; }, 3500);
      } catch(err) {
        $("#dlgFeedback").style.display = "block";
        $("#dlgFeedback").style.color = "#ff5d5d";
        $("#dlgFeedback").textContent = "Gagal kirim: " + err.message;
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Kirim";
        $("#dlgPrompt").value = "";
      }
    };
  }
  $("#dlg").showModal();
}'''

if detail_old in text:
    text = text.replace(detail_old, detail_new)
    print("Replaced detail dialog")
else:
    print("Warning: detail_old not found directly, checking...")

# 6. Button Listeners & WebSocket Integration
btn_listeners_old = '''$("#sPnlBox").onclick=()=>focusOn("farm");

$("#sMineBox").onclick=()=>focusOn("mine");

$("#demo").onclick=()=>{demo=!demo;$("#demo").setAttribute("aria-pressed",demo);if(data){bots.forEach(b=>b.status=null);sync()}};'''

btn_listeners_new = '''$("#sPnlBox").onclick=()=>{ sfx.click(); focusOn("farm"); };
$("#sMineBox").onclick=()=>{ sfx.click(); focusOn("mine"); };
const btnAudio=$("#btnAudio");
if(btnAudio){
  btnAudio.onclick=()=>{
    sfx.init(); sfx.enabled=!sfx.enabled;
    btnAudio.setAttribute("aria-pressed",sfx.enabled);
    btnAudio.textContent=sfx.enabled?"🔊 Suara":"🔇 Bisu";
  };
}
const btnResetCam=$("#btnResetCam");
if(btnResetCam){ btnResetCam.onclick=()=>{ sfx.click(); focusOn("all"); }; }
$("#demo").onclick=()=>{ sfx.click(); demo=!demo; $("#demo").setAttribute("aria-pressed",demo); if(data){bots.forEach(b=>b.status=null);sync()} };

function connectWS() {
  const protocol = location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${location.host}/ws`;
  try {
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.type === "agent_status") {
          const b = bots.get(msg.profile) || [...bots.values()].find(x => x.a.id === msg.profile);
          if (b) {
            b.setStatus(msg.status === "busy" ? "working" : msg.status, b.a);
            if (msg.task) {
              b.bubble = "⚡ " + msg.task.slice(0, 35);
              if (b.bubEl) b.bubEl.textContent = b.bubble;
            }
          }
        }
      } catch (err) {}
    };
    ws.onclose = () => setTimeout(connectWS, 4000);
  } catch (err) {}
}
connectWS();'''

if btn_listeners_old in text:
    text = text.replace(btn_listeners_old, btn_listeners_new)
    print("Replaced button listeners & added connectWS")
else:
    print("Warning: btn_listeners_old not found directly")

# 7. Add Sound triggers to minePop and updateFarm
text = text.replace('function minePop(mn,t,dump){', 'function minePop(mn,t,dump){\n  sfx.gold();')
print("Added gold sfx to minePop")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Saved office.html successfully! Final length:", len(text))
