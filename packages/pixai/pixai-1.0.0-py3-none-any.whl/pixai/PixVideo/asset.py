import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser, simpledialog
import requests
from PIL import Image, ImageTk, ImageFilter
import io
import threading
from urllib.parse import quote
import random
import json
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageTk, ImageEnhance
import sys

def pixelate_image(img, pixel_size=20):
    """Fungsi dasar pixelate"""
    small = img.resize(
        (img.width // pixel_size, img.height // pixel_size),
        resample=Image.NEAREST
    )
    return small.resize(img.size, Image.NEAREST)

class VideoSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PixAi Video")
        # ukuran diperkecil
        self.root.geometry("320x390")
        self.root.configure(bg="#fafafa")
        self.root.resizable(False, False)

        try:
            self.root.iconbitmap(r"c:\Users\User\Downloads\gambar\gambar\logo.ico")
        except:
            try:
                icon_img = Image.open(r"c:\Users\User\Downloads\gambar\gambar\logo.ico")
                icon_photo = ImageTk.PhotoImage(icon_img)
                self.root.iconphoto(False, icon_photo)
            except:
                pass  # Skip if icon file is not found

        # API Key Pexels untuk video
        self.api_key = "LH59shPdj1xO0lolnHPsClH23qsnHE4NjkCFBhKEXvR0CbqwkrXbqBnw"
        self.base_url = "https://api.pexels.com/videos/"

        # Variabel pencarian
        self.current_page = 1
        self.current_query = ""
        self.is_loading = False

        # Variabel tema
        self.is_dark = False
        self.custom_theme = None
        
        # Data untuk JSON
        self.search_history = []
        self.load_search_history()

        self.setup_ui()
        self.load_default_videos()

    def setup_ui(self):
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 9), padding=4)
        self.style.configure("TLabel", font=("Arial", 10))
        self.style.configure("TFrame", background="#fafafa")

        # Frame utama dengan gradasi
        self.main_frame = tk.Canvas(self.root, bg="#fafafa", highlightthickness=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame untuk konten di atas gradasi
        self.content_frame = ttk.Frame(self.main_frame, padding=6)
        self.content_frame_window = self.main_frame.create_window(
            0, 0, window=self.content_frame, anchor="nw", width=340
        )

        self.title_label = ttk.Label(
            self.content_frame,
            text="🔍 Video Search",
            font=("Arial", 12, "bold")
        )
        self.title_label.pack(pady=(0, 8))

        # Frame search
        self.search_frame = ttk.Frame(self.content_frame)
        self.search_frame.pack(fill=tk.X, pady=(0, 8))

        self.search_var = tk.StringVar()

        # Entry pakai grid
        self.search_entry = ttk.Entry(
            self.search_frame,
            textvariable=self.search_var,
            font=("Arial", 10)
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.search_entry.bind("<Return>", self.on_search)

        # Tombol pakai grid
        self.search_btn = ttk.Button(
            self.search_frame,
            text="Cari",
            command=self.on_search
        )
        self.search_btn.grid(row=0, column=1, sticky="ew")

        # Supaya kolom Entry fleksibel melebar
        self.search_frame.columnconfigure(0, weight=1)
        self.search_frame.columnconfigure(1, weight=0)

        # Scrollable canvas
        self.container = ttk.Frame(self.content_frame)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.container, bg='white', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # bind scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Status bar
        self.status_var = tk.StringVar(value="Siap mencari...")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind resize event untuk mengupdate gradasi
        self.root.bind("<Configure>", self.on_resize)


    def on_resize(self, event):
        """Handle window resize untuk mengupdate gradasi"""

    def load_default_videos(self):
        """Menampilkan 10 video random default dari Pexels"""
        self.current_query = random.choice(["nature", "city", "technology", "animal", "art"])
        self.current_page = 1
        self.search_videos(limit=10)

    def on_search(self, event=None):
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Peringatan", "Masukkan kata kunci pencarian")
            return

        self.current_query = query
        self.current_page = 1

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.status_var.set("Sedang mencari...")
        
        # Simpan ke riwayat pencarian
        self.add_to_search_history(query)
        self.search_videos()

    def add_to_search_history(self, query):
        """Menambahkan pencarian ke riwayat"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.search_history.append({
            "query": query,
            "timestamp": timestamp
        })
        
        # Batasi riwayat hingga 50 item terakhir
        if len(self.search_history) > 50:
            self.search_history = self.search_history[-50:]

    def load_search_history(self):
        """Memuat riwayat pencarian dari file default"""
        try:
            if os.path.exists("search_history.json"):
                with open("search_history.json", 'r') as f:
                    self.search_history = json.load(f)
        except:
            self.search_history = []

    def save_search_history(self):
        """Menyimpan riwayat pencarian ke file default"""
        try:
            with open("search_history.json", 'w') as f:
                json.dump(self.search_history, f, indent=4)
        except:
            pass

    def search_videos(self, limit=12):
        if self.is_loading:
            return

        self.is_loading = True
        query = quote(self.current_query)
        url = f"{self.base_url}search?query={query}&page={self.current_page}&per_page={limit}"
        headers = {"Authorization": self.api_key}

        thread = threading.Thread(target=self.fetch_videos, args=(url, headers))
        thread.daemon = True
        thread.start()

    def fetch_videos(self, url, headers):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.root.after(0, self.display_videos, data)
            else:
                self.root.after(0, self.handle_error, f"Error: {response.status_code}")
        except Exception as e:
            self.root.after(0, self.handle_error, str(e))

    def display_videos(self, data):
        self.is_loading = False

        if not data or 'videos' not in data or not data['videos']:
            if self.current_page == 1:
                self.status_var.set("Tidak ada hasil ditemukan")
            return

        row, col = 0, 0
        max_cols = 2

        for video in data['videos']:
            video_frame = ttk.Frame(self.scrollable_frame, relief=tk.RIDGE, borderwidth=1, padding=3)
            video_frame.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

            thread = threading.Thread(target=self.load_video, args=(video, video_frame))
            thread.daemon = True
            thread.start()

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        for i in range(max_cols):
            self.scrollable_frame.columnconfigure(i, weight=1)

        self.status_var.set(f"Hasil: {self.current_query} - Hal {self.current_page}")
        self.current_page += 1

    def load_video(self, video, parent_frame):
        try:
            # Ambil thumbnail video
            image_url = video['image']
            response = requests.get(image_url)
            img_data = response.content

            image = Image.open(io.BytesIO(img_data))
            image.thumbnail((130, 100), Image.Resampling.LANCZOS)
            video_img = ImageTk.PhotoImage(image)

            self.root.after(0, self.display_video, parent_frame, video_img, video, video['user']['name'])
        except Exception as e:
            print(f"Error loading video thumbnail: {e}")

    def display_video(self, parent_frame, image, video, videographer):
        img_label = ttk.Label(parent_frame, image=image)
        img_label.image = image
        img_label.pack(padx=2, pady=2)
        
        # Label videographer
        videographer_label = ttk.Label(parent_frame, text=f"By: {videographer}", font=("Arial", 7))
        videographer_label.pack()

        # Durasi video
        duration_label = ttk.Label(parent_frame, text=f"Duration: {video['duration']}s", font=("Arial", 7))
        duration_label.pack()

        # Frame untuk tombol
        btn_frame = ttk.Frame(parent_frame)
        btn_frame.pack(pady=(0, 2))
        
        preview_btn = ttk.Button(btn_frame, text="👁️", width=2,
                                command=lambda: self.preview_video(video))
        preview_btn.pack(side=tk.LEFT, padx=2)

        download_btn = ttk.Button(btn_frame, text="📥", width=2,
                                command=lambda: self.download_video(video))
        download_btn.pack(side=tk.LEFT, padx=2)

    def preview_video(self, video):
        try:
            # Buat window preview
            preview_win = tk.Toplevel(self.root)
            preview_win.title("Video Preview")
            preview_win.geometry("640x490")

            try:
                preview_win.iconbitmap(r"c:\Users\User\Downloads\gambar\gambar\logo.ico")
            except:
                try:
                    icon_img = tk.PhotoImage(file=r"c:\Users\User\Downloads\gambar\gambar\logo.ico")
                    preview_win.iconphoto(False, icon_img)
                except:
                    pass

            # Tampilkan informasi video
            info_frame = ttk.Frame(preview_win)
            info_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(info_frame, text=f"Videographer: {video['user']['name']}").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Duration: {video['duration']} seconds").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Resolution: {video['width']}x{video['height']}").pack(anchor=tk.W)
            
            # Tampilkan thumbnail sebagai preview (karena kita tidak bisa memutar video langsung di tkinter)
            try:
                response = requests.get(video['image'])
                img_data = response.content
                img = Image.open(io.BytesIO(img_data))
                img.thumbnail((600, 400), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                label = tk.Label(preview_win, image=photo, bg="black")
                label.image = photo
                label.pack(pady=10)
                
                # Tampilkan pesan bahwa video perlu didownload untuk ditonton
                ttk.Label(preview_win, text="Download video untuk menontonnya", 
                         font=("Arial", 10, "italic")).pack(pady=5)
                
            except Exception as e:
                ttk.Label(preview_win, text="Gagal memuat thumbnail video").pack(pady=10)
                print(f"Error loading thumbnail: {e}")
            
            # Tombol untuk membuka di browser
            def open_in_browser():
                import webbrowser
                webbrowser.open(video['url'])
            
            btn_frame = ttk.Frame(preview_win)
            btn_frame.pack(pady=10)
            
            ttk.Button(btn_frame, text="Buka di Browser", command=open_in_browser).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Download", command=lambda: self.download_video(video)).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Tutup", command=preview_win.destroy).pack(side=tk.LEFT, padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat preview video: {e}")

    def download_video(self, video):
        try:
            # Dapatkan link video dengan kualitas tertinggi
            video_files = video['video_files']
            best_quality = max(video_files, key=lambda x: x.get('width', 0) * x.get('height', 0))
            video_url = best_quality['link']
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".mp4",
                filetypes=[("MP4 Video", "*.mp4")],
                title="Simpan Video"
            )
            
            if file_path:
                self.status_var.set("Mendownload video...")
                
                # Download dalam thread terpisah
                thread = threading.Thread(target=self.download_video_thread, args=(video_url, file_path))
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mempersiapkan download: {e}")

    def download_video_thread(self, url, file_path):
        try:
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(file_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self.root.after(0, self.update_download_progress, progress)
            
            self.root.after(0, self.download_complete, file_path)
            
        except Exception as e:
            self.root.after(0, self.handle_error, f"Gagal download video: {e}")

    def update_download_progress(self, progress):
        self.status_var.set(f"Download: {progress:.1f}%")

    def download_complete(self, file_path):
        self.status_var.set("Download selesai")
        messagebox.showinfo("Berhasil", f"Video disimpan ke:\n{file_path}")

    def handle_error(self, error_msg):
        self.is_loading = False
        self.status_var.set(f"Error: {error_msg}")
        messagebox.showerror("Error", error_msg)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        # cek jika posisi scroll dekat bawah untuk infinity scroll
        if self.canvas.bbox("all") and self.canvas.canvasy(self.canvas.winfo_height()) >= self.canvas.bbox("all")[3] - 200:
            self.search_videos()
        
def run_gui():
    root = tk.Tk()
    
    # Set Windows style if available
    if sys.platform == "win32":
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)

    app = VideoSearchApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()