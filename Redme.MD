# 🎬 YT Video Downloader GUI

> A clean, dark-themed YouTube Video Downloader built with **Python + Tkinter + yt-dlp**.  
> Paste any YouTube URL → title loads instantly → pick quality → hit Download!

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-red?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Features

| Feature | Detail |
|---|---|
| 🔴 Auto Info Fetch | Paste URL → title, channel & duration load automatically |
| 🎬 MP4 Download | 360p / 480p / 720p / 1080p / Best quality |
| 🎵 MP3 Download | Audio-only at 192 kbps |
| 📊 Progress Bar | Real-time speed (MB/s) + ETA display |
| 📁 Folder Picker | Browse & select any save folder from UI |
| 🔔 Sound Alert | System beep when download completes |
| 📂 Open Folder | Click "Yes" on done popup to open save folder instantly |
| 🖥️ Fullscreen UI | Opens maximized — works on any screen size |
| 🔁 Auto Retry | Retries up to 10x on network errors |
| ⚡ Fast Download | 10 MB chunks + 4 parallel fragment downloads |

---

## 📸 Preview

```
┌─────────────────────────────────────────────────────┐
│  ▶  YouTube Downloader               by Mo Aman     │  ← Red header
├─────────────────────────────────────────────────────┤
│  YouTube URL: [ paste link here...          ] [✕]   │
├─────────────────────────────────────────────────────┤
│  🎬  Video Title Here                               │
│      Duration: 4:32  •  Channel: Example Channel   │
├──────────────┬──────────────┬───────────────────────┤
│   Quality    │   Format     │   Save Folder         │
│  ○ Best      │  ● Video MP4 │  C:\Users\...\Videos  │
│  ● 1080p     │  ○ Audio MP3 │  [Browse] [Open]      │
│  ○ 720p      │              │                       │
├─────────────────────────────────────────────────────┤
│  Downloading: video.mp4             2.4 MB/s        │
│  [████████████████░░░░░░░░░░░]  67%   ETA 0:12     │
├─────────────────────────────────────────────────────┤
│           ⬇   DOWNLOAD NOW                         │
└─────────────────────────────────────────────────────┘
```

---

## 🛠️ Requirements

- **Python 3.8+** — [Download](https://python.org)
- **yt-dlp** — YouTube download engine
- **FFmpeg** — Required for MP4 merging & MP3 conversion

---

## 📦 Installation

### Step 1 — Clone the repo
```bash
git clone https://github.com/aman-codes777/yt-video-downloader-gui.git
cd yt-video-downloader-gui
```

### Step 2 — Install Python dependency
```bash
pip install yt-dlp
```

### Step 3 — Install FFmpeg (important!)

**Windows:**
1. Go to 👉 https://www.gyan.dev/ffmpeg/builds/
2. Download `ffmpeg-release-essentials.zip`
3. Extract it → copy the `bin` folder path  
   Example: `C:\ffmpeg\bin`
4. Add to Windows PATH:
   - Search **"Environment Variables"** in Start Menu
   - Click **"Edit the system environment variables"**
   - Under **System Variables** → find `Path` → click **Edit**
   - Click **New** → paste `C:\ffmpeg\bin` → click **OK**

**Verify FFmpeg is working:**
```bash
ffmpeg -version
```
You should see version info — not an error.

---

## ▶️ Run the App

```bash
python downloader.py
```

The app opens **fullscreen** automatically.

---

## 🎮 How to Use

1. **Open** the app → it launches fullscreen
2. **Paste** any YouTube video/playlist URL in the URL box
3. **Wait 1 second** → title, channel & duration appear automatically
4. **Choose Quality** → Best / 1080p / 720p / 480p / 360p
5. **Choose Format** → Video (MP4) or Audio (MP3)
6. **Select Folder** → click Browse to pick where to save
7. **Click** `⬇ DOWNLOAD NOW`
8. Watch the **progress bar** with live speed & ETA
9. **Done popup** appears with a sound alert 🔔
10. Click **Yes** to open the folder directly!

---

## 📁 Project Structure

```
yt-video-downloader-gui/
│
├── downloader.py       ← Main app — run this file
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## ⚠️ Common Issues & Fixes

| Problem | Fix |
|---|---|
| `FFmpeg not found` error | Install FFmpeg and add `bin` folder to PATH |
| Video downloads but no sound | FFmpeg not installed — MP4 needs it to merge audio |
| `ERROR: Requested format not available` | Try a lower quality (720p or 480p) |
| App won't open | Run `pip install yt-dlp` first |
| Slow download | Normal for large files — speed shown in MB/s |

---

## 🔧 Update yt-dlp (if videos stop downloading)

YouTube changes frequently. Update yt-dlp regularly:
```bash
pip install -U yt-dlp
```

---

## 🧑‍💻 Author

**Mo Aman**  
🔗 GitHub: [github.com/aman-codes777](https://github.com/aman-codes777)  
🔗 LinkedIn: [linkedin.com/in/amandeveloper777](https://linkedin.com/in/amandeveloper777)

---

## ⚠️ Disclaimer

This tool is for **personal and educational use only**.  
Please respect copyright laws and YouTube's [Terms of Service](https://www.youtube.com/t/terms).  
Do not use this tool to download copyrighted content without permission.

---

## 📄 License

MIT License — free to use, modify, and share.
