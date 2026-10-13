import os

file_path = "D:/agent/multi_agent_dashboard/static/office.html"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('const JOBS=')
end_idx = text.find('/* ================= renderer & kamera', idx)

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
}

'''

text = text[:idx] + jobs_new + text[end_idx:]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Successfully replaced JOBS and jobOf!")
