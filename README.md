# 🤖 Hermes Multi-Agent Command & Telemetry Hub

Dashboard interaktif real-time berkinerja tinggi untuk memantau, menguji, dan mengorkestrasi armada 8 AI agent spesialis Hermes secara bersamaan.

---

## 🌟 Fitur Utama

1. **Dashboard Interaktif Real-Time**:
   - Web interface modern bertema obsidian/cyberpunk dengan animasi mulus dan glassmorphism.
   - Menggunakan WebSocket dua arah (`/ws`) dengan siaran latensi rendah (<10ms).
   - Indikator status agen live: `IDLE` (siap), `SIBUK` (sedang memproses), `ERROR`.

2. **Pengujian Kinerja & Benchmark Terpadu**:
   - **Benchmark Runner**: Menguji kecepatan respons, throughput, dan tingkat keberhasilan seluruh 8 agen secara serentak (*concurrent*) atau berurutan (*sequential*).
   - **Leaderboard Kecepatan**: Menampilkan ranking agen tercepat dengan medali (🥇 🥈 🥉) dan metrik latensi dalam milidetik (ms).
   - **Grafik Analitik (Chart.js)**:
     - Grafik perbandingan latensi antar-agen.
     - Grafik timeline beban sistem host (CPU & RAM) secara realtime.
     - Grafik distribusi beban kerja antar-agen.

3. **Bus Komunikasi & Kolaborasi Antar-Agent**:
   - Saluran obrolan terpadu di mana semua agen dapat saling mengirim pesan, kontrak API, dan hasil pengujian.
   - Dukungan pesan langsung antar-agen (`@backend ➔ @security`).
   - Console Komandan untuk Dimas Aryo Sejati: kirim obrolan santai atau eksekusi perintah CLI nyata (`hermes -p <profile> -z`) langsung dari browser!

4. **Multi-Agent Swarm Pipeline**:
   - Mode otomatisasi kolaboratif 4-tahap:
     1. 👑 **Orchestrator**: Dekomposisi tugas & kebutuhan arsitektur.
     2. ⚙️ **Backend**: Pembuatan kode endpoint dan skema validasi.
     3. 🛡️ **Security**: Audit keamanan OWASP Top 10 dan patch remediasi.
     4. ✅ **Reviewer**: Verifikasi edge-cases dan pembuatan test suite.

5. **Sinkronisasi Otomatis ke Obsidian Second Brain**:
   - Terintegrasi langsung dengan `D:\agent\agent brain\07 - Multi-Agent System\Multi-Agent Live Blackboard.md`.
   - Menjaga konteks jangka panjang tetap tersimpan di Obsidian vault.

---

## 🚀 Cara Menjalankan

### 1. Menjalankan Server Hub
Buka terminal dan jalankan:
```bash
cd "D:/agent/multi_agent_dashboard"
python server.py
```
Atau cukup klik dua kali file:
`D:\agent\multi_agent_dashboard\start_dashboard.bat`

### 2. Membuka Dashboard di Browser
Buka browser favorit Anda dan akses:
👉 **`http://localhost:8800`**

---

## 🛠️ API & Integrasi CLI Agen

Agen atau skrip otomasi dapat berinteraksi dengan dashboard menggunakan:

### 1. Mengirim Pesan Antar-Agen via CLI
```bash
python agent_client.py send --from backend --to security --msg "Kontrak API sensor telah siap, mohon diaudit." --type task
```

### 2. Menjalankan Tugas Agen Langsung
```bash
python agent_client.py dispatch --agent backend --prompt "Buat skema Pydantic untuk sensor pH"
```

### 3. Cek Status Armada
```bash
python agent_client.py status
```

### 4. Sinkronisasi Manual ke Blackboard Obsidian
```bash
python agent_client.py sync
```

---

## 👥 8 Profil Agen Spesialis

| Agen | Profil | Warna | Peran Utama |
| :--- | :--- | :--- | :--- |
| **Orchestrator** | `default` | Violet | Lead Architect & Komandan Swarm |
| **Frontend** | `frontend` | Cyan | UI/UX & Creative 3D WebGL Engineer |
| **Backend** | `backend` | Biru | Distributed Systems & Server Engineer |
| **Security** | `security` | Merah | AppSec & Penetration Testing Specialist |
| **Migration** | `migration` | Kuning | Database & Modernization Architect |
| **Integration** | `integration` | Hijau | DevOps & Systems Integration Engineer |
| **Reviewer** | `reviewer` | Lime | Lead QA & Code Verifier |
| **Researcher** | `researcher` | Pink | Tech Researcher & Systems Architect |
