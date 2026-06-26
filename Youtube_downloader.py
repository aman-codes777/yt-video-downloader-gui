import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
import subprocess
import yt_dlp

# ──────────────────────────────────────────────────────────────
#  COLORS & FONTS
# ──────────────────────────────────────────────────────────────
BG      = "#0d0d0d"
CARD    = "#181818"
CARD2   = "#1f1f1f"
ACCENT  = "#ff0000"
ACCENT2 = "#cc0000"
TEXT    = "#ffffff"
SUB     = "#aaaaaa"
SUCCESS = "#00e676"
ERR     = "#ff5252"
BORDER  = "#2c2c2c"

F       = ("Segoe UI", 10)
FB      = ("Segoe UI", 10, "bold")
FLG     = ("Segoe UI", 15, "bold")
FSM     = ("Segoe UI", 9)
FHDR    = ("Segoe UI", 17, "bold")


def play_sound_windows():
    """Play a system beep / ding on download complete (Windows only, no extra libs)."""
    try:
        import winsound
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception:
        pass  # non-Windows or unavailable — silently skip


def open_folder(path):
    """Open the save folder in File Explorer / Finder / Nautilus."""
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────
#  MAIN APP
# ──────────────────────────────────────────────────────────────
class YTDownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader  —  Mo Aman")
        self.configure(bg=BG)

        # ── Full-screen on start ──────────────────────────────
        self.state("zoomed")          # Windows maximized
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{sw}x{sh}+0+0")
        self.resizable(True, True)

        # ── Vars ─────────────────────────────────────────────
        self.save_folder  = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.quality_var  = tk.StringVar(value="720p")
        self.type_var     = tk.StringVar(value="Video (MP4)")
        self.url_var      = tk.StringVar()
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var   = tk.StringVar(value="Paste a YouTube URL above and video info will appear automatically")
        self.speed_var    = tk.StringVar(value="")
        self.eta_var      = tk.StringVar(value="")

        self._fetch_after = None
        self._downloading = False
        self._last_folder = self.save_folder.get()

        self._build_ui()
        self.url_var.trace_add("write", self._on_url_change)

    # ──────────────────────────────────────────────────────────
    #  BUILD UI
    # ──────────────────────────────────────────────────────────
    def _build_ui(self):
        # ROOT grid: header + body
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # ── HEADER ───────────────────────────────────────────
        hdr = tk.Frame(self, bg=ACCENT, height=64)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="▶  YouTube Downloader",
                 bg=ACCENT, fg=TEXT, font=FHDR, pady=16).pack(side="left", padx=24)
        tk.Label(hdr, text="by Mo Aman",
                 bg=ACCENT, fg="#ffcccc", font=FSM).pack(side="right", padx=24)

        # ── BODY (scrollable canvas so it works on any screen) ─
        body_outer = tk.Frame(self, bg=BG)
        body_outer.grid(row=1, column=0, sticky="nsew")
        body_outer.rowconfigure(0, weight=1)
        body_outer.columnconfigure(0, weight=1)

        canvas = tk.Canvas(body_outer, bg=BG, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(body_outer, orient="vertical", command=canvas.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=vsb.set)

        body = tk.Frame(canvas, bg=BG)
        body_win = canvas.create_window((0, 0), window=body, anchor="nw")

        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_resize(e):
            canvas.itemconfig(body_win, width=e.width)

        body.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_canvas_resize)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        PADX = 28   # only horizontal padding — avoids pady conflict

        # ── URL CARD ─────────────────────────────────────────
        url_card = tk.Frame(body, bg=CARD, pady=18, padx=22,
                            highlightbackground=BORDER, highlightthickness=1)
        url_card.pack(fill="x", padx=PADX, pady=(20, 0))

        tk.Label(url_card, text="YouTube URL", bg=CARD, fg=SUB,
                 font=FSM).pack(anchor="w")

        url_row = tk.Frame(url_card, bg=CARD)
        url_row.pack(fill="x", pady=(6, 0))

        self.url_entry = tk.Entry(url_row, textvariable=self.url_var,
                                  bg="#252525", fg=TEXT, insertbackground=TEXT,
                                  relief="flat", font=("Segoe UI", 12), bd=0)
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=10, ipadx=10)
        self.url_entry.focus()

        tk.Button(url_row, text="✕  Clear", bg="#252525", fg=SUB,
                  relief="flat", font=FSM, cursor="hand2",
                  activebackground="#333", activeforeground=TEXT,
                  command=self._clear_url, bd=0, padx=12,
                  pady=10).pack(side="left", padx=(4, 0))

        # ── VIDEO INFO CARD ───────────────────────────────────
        info_card = tk.Frame(body, bg=CARD, pady=16, padx=22,
                             highlightbackground=BORDER, highlightthickness=1)
        info_card.pack(fill="x", padx=PADX, pady=(12, 0))

        left = tk.Frame(info_card, bg=CARD)
        left.pack(side="left", padx=(0, 16))
        self.thumb_lbl = tk.Label(left, text="🎬", bg=CARD, fg="#333",
                                  font=("Segoe UI", 40))
        self.thumb_lbl.pack()

        right = tk.Frame(info_card, bg=CARD)
        right.pack(side="left", fill="x", expand=True)

        self.title_lbl = tk.Label(right, text="No video loaded",
                                  bg=CARD, fg=SUB, font=FLG,
                                  anchor="w", wraplength=900, justify="left")
        self.title_lbl.pack(anchor="w")

        meta = tk.Frame(right, bg=CARD)
        meta.pack(anchor="w", pady=(6, 0))
        self.dur_lbl  = tk.Label(meta, text="Duration: —", bg=CARD, fg=SUB, font=FSM)
        self.dur_lbl.pack(side="left")
        tk.Label(meta, text="   •   ", bg=CARD, fg=BORDER, font=FSM).pack(side="left")
        self.chan_lbl = tk.Label(meta, text="Channel: —",  bg=CARD, fg=SUB, font=FSM)
        self.chan_lbl.pack(side="left")

        self.fetch_lbl = tk.Label(info_card, text="", bg=CARD,
                                  fg=ACCENT, font=FB)
        self.fetch_lbl.pack(side="right")

        # ── SETTINGS ROW ──────────────────────────────────────
        settings = tk.Frame(body, bg=BG)
        settings.pack(fill="x", padx=PADX, pady=(14, 0))
        settings.columnconfigure(0, weight=1)
        settings.columnconfigure(1, weight=1)
        settings.columnconfigure(2, weight=2)

        # Quality
        qf = tk.Frame(settings, bg=CARD, padx=16, pady=14,
                      highlightbackground=BORDER, highlightthickness=1)
        qf.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        tk.Label(qf, text="Quality", bg=CARD, fg=SUB, font=FSM).pack(anchor="w")
        for q in ["Best", "1080p", "720p", "480p", "360p"]:
            tk.Radiobutton(qf, text=q, variable=self.quality_var,
                           value=q.lower(), bg=CARD, fg=TEXT,
                           selectcolor=ACCENT, activebackground=CARD,
                           activeforeground=TEXT, font=F,
                           cursor="hand2").pack(anchor="w", pady=1)

        # Format
        tf = tk.Frame(settings, bg=CARD, padx=16, pady=14,
                      highlightbackground=BORDER, highlightthickness=1)
        tf.grid(row=0, column=1, sticky="nsew", padx=(0, 7))
        tk.Label(tf, text="Format", bg=CARD, fg=SUB, font=FSM).pack(anchor="w")
        for t in ["Video (MP4)", "Audio (MP3)"]:
            tk.Radiobutton(tf, text=t, variable=self.type_var,
                           value=t, bg=CARD, fg=TEXT,
                           selectcolor=ACCENT, activebackground=CARD,
                           activeforeground=TEXT, font=F,
                           cursor="hand2").pack(anchor="w", pady=1)

        # Folder
        ff = tk.Frame(settings, bg=CARD, padx=16, pady=14,
                      highlightbackground=BORDER, highlightthickness=1)
        ff.grid(row=0, column=2, sticky="nsew")
        tk.Label(ff, text="Save Folder", bg=CARD, fg=SUB, font=FSM).pack(anchor="w")
        tk.Entry(ff, textvariable=self.save_folder,
                 bg="#252525", fg=TEXT, insertbackground=TEXT,
                 relief="flat", font=FSM, bd=0).pack(fill="x", ipady=6, pady=(6, 8))
        btn_row = tk.Frame(ff, bg=CARD)
        btn_row.pack(anchor="w")
        tk.Button(btn_row, text="📂  Browse",
                  bg="#252525", fg=TEXT, relief="flat",
                  font=FSM, cursor="hand2",
                  activebackground="#333", activeforeground=TEXT,
                  command=self._browse_folder,
                  padx=10, pady=6).pack(side="left")
        self.open_folder_btn = tk.Button(btn_row, text="📁  Open Folder",
                  bg="#252525", fg=SUB, relief="flat",
                  font=FSM, cursor="hand2",
                  activebackground="#333", activeforeground=TEXT,
                  command=lambda: open_folder(self.save_folder.get()),
                  padx=10, pady=6)
        self.open_folder_btn.pack(side="left", padx=(8, 0))

        # ── PROGRESS CARD ─────────────────────────────────────
        prog_card = tk.Frame(body, bg=CARD, pady=16, padx=22,
                             highlightbackground=BORDER, highlightthickness=1)
        prog_card.pack(fill="x", padx=PADX, pady=(14, 0))

        top_row = tk.Frame(prog_card, bg=CARD)
        top_row.pack(fill="x")
        self.status_lbl = tk.Label(top_row, textvariable=self.status_var,
                                   bg=CARD, fg=SUB, font=FSM, anchor="w")
        self.status_lbl.pack(side="left")
        self.speed_lbl = tk.Label(top_row, textvariable=self.speed_var,
                                  bg=CARD, fg=ACCENT, font=FB)
        self.speed_lbl.pack(side="right")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("YT.Horizontal.TProgressbar",
                        troughcolor=BORDER, background=ACCENT,
                        bordercolor=CARD, lightcolor=ACCENT, darkcolor=ACCENT,
                        thickness=18)
        self.pbar = ttk.Progressbar(prog_card, variable=self.progress_var,
                                    maximum=100, style="YT.Horizontal.TProgressbar")
        self.pbar.pack(fill="x", pady=(10, 4))

        self.eta_lbl = tk.Label(prog_card, textvariable=self.eta_var,
                                bg=CARD, fg=SUB, font=FSM, anchor="e")
        self.eta_lbl.pack(fill="x")

        # ── DOWNLOAD BUTTON ───────────────────────────────────
        self.dl_btn = tk.Button(body, text="⬇   DOWNLOAD NOW",
                                bg=ACCENT, fg=TEXT,
                                font=("Segoe UI", 14, "bold"),
                                relief="flat", cursor="hand2",
                                activebackground=ACCENT2, activeforeground=TEXT,
                                command=self._start_download,
                                pady=18)
        self.dl_btn.pack(fill="x", padx=PADX, pady=(16, 6))

        # Hover effect on download button
        self.dl_btn.bind("<Enter>", lambda e: self.dl_btn.config(bg=ACCENT2))
        self.dl_btn.bind("<Leave>", lambda e: self.dl_btn.config(
            bg=ACCENT if not self._downloading else "#555"))

        # ── TIPS ─────────────────────────────────────────────
        tips = tk.Frame(body, bg=CARD2, padx=20, pady=12,
                        highlightbackground=BORDER, highlightthickness=1)
        tips.pack(fill="x", padx=PADX, pady=(4, 24))
        tk.Label(tips, text="💡  Tips", bg=CARD2, fg=ACCENT, font=FB).pack(anchor="w")
        for tip in [
            "• Make sure FFmpeg is installed and added to PATH for MP4 downloads with sound.",
            "• For best quality with audio, choose 'Best' or '1080p' — yt-dlp merges video + audio automatically.",
            "• Audio (MP3) mode downloads only sound at 192 kbps quality.",
            "• If a video fails, try a different quality setting.",
        ]:
            tk.Label(tips, text=tip, bg=CARD2, fg=SUB, font=FSM,
                     anchor="w", justify="left").pack(anchor="w")

    def _card(self, parent, pady_top=0):
        pass  # placeholder for spacing

    # ──────────────────────────────────────────────────────────
    #  URL AUTO-FETCH
    # ──────────────────────────────────────────────────────────
    def _on_url_change(self, *_):
        if self._fetch_after:
            self.after_cancel(self._fetch_after)
        url = self.url_var.get().strip()
        if not url:
            self._reset_info()
            return
        self._fetch_after = self.after(700, lambda: self._fetch_info(url))

    def _fetch_info(self, url):
        self.fetch_lbl.config(text="⏳ Loading...")
        self.title_lbl.config(text="Fetching video info...", fg=SUB)
        self.dur_lbl.config(text="Duration: —")
        self.chan_lbl.config(text="Channel: —")
        self.thumb_lbl.config(fg="#333")
        threading.Thread(target=self._fetch_thread, args=(url,), daemon=True).start()

    def _fetch_thread(self, url):
        opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "ignoreerrors": True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            if not info:
                raise ValueError("No video info returned. Check the URL.")
            title   = info.get("title", "Unknown Title")
            dur     = info.get("duration", 0) or 0
            channel = info.get("uploader", "Unknown Channel")
            mins, secs = divmod(int(dur), 60)
            self.after(0, self._set_info, title, f"{mins}:{secs:02d}", channel)
        except Exception as e:
            self.after(0, self._info_error, str(e))

    def _set_info(self, title, dur, channel):
        self.fetch_lbl.config(text="✅ Ready")
        self.title_lbl.config(text=title, fg=TEXT)
        self.dur_lbl.config(text=f"Duration: {dur}")
        self.chan_lbl.config(text=f"Channel: {channel}")
        self.thumb_lbl.config(text="🎬", fg=ACCENT)
        self.status_var.set("✅ Video info loaded — click DOWNLOAD NOW to start")

    def _info_error(self, msg):
        self.fetch_lbl.config(text="❌ Error")
        self.title_lbl.config(text="Could not load video. Please check the URL.", fg=ERR)
        self.status_var.set(f"Error: {msg[:100]}")

    def _reset_info(self):
        self.fetch_lbl.config(text="")
        self.title_lbl.config(text="No video loaded", fg=SUB)
        self.dur_lbl.config(text="Duration: —")
        self.chan_lbl.config(text="Channel: —")
        self.thumb_lbl.config(text="🎬", fg="#333")
        self.status_var.set("Paste a YouTube URL above and video info will appear automatically")
        self.progress_var.set(0)
        self.speed_var.set("")
        self.eta_var.set("")

    # ──────────────────────────────────────────────────────────
    #  BROWSE / CLEAR
    # ──────────────────────────────────────────────────────────
    def _browse_folder(self):
        f = filedialog.askdirectory(initialdir=self.save_folder.get())
        if f:
            self.save_folder.set(f)

    def _clear_url(self):
        self.url_var.set("")
        self._reset_info()

    # ──────────────────────────────────────────────────────────
    #  DOWNLOAD
    # ──────────────────────────────────────────────────────────
    def _start_download(self):
        if self._downloading:
            return
        url    = self.url_var.get().strip()
        folder = self.save_folder.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please paste a YouTube URL first.")
            return
        if not folder:
            messagebox.showwarning("No Folder", "Please select a save folder.")
            return
        os.makedirs(folder, exist_ok=True)
        self._downloading = True
        self.dl_btn.config(text="⏳  DOWNLOADING...  Please wait", bg="#444", state="disabled")
        self.progress_var.set(0)
        self.speed_var.set("")
        self.eta_var.set("")
        self.status_var.set("Starting download...")
        self.status_lbl.config(fg=SUB)
        threading.Thread(target=self._dl_thread, args=(url, folder), daemon=True).start()

    def _dl_thread(self, url, folder):
        quality  = self.quality_var.get()
        is_audio = self.type_var.get() == "Audio (MP3)"

        # Format strings — always include audio stream for MP4
        fmt_map = {
            "best":  "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p":  "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p":  "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best[height<=480]",
            "360p":  "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=360]+bestaudio/best[height<=360]",
        }

        if is_audio:
            selected = "bestaudio/best"
            pp = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
            merge_fmt = None
        else:
            selected = fmt_map.get(quality, fmt_map["best"])
            pp = []   # yt-dlp merges automatically when format has two streams
            merge_fmt = "mp4"

        ydl_opts = {
            "format":               selected,
            "outtmpl":              os.path.join(folder, "%(title)s.%(ext)s"),
            "merge_output_format":  merge_fmt,
            "postprocessors":       pp,
            "quiet":                True,
            "no_warnings":          True,
            "progress_hooks":       [self._hook],
            "ignoreerrors":         True,   # skip broken videos, don't crash
            "retries":              10,
            "fragment_retries":     10,
            "http_chunk_size":      10485760,  # 10 MB chunks — faster + stable
            "concurrent_fragment_downloads": 4,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.after(0, self._done, folder)
        except Exception as e:
            self.after(0, self._error, str(e))

    def _hook(self, d):
        if d["status"] == "downloading":
            total      = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            speed      = d.get("speed") or 0
            eta        = d.get("eta") or 0
            pct        = (downloaded / total * 100) if total else 0

            if speed >= 1024 * 1024:
                spd_str = f"{speed/1024/1024:.1f} MB/s"
            else:
                spd_str = f"{speed/1024:.0f} KB/s"

            eta_str  = f"ETA  {eta//60}:{eta%60:02d}" if eta else ""
            fname    = os.path.basename(d.get("filename", ""))
            stat_str = f"Downloading: {fname[:60]}"
            self.after(0, self._upd, pct, spd_str, eta_str, stat_str)

        elif d["status"] == "finished":
            self.after(0, self._upd, 98, "", "", "⚙️  Merging video + audio (FFmpeg)...")

    def _upd(self, pct, spd, eta, stat):
        self.progress_var.set(pct)
        self.speed_var.set(spd)
        self.eta_var.set(eta)
        self.status_var.set(stat)

    def _done(self, folder):
        self.progress_var.set(100)
        self.speed_var.set("")
        self.eta_var.set("")
        self.status_var.set("✅  Download complete!")
        self.status_lbl.config(fg=SUCCESS)
        self.dl_btn.config(text="⬇   DOWNLOAD NOW", bg=ACCENT, state="normal")
        self._downloading = False
        play_sound_windows()   # 🔔 beep / ding on completion
        result = messagebox.askquestion(
            "✅ Download Complete!",
            f"Your file has been saved to:\n{folder}\n\nOpen folder now?",
            icon="info"
        )
        if result == "yes":
            open_folder(folder)
        self.status_lbl.config(fg=SUB)

    def _error(self, msg):
        self.progress_var.set(0)
        self.speed_var.set("")
        self.eta_var.set("")
        self.status_var.set(f"❌ Error occurred")
        self.status_lbl.config(fg=ERR)
        self.dl_btn.config(text="⬇   DOWNLOAD NOW", bg=ACCENT, state="normal")
        self._downloading = False
        messagebox.showerror(
            "Download Error",
            f"Something went wrong:\n\n{msg[:200]}\n\n"
            "Common fixes:\n"
            "1. Make sure FFmpeg is installed & in PATH\n"
            "2. Update yt-dlp:  pip install -U yt-dlp\n"
            "3. Try a different quality setting\n"
            "4. Check your internet connection"
        )
        self.status_lbl.config(fg=SUB)


# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = YTDownloaderApp()
    app.mainloop()