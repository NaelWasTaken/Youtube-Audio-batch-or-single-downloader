import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

class YTDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Audio Downloader")
        self.root.geometry("680x720")
        self.root.minsize(600, 650)
        
        # Modern Dark Theme Palette
        self.bg_color = "#1e1e2e"
        self.card_bg = "#2b2b3b"
        self.fg_color = "#cdd6f4"
        self.accent_color = "#89b4fa"
        self.btn_bg = "#45475a"
        self.btn_active = "#585b70"
        self.text_area_bg = "#11111b"
        self.error_color = "#f38ba8"
        self.success_color = "#a6e3a1"
        
        self.root.configure(bg=self.bg_color)
        
        self.download_process = None
        self.is_downloading = False
        
        self.setup_ui()
        
    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('default')
        
        # Header Section
        header_frame = tk.Frame(self.root, bg=self.bg_color)
        header_frame.pack(fill="x", padx=20, pady=(15, 5))
        
        title_lbl = tk.Label(header_frame, text="YouTube Audio Downloader", 
                             font=("Helvetica", 16, "bold"), fg=self.accent_color, bg=self.bg_color)
        title_lbl.pack(anchor="w")
        
        subtitle_lbl = tk.Label(header_frame, text="Download high quality audio, playlists, and chapters with embedded cover art.", 
                                font=("Helvetica", 9), fg="#a6adc8", bg=self.bg_color)
        subtitle_lbl.pack(anchor="w")
        
        # Target URL Section
        url_frame = tk.LabelFrame(self.root, text=" Target Video / Playlist URL ", 
                                 fg=self.fg_color, bg=self.bg_color, font=("Helvetica", 10, "bold"),
                                 bd=1, relief="solid")
        url_frame.pack(fill="x", padx=20, pady=10)
        
        self.url_entry = tk.Entry(url_frame, font=("Helvetica", 10), bg=self.card_bg, fg=self.fg_color, 
                                  insertbackground=self.fg_color, relief="flat")
        self.url_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        paste_btn = tk.Button(url_frame, text="Paste", command=self.paste_url,
                              bg=self.btn_bg, fg=self.fg_color, activebackground=self.btn_active,
                              activeforeground=self.fg_color, relief="flat", font=("Helvetica", 9))
        paste_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # Options Grid
        options_frame = tk.Frame(self.root, bg=self.bg_color)
        options_frame.pack(fill="x", padx=20, pady=5)
        
        # Left Column: Mode Selection
        mode_frame = tk.LabelFrame(options_frame, text=" Download Mode ", 
                                   fg=self.fg_color, bg=self.bg_color, font=("Helvetica", 10, "bold"),
                                   bd=1, relief="solid")
        mode_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.mode_var = tk.StringVar(value="single")
        
        rb1 = tk.Radiobutton(mode_frame, text="Single Track", value="single", variable=self.mode_var,
                             bg=self.bg_color, fg=self.fg_color, activebackground=self.bg_color,
                             activeforeground=self.accent_color, selectcolor=self.card_bg,
                             command=self.toggle_mode_options)
        rb1.pack(anchor="w", padx=10, pady=(8, 2))
        
        rb2 = tk.Radiobutton(mode_frame, text="Playlist / Mix", value="playlist", variable=self.mode_var,
                             bg=self.bg_color, fg=self.fg_color, activebackground=self.bg_color,
                             activeforeground=self.accent_color, selectcolor=self.card_bg,
                             command=self.toggle_mode_options)
        rb2.pack(anchor="w", padx=10, pady=2)
        
        limit_frame = tk.Frame(mode_frame, bg=self.bg_color)
        limit_frame.pack(anchor="w", padx=(30, 10), pady=(0, 5))
        tk.Label(limit_frame, text="Limit items (0=All):", fg="#a6adc8", bg=self.bg_color, font=("Helvetica", 8)).pack(side="left")
        self.limit_entry = tk.Entry(limit_frame, width=5, bg=self.card_bg, fg=self.fg_color, insertbackground=self.fg_color, relief="flat")
        self.limit_entry.insert(0, "0")
        self.limit_entry.pack(side="left", padx=5)
        
        rb3 = tk.Radiobutton(mode_frame, text="Split Chapters", value="chapters", variable=self.mode_var,
                             bg=self.bg_color, fg=self.fg_color, activebackground=self.bg_color,
                             activeforeground=self.accent_color, selectcolor=self.card_bg,
                             command=self.toggle_mode_options)
        rb3.pack(anchor="w", padx=10, pady=(2, 2))
        
        # Checkbox for Auto Subfolder Creation
        self.auto_folder_var = tk.BooleanVar(value=True)
        cb_folder = tk.Checkbutton(mode_frame, text="Create subfolder for playlist/mix", variable=self.auto_folder_var,
                                   bg=self.bg_color, fg=self.fg_color, activebackground=self.bg_color,
                                   activeforeground=self.accent_color, selectcolor=self.card_bg, font=("Helvetica", 8))
        cb_folder.pack(anchor="w", padx=10, pady=(2, 8))
        
        # Right Column: Format & Quality Settings
        audio_frame = tk.LabelFrame(options_frame, text=" Audio & Metadata ", 
                                    fg=self.fg_color, bg=self.bg_color, font=("Helvetica", 10, "bold"),
                                    bd=1, relief="solid")
        audio_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        fmt_frame = tk.Frame(audio_frame, bg=self.bg_color)
        fmt_frame.pack(fill="x", padx=10, pady=(8, 2))
        tk.Label(fmt_frame, text="Format:", fg=self.fg_color, bg=self.bg_color).pack(side="left")
        self.format_var = tk.StringVar(value="mp3")
        fmt_combo = ttk.Combobox(fmt_frame, textvariable=self.format_var, values=["mp3", "m4a", "flac", "wav", "aac", "opus"], width=8, state="readonly")
        fmt_combo.pack(side="right")
        
        q_frame = tk.Frame(audio_frame, bg=self.bg_color)
        q_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(q_frame, text="Quality:", fg=self.fg_color, bg=self.bg_color).pack(side="left")
        self.quality_var = tk.StringVar(value="0 (Best VBR)")
        q_combo = ttk.Combobox(q_frame, textvariable=self.quality_var, values=["0 (Best VBR)", "320k CBR", "256k CBR", "128k CBR"], width=12, state="readonly")
        q_combo.pack(side="right")
        
        self.embed_thumb_var = tk.BooleanVar(value=True)
        cb_thumb = tk.Checkbutton(audio_frame, text="Embed Cover Art", variable=self.embed_thumb_var,
                                  bg=self.bg_color, fg=self.fg_color, activebackground=self.bg_color,
                                  activeforeground=self.accent_color, selectcolor=self.card_bg, font=("Helvetica", 8))
        cb_thumb.pack(anchor="w", padx=10, pady=(5, 2))
        
        self.embed_meta_var = tk.BooleanVar(value=True)
        cb_meta = tk.Checkbutton(audio_frame, text="Embed Metadata (Tags)", variable=self.embed_meta_var,
                                 bg=self.bg_color, fg=self.fg_color, activebackground=self.bg_color,
                                 activeforeground=self.accent_color, selectcolor=self.card_bg, font=("Helvetica", 8))
        cb_meta.pack(anchor="w", padx=10, pady=(0, 8))
        
        # Save Destination
        dir_frame = tk.LabelFrame(self.root, text=" Save Destination ", 
                                 fg=self.fg_color, bg=self.bg_color, font=("Helvetica", 10, "bold"),
                                 bd=1, relief="solid")
        dir_frame.pack(fill="x", padx=20, pady=5)
        
        default_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.dir_entry = tk.Entry(dir_frame, font=("Helvetica", 9), bg=self.card_bg, fg=self.fg_color, insertbackground=self.fg_color, relief="flat")
        self.dir_entry.insert(0, default_dir)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        
        browse_btn = tk.Button(dir_frame, text="Browse...", command=self.browse_dir,
                               bg=self.btn_bg, fg=self.fg_color, activebackground=self.btn_active,
                               activeforeground=self.fg_color, relief="flat", font=("Helvetica", 9))
        browse_btn.pack(side="right", padx=(0, 10), pady=8)
        
        # Control Buttons
        action_frame = tk.Frame(self.root, bg=self.bg_color)
        action_frame.pack(fill="x", padx=20, pady=10)
        
        self.download_btn = tk.Button(action_frame, text="Start Download", command=self.toggle_download,
                                      bg="#a6e3a1", fg="#11111b", activebackground="#94e2d5",
                                      font=("Helvetica", 11, "bold"), relief="flat", height=2)
        self.download_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        open_dir_btn = tk.Button(action_frame, text="Open Folder", command=self.open_output_dir,
                                 bg=self.btn_bg, fg=self.fg_color, activebackground=self.btn_active,
                                 font=("Helvetica", 10, "bold"), relief="flat", height=2)
        open_dir_btn.pack(side="right", padx=(5, 0))
        
        # Console Output Log
        log_frame = tk.LabelFrame(self.root, text=" Download Console Log ", 
                                  fg=self.fg_color, bg=self.bg_color, font=("Helvetica", 10, "bold"),
                                  bd=1, relief="solid")
        log_frame.pack(fill="both", expand=True, padx=20, pady=(5, 15))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, bg=self.text_area_bg, fg="#a6adc8", 
                                                 font=("Consolas", 9), relief="flat", insertbackground=self.fg_color)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.toggle_mode_options()
        
    def paste_url(self):
        try:
            text = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, text.strip())
        except Exception:
            pass
            
    def browse_dir(self):
        selected = filedialog.askdirectory(initialdir=self.dir_entry.get())
        if selected:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, selected)
            
    def open_output_dir(self):
        path = self.dir_entry.get().strip()
        if os.path.exists(path):
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        else:
            messagebox.showerror("Error", "Directory does not exist.")
            
    def toggle_mode_options(self):
        if self.mode_var.get() == "playlist":
            self.limit_entry.config(state="normal")
        else:
            self.limit_entry.config(state="disabled")
            
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        
    def toggle_download(self):
        if self.is_downloading:
            self.cancel_download()
        else:
            self.start_download()
            
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a valid YouTube URL.")
            return
            
        output_dir = self.dir_entry.get().strip()
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create output directory:\n{e}")
                return

        self.is_downloading = True
        self.download_btn.config(text="Cancel / Stop Download", bg="#f38ba8", fg="#11111b")
        self.log_text.delete("1.0", tk.END)
        self.log("[INFO] Starting download task...")
        
        threading.Thread(target=self.run_ytdlp, args=(url, output_dir), daemon=True).start()
        
    def cancel_download(self):
        if self.download_process and self.download_process.poll() is None:
            self.download_process.terminate()
            self.log("\n[CANCELLED] Download was stopped by user.")
        self.reset_download_button()
        
    def reset_download_button(self):
        self.is_downloading = False
        self.download_btn.config(text="Start Download", bg="#a6e3a1", fg="#11111b")
        
    def run_ytdlp(self, url, output_dir):
        cmd = [sys.executable, "-m", "yt_dlp", "-x"]
        
        # Audio Format
        fmt = self.format_var.get()
        cmd.extend(["--audio-format", fmt])
        
        # Quality Settings
        q_val = self.quality_var.get()
        if "0" in q_val:
            cmd.extend(["--audio-quality", "0"])
        elif "320k" in q_val:
            cmd.extend(["--audio-quality", "320K"])
        elif "256k" in q_val:
            cmd.extend(["--audio-quality", "256K"])
        elif "128k" in q_val:
            cmd.extend(["--audio-quality", "128K"])
            
        # Metadata and Cover Art
        if self.embed_meta_var.get():
            cmd.append("--add-metadata")
        if self.embed_thumb_var.get():
            cmd.append("--embed-thumbnail")
            
        # Mode Selection
        mode = self.mode_var.get()
        use_subfolder = self.auto_folder_var.get()
        
        if mode == "playlist":
            cmd.append("--yes-playlist")
            try:
                limit = int(self.limit_entry.get().strip())
                if limit > 0:
                    cmd.extend(["--max-downloads", str(limit)])
            except ValueError:
                pass
            
            if use_subfolder:
                output_template = os.path.join(output_dir, "%(playlist_title,playlist|Playlist)s", "%(title)s.%(ext)s")
            else:
                output_template = os.path.join(output_dir, "%(title)s.%(ext)s")

        elif mode == "chapters":
            cmd.extend(["--no-playlist", "--split-chapters"])
            if use_subfolder:
                output_template = os.path.join(output_dir, "%(title)s", "chapter:%(section_number)02d - %(section_title)s.%(ext)s")
            else:
                output_template = os.path.join(output_dir, "chapter:%(section_number)02d - %(section_title)s.%(ext)s")
        else:
            cmd.append("--no-playlist")
            output_template = os.path.join(output_dir, "%(title)s.%(ext)s")
            
        cmd.extend(["-o", output_template, url])
        
        self.log(f"[COMMAND] {' '.join(cmd)}\n")
        
        try:
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            
            self.download_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=creationflags
            )
            
            for line in iter(self.download_process.stdout.readline, ''):
                if line:
                    self.root.after(0, self.log, line.strip())
                    
            self.download_process.stdout.close()
            return_code = self.download_process.wait()
            
            if return_code == 0:
                self.root.after(0, self.log, "\n[SUCCESS] Download finished successfully!")
            else:
                if self.is_downloading:
                    self.root.after(0, self.log, f"\n[ERROR] Process finished with exit code {return_code}")
                    
        except Exception as e:
            self.root.after(0, self.log, f"\n[EXCEPTION] {str(e)}")
            
        finally:
            self.root.after(0, self.reset_download_button)

if __name__ == "__main__":
    root = tk.Tk()
    app = YTDownloaderApp(root)
    root.mainloop()