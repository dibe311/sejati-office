import os

file_path = "D:/agent/multi_agent_dashboard/static/office.html"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update POS, titleOf, jobOf, and JOBS
pos_old = '''const POS={trading:"Trader",cs:"Customer Service",social:"Social Media",schedule:"Admin Jadwal",finance:"Finance",gym:"Admin Gym",server:"Teknisi"};

const titleOf=a=>a.title||(jobOf(a)==="boss"?(/ceo/i.test(a.role||"")?"CEO":"Koordinator"):POS[jobOf(a)]||"Staf");'''

pos_new = '''const POS = {
  orchestrator: "Swarm Commander",
  frontend: "UI/UX & 3D",
  backend: "Systems Backend",
  security: "AppSec Sentinel",
  migration: "DB Migration",
  integration: "DevOps & CI/CD",
  reviewer: "Lead QA & Verifier",
  researcher: "Tech Researcher",
  database: "DB Architect",
  "3d": "3D Artist",
  gamedev: "Game Engineer",
  api: "API Specialist",
  soros: "Trader Kuantitatif",
  server: "Hardware / IoT",
  trading: "Trader Kuantitatif",
  boss: "Lead Architect"
};

const titleOf = a => a.title || POS[a.id] || POS[jobOf(a)] || (jobOf(a) === "boss" ? "Swarm Commander" : "Engineer");'''

if pos_old in text:
    text = text.replace(pos_old, pos_new)
    print("Replaced POS & titleOf")
else:
    print("Warning: pos_old not found")

# 2. Update jobOf and JOBS
jobs_old = '''const JOBS={

  trading:{wall:true, act:"point", say:["📈 pantau chart & posisi","📊 cek PnL & stop loss","🔎 scan koin momentum"]},

  boss:{wall:true, act:"point", say:["🧠 bagi tugas ke tim","📋 cek progres semua agent","🎯 susun prioritas hari ini"]},

  cs:{wall:false, act:"phone", say:["📞 balas chat pelanggan","💬 follow-up calon member","🙋 jawab pertanyaan"]},

  social:{wall:false, act:"camera", say:["🎬 rekam konten","📸 foto buat IG","💬 balas komentar"]},

  schedule:{wall:true, act:"point", say:["📅 susun jadwal","⏰ pasang pengingat","🗓️ atur meeting"]},

  finance:{wall:false, act:"forward", say:["💰 catat pengeluaran","🧾 rekap transaksi","📒 hitung saldo"]},

  gym:{wall:false, act:"lift", say:["🏋️ update data member","💪 rekap latihan","📋 cek absensi gym"]},

  server:{wall:false, act:"forward", say:["🗄️ cek log sistem","🔧 rawat server & cron","🧹 bersih-bersih sesi"]},

};

function jobOf(a){const r=((a.role||"")+" "+(a.creature||"")).toLowerCase();

  if(a.framework==="hermes")return"server";

  if(/orchestr|ceo|koordinator/.test(r))return"boss";

  if(/trad/.test(r))return"trading";

  if(/customer|service|\bcs\b/.test(r))return"cs";

  if(/social|media|konten/.test(r))return"social";

  if(/schedule|jadwal/.test(r))return"schedule";

  if(/financ|keuangan|uang/.test(r))return"finance";

  if(/gym|fitness/.test(r))return"gym";

  return"boss"}'''

jobs_new = '''const JOBS = {
  boss: { wall: true, act: "point", say: ["🧠 susun arsitektur swarm", "📋 delegasi tugas ke tim", "🎯 koordinasi deliverable akhir"] },
  frontend: { wall: true, act: "point", say: ["🎨 Three.js 3D WebGL scene", "✨ tuning micro-interactions", "⚡ optimasi bundle UI"] },
  backend: { wall: false, act: "forward", say: ["⚙️ endpoint FastAPI", "🔄 streaming MQTT asyncio", "📡 broadcast WebSocket"] },
  security: { wall: true, act: "point", say: ["🛡️ SAST code audit OWASP", "🔒 hardening API authorization", "🚨 verifikasi zero-vuln"] },
  reviewer: { wall: false, act: "forward", say: ["✅ jalankan pytest suite", "🔍 cek edge cases kode", "💯 verifikasi exit code 0"] },
  researcher: { wall: true, act: "point", say: ["🔬 riset paper AI architecture", "⚖️ benchmark trade-off library", "📚 sinkronisasi Obsidian"] },
  database: { wall: false, act: "forward", say: ["🗄️ indexing query SQLite WAL", "📊 normalisasi PostgreSQL", "⚡ ACID data integrity"] },
  migration: { wall: false, act: "forward", say: ["🔄 zero-downtime migration", "📜 verifikasi rollback down()", "🛡️ validasi constraint skema"] },
  integration: { wall: false, act: "forward", say: ["🔌 webhook receiver HMAC", "🐳 multi-stage Docker build", "🚀 pipeline deploy Vercel"] },
  "3d": { wall: true, act: "point", say: ["🧊 procedural PBR material", "📐 hard-surface 3D model", "🎬 rigging & animation bake"] },
  gamedev: { wall: false, act: "forward", say: ["🎮 Unity 6 C# gameplay loop", "🕹️ physics raycast & collision", "🚀 input state machine"] },
  api: { wall: false, act: "forward", say: ["⚡ Postman collections v2.1", "📄 generate OpenAPI 3.1", "🌐 mock server endpoint"] },
  trading: { wall: true, act: "point", say: ["📈 sinyal VolBreakoutLong", "🌾 panen PnL di kebun Soros", "📊 kalkulasi equity & risk"] },
  server: { wall: false, act: "forward", say: ["🔧 inspeksi hardware ESP32", "🗄️ sensor AquaSmart IoT", "🧹 diagnosa system telemetry"] },
  cs: { wall: false, act: "phone", say: ["📞 balas chat", "💬 konsultasi sistem", "🙋 respon pengguna"] },
  gym: { wall: false, act: "lift", say: ["🏋️ olahraga gym", "💪 treadmill santai", "📋 rekap kebugaran"] },
  finance: { wall: false, act: "forward", say: ["💰 kalkulasi PnL", "🧾 rekap transaksi", "📒 hitung modal"] },
  social: { wall: false, act: "camera", say: ["🎬 render showcase", "📸 tangkapan layar 3D", "💬 update status"] },
  schedule: { wall: true, act: "point", say: ["📅 susun jadwal", "⏰ reminder cronjob", "🗓️ agenda rapat"] }
};

function jobOf(a){
  const id = (a.id || "").toLowerCase();
  const r = ((a.role || "") + " " + (a.creature || "")).toLowerCase();
  if (id === "orchestrator") return "boss";
  if (id === "frontend" || /ui|ux|frontend/.test(r)) return "frontend";
  if (id === "backend" || /fastapi|asyncio|backend/.test(r)) return "backend";
  if (id === "security" || /sec|owasp|pentest/.test(r)) return "security";
  if (id === "reviewer" || /qa|review|test/.test(r)) return "reviewer";
  if (id === "researcher" || /research|riset/.test(r)) return "researcher";
  if (id === "database" || /postgres|sql|sqlite/.test(r)) return "database";
  if (id === "migration" || /migration|alembic/.test(r)) return "migration";
  if (id === "integration" || /devops|docker|ci/.test(r)) return "integration";
  if (id === "3d" || /blender|3d/.test(r)) return "3d";
  if (id === "gamedev" || /unity|game/.test(r)) return "gamedev";
  if (id === "api" || /postman|openapi/.test(r)) return "api";
  if (id === "soros" || /trad/.test(r)) return "trading";
  if (id === "hermes" || a.framework === "hermes") return "server";
  return "boss";
}'''

if jobs_old in text:
    text = text.replace(jobs_old, jobs_new)
    print("Replaced JOBS and jobOf")
else:
    print("Warning: jobs_old not found")

# 3. Update liveStatus
livestatus_old = '''function liveStatus(a,h,now){if(a.status==="offline")return"offline";

  if(demo)return"working";const s=now-(a.lastActive||0);return s<120?"working":s<1800?"recent":"idle"}'''

livestatus_new = '''function liveStatus(a,h,now){
  if(a.status==="offline") return "offline";
  if(demo) return "working";
  if(a.status==="working" || a.status==="busy") return "working";
  if(a.status==="recent") return "recent";
  if(a.status==="idle") return "idle";
  const s = now - (a.lastActive || 0);
  return s < 120 ? "working" : s < 1800 ? "recent" : "idle";
}'''

if livestatus_old in text:
    text = text.replace(livestatus_old, livestatus_new)
    print("Replaced liveStatus")
else:
    print("Warning: livestatus_old not found")

# 4. Update status update label
status_old = '$("#upd").textContent=last?`Data VPS diperbarui ${ago(last,now)} · refresh tiap 20 detik${demo?" · MODE DEMO":""}`:"Menghubungi VPS…";'
status_new = '$("#upd").textContent=`Engine Sejati Corp terhubung · refresh tiap 5 detik${demo?" · MODE DEMO":""}`;'
if status_old in text:
    text = text.replace(status_old, status_new)
    print("Replaced status_old")
else:
    print("Warning: status_old not found")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Polish script executed successfully!")
