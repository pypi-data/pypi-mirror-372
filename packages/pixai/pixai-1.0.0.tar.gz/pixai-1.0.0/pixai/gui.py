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

class MediaSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gen PixAi")
        # ukuran diperkecil
        self.root.geometry("320x390")
        self.root.configure(bg="#fafafa")
        self.root.resizable(False, False)

        try:
            self.root.iconbitmap(r"c:\Users\User\Downloads\pixai\pixai\logo.ico")
        except:
            try:
                icon_img = Image.open(r"c:\Users\User\Downloads\pixai\pixai\logo.ico")
                icon_photo = ImageTk.PhotoImage(icon_img)
                self.root.iconphoto(False, icon_photo)
            except:
                pass  # Skip if icon file is not found

        # API Key Pexels
        self.api_key = "LH59shPdj1xO0lolnHPsClH23qsnHE4NjkCFBhKEXvR0CbqwkrXbqBnw"
        self.base_url = "https://api.pexels.com/v1/"

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
        self.load_default_images()

    def setup_ui(self):
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 9), padding=4)
        self.style.configure("TLabel", font=("Arial", 10))
        self.style.configure("TFrame", background="#fafafa")

        # menu bar
        self.menubar = tk.Menu(self.root, bg="#fafafa", fg="black")
        
        # Menu Tema
        tema_menu = tk.Menu(self.menubar, tearoff=0, bg="#fafafa", fg="black")
        tema_menu.add_command(label="Light Mode", command=self.set_light_theme)
        tema_menu.add_command(label="Dark Mode", command=self.set_dark_theme)
        
        # Menu Tema Kustom
        custom_menu = tk.Menu(tema_menu, tearoff=0, bg="#fafafa", fg="black")
        custom_menu.add_command(label="Pilih Warna Sendiri", command=self.choose_custom_colors)
        tema_menu.add_cascade(label="Custom Themes", menu=custom_menu)
        
        # Menu JSON
        json_menu = tk.Menu(self.menubar, tearoff=0, bg="#fafafa", fg="black")
        json_menu.add_command(label="Save Search History", command=self.save_search_history_json)
        json_menu.add_command(label="Load Search History", command=self.load_search_history_json)
        
        self.menubar.add_cascade(label="Theme", menu=tema_menu)
        self.menubar.add_cascade(label="JSON", menu=json_menu)
        
        # Menu Pixel Art
        pixel_menu = tk.Menu(self.menubar, tearoff=0, bg="#fafafa", fg="black")
        pixel_menu.add_command(label="Open Pixel Editor", command=self.open_pixel_editor)
        self.menubar.add_cascade(label="Pixel Art", menu=pixel_menu)
        
        # Menu Pixel Art
        pixel_menu2 = tk.Menu(self.menubar, tearoff=0, bg="#fafafa", fg="black")
        pixel_menu2.add_command(label="Open Gen PixAi Video Programs", command=self.open_exe)
        self.menubar.add_cascade(label="PixAi VD", menu=pixel_menu2)

        
                # Menu Informasi Pixel Art
        pixel_menu = tk.Menu(self.menubar, tearoff=0, bg="#fafafa", fg="black")

        # Informasi Pengembang
        pixel_menu.add_command(
            label="Developer Apps",
            command=lambda: messagebox.showinfo(
                "Information Developer",
                "Pixel Art Module dikembangkan oleh:\n\n"
                "Nama Pengembang : Dwi Bakti N Dev\n"
                "Website         : https://profiledwibaktindev.netlify.app/\n"
                "Email           : dwibakti76@gmail.com\n\n"
                "Pengembang berfokus pada solusi kreatif di bidang teknologi, "
                "desain digital, dan aplikasi edukasi."
            )
        )

        # Lisensi Penggunaan
        pixel_menu.add_command(
            label="Lisensi",
            command=lambda: messagebox.showinfo(
                "Lisensi Penggunaan Pixel Art",
                "Lisensi Penggunaan:\n\n"
                "© 2025 Dwi Bakti N Dev. All rights reserved.\n\n"
                "1. Pixel Art ini hanya diperbolehkan untuk penggunaan pribadi, "
                "edukasi, atau penelitian non-komersial.\n"
                "2. Tidak diperbolehkan memperjualbelikan, mendistribusikan ulang, "
                "atau memodifikasi tanpa izin tertulis dari pengembang.\n"
                "3. Penggunaan komersial wajib memperoleh lisensi resmi dari pengembang.\n"
                "4. Pelanggaran terhadap lisensi ini dapat berakibat pada pencabutan hak penggunaan.\n\n"
                "Lisensi mengikuti standar Creative Commons BY-NC-ND 4.0."
            )
        )

        # Tata Cara Penggunaan
        pixel_menu.add_command(
            label="Tata Cara Penggunaan",
            command=lambda: messagebox.showinfo(
                "Tata Cara Penggunaan Pixel Art",
                "Panduan Penggunaan Pixel Art:\n\n"
                "1. Pilih menu Pixel Art di aplikasi.\n"
                "2. Gunakan alat pensil untuk menggambar pixel sesuai grid.\n"
                "3. Simpan hasil karya menggunakan menu 'Save'.\n"
                "4. Untuk membuka kembali karya, gunakan menu 'Open'.\n"
                "5. Hasil karya boleh digunakan untuk:\n"
                "   - Latihan pribadi\n"
                "   - Proyek sekolah/kampus\n"
                "   - Kegiatan edukasi\n\n"
                "Dilarang:\n"
                "❌ Menghapus watermark atau informasi pengembang\n"
                "❌ Menggunakan karya untuk tujuan komersial tanpa izin\n"
                "❌ Mengklaim karya sebagai milik sendiri"
            )
        )

        self.menubar.add_cascade(label="Dev", menu=pixel_menu)
        
        self.root.config(menu=self.menubar)

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
            text="🔍 PixAi Search",
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
        
        


    def open_exe(self):
        exe_path = r"C:\Users\User\Downloads\pixai\pixai\asset\asset.exe"
        try:
            # Cara 1: langsung buka (Windows)
            os.startfile(exe_path)

            # Cara 2 (alternatif jika mau pakai subprocess):
            # subprocess.Popen([exe_path], shell=True)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka file:\n{e}")
            
            

    def draw_gradient(self, theme=None):
        """Menggambar latar belakang gradasi berdasarkan tema"""
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # Hapus gradasi sebelumnya
        self.main_frame.delete("gradient")
        
        if theme == "ocean":
            colors = ["#00416A", "#0077B6", "#00B4D8", "#90E0EF"]
        elif theme == "sunset":
            colors = ["#FF6B6B", "#FF9E6B", "#FFCA6B", "#FFE66D"]
        elif theme == "forest":
            colors = ["#2E5A2E", "#3D7B3D", "#5AA469", "#87C79D"]
        elif theme == "lavender":
            colors = ["#6B5B95", "#8B7BAA", "#AA9BC5", "#D2C9E3"]
        elif self.is_dark:
            colors = ["#1A1A2E", "#16213E", "#0F3460", "#0D1B2A"]
        else:
            colors = ["#F8F9FA", "#E9ECEF", "#DEE2E6", "#CED4DA"]
        
        # Buat gambar gradasi
        gradient = Image.new('RGB', (width, height), colors[0])
        draw = Image.new('RGB', (width, height), colors[0])
        
        for i in range(height):
            r = int((i / height) * 255)
            color_index = min(int(i / (height / (len(colors) - 1))), len(colors) - 2)
            
            # Interpolasi antara warna
            ratio = (i - color_index * (height / (len(colors) - 1))) / (height / (len(colors) - 1))
            r1, g1, b1 = int(colors[color_index][1:3], 16), int(colors[color_index][3:5], 16), int(colors[color_index][5:7], 16)
            r2, g2, b2 = int(colors[color_index+1][1:3], 16), int(colors[color_index+1][3:5], 16), int(colors[color_index+1][5:7], 16)
            
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.main_frame.create_line(0, i, width, i, fill=color, tags="gradient")

    def on_resize(self, event):
        """Handle window resize untuk mengupdate gradasi"""
        self.draw_gradient(self.custom_theme)

    def load_default_images(self):
        """Menampilkan 10 gambar random default dari Pexels"""
        self.current_query = random.choice(["nature", "city", "technology", "animal", "art"])
        self.current_page = 1
        self.search_media(limit=10)

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
        self.search_media()

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

    def save_search_history_json(self):
        """Menyimpan riwayat pencarian ke file JSON"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                title="Simpan Riwayat Pencarian"
            )
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(self.search_history, f, indent=4)
                messagebox.showinfo("Berhasil", f"Riwayat pencarian disimpan ke:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan riwayat: {e}")

    def load_search_history_json(self):
        """Memuat riwayat pencarian dari file JSON"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")],
                title="Pilih File Riwayat Pencarian"
            )
            if file_path:
                with open(file_path, 'r') as f:
                    self.search_history = json.load(f)
                messagebox.showinfo("Berhasil", "Riwayat pencarian dimuat")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat riwayat: {e}")

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

    def search_media(self, limit=12):
        if self.is_loading:
            return

        self.is_loading = True
        query = quote(self.current_query)
        url = f"{self.base_url}search?query={query}&page={self.current_page}&per_page={limit}"
        headers = {"Authorization": self.api_key}

        thread = threading.Thread(target=self.fetch_media, args=(url, headers))
        thread.daemon = True
        thread.start()

    def fetch_media(self, url, headers):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.root.after(0, self.display_media, data)
            else:
                self.root.after(0, self.handle_error, f"Error: {response.status_code}")
        except Exception as e:
            self.root.after(0, self.handle_error, str(e))

    def display_media(self, data):
        self.is_loading = False

        if not data or 'photos' not in data or not data['photos']:
            if self.current_page == 1:
                self.status_var.set("Tidak ada hasil ditemukan")
            return

        row, col = 0, 0
        max_cols = 2

        for photo in data['photos']:
            photo_frame = ttk.Frame(self.scrollable_frame, relief=tk.RIDGE, borderwidth=1, padding=3)
            photo_frame.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

            thread = threading.Thread(target=self.load_photo, args=(photo, photo_frame))
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

    def load_photo(self, photo, parent_frame):
        try:
            image_url = photo['src']['medium']
            response = requests.get(image_url)
            img_data = response.content

            image = Image.open(io.BytesIO(img_data))
            image.thumbnail((130, 100), Image.Resampling.LANCZOS)
            photo_img = ImageTk.PhotoImage(image)

            self.root.after(0, self.display_photo, parent_frame, photo_img, photo['src']['original'], photo['photographer'])
        except Exception as e:
            print(f"Error loading image: {e}")

    def display_photo(self, parent_frame, image, original_url, photographer):
        img_label = ttk.Label(parent_frame, image=image)
        img_label.image = image
        img_label.pack(padx=2, pady=2)
        
        # Label fotografer
        photographer_label = ttk.Label(parent_frame, text=f"By: {photographer}", font=("Arial", 7))
        photographer_label.pack()

        # Frame untuk tombol
        btn_frame = ttk.Frame(parent_frame)
        btn_frame.pack(pady=(0, 2))
        
        preview_btn = ttk.Button(btn_frame, text="👁️", width=2,
                                command=lambda: self.preview_image(original_url))
        preview_btn.pack(side=tk.LEFT, padx=2)

        edit_btn = ttk.Button(btn_frame, text="🖊️", width=2,
                            command=lambda: self.edit_image(original_url))
        edit_btn.pack(side=tk.LEFT, padx=2)

        pixel_btn = ttk.Button(btn_frame, text="🖼️", width=2,
                            command=lambda: self.pixelate_from_url(original_url))
        pixel_btn.pack(side=tk.LEFT, padx=2)

        download_btn = ttk.Button(btn_frame, text="📥", width=2,
                                command=lambda: self.download_image(original_url))
        download_btn.pack(side=tk.LEFT, padx=2)



    def preview_image(self, url):
        try:
            response = requests.get(url)
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))

            # Buat window preview
            preview_win = tk.Toplevel(self.root)
            preview_win.title("Image Preview")

            # Tambahkan icon (ganti dengan file icon kamu)
            try:
                preview_win.iconbitmap(r"c:\Users\User\Downloads\pixai\pixai\logo.ico")  # Windows (ICO)
            except:
                try:
                    icon_img = tk.PhotoImage(file=r"c:\Users\User\Downloads\pixai\pixai\logo.ico")  # PNG alternatif
                    preview_win.iconphoto(False, icon_img)
                except:
                    pass  # Kalau gagal, skip

            # Resize image jika terlalu besar
            max_size = (800, 600)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            # Label untuk menampilkan gambar
            label = tk.Label(preview_win, image=photo, bg="black")
            label.image = photo
            label.pack(expand=True, fill="both")

            # === FITUR TAMBAHAN ===
            def zoom(factor):
                new_size = (int(img.width * factor), int(img.height * factor))
                zoomed = img.resize(new_size, Image.Resampling.LANCZOS)
                photo_zoom = ImageTk.PhotoImage(zoomed)
                label.config(image=photo_zoom)
                label.image = photo_zoom

            def save_image():
                file = filedialog.asksaveasfilename(defaultextension=".png",
                                                    filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
                if file:
                    img.save(file)
                    messagebox.showinfo("Saved", f"Gambar berhasil disimpan di:\n{file}")

            def fullscreen_toggle():
                state = not bool(preview_win.attributes("-fullscreen"))
                preview_win.attributes("-fullscreen", state)

            # Tombol kontrol
            btn_frame = tk.Frame(preview_win)
            btn_frame.pack(pady=5)

            tk.Button(btn_frame, text="🔍 Zoom In", command=lambda: zoom(1.2)).pack(side="left", padx=5)
            tk.Button(btn_frame, text="🔎 Zoom Out", command=lambda: zoom(0.8)).pack(side="left", padx=5)
            tk.Button(btn_frame, text="💾 Save", command=save_image).pack(side="left", padx=5)
            tk.Button(btn_frame, text="⛶ Fullscreen", command=fullscreen_toggle).pack(side="left", padx=5)
            tk.Button(btn_frame, text="❌ Close", command=preview_win.destroy).pack(side="left", padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat gambar: {e}")

        except Exception as e:
            messagebox.showerror("Error", f"Gagal preview gambar: {e}")

    def edit_image(self, url):
        try:
            response = requests.get(url)
            img_data = response.content
            self.edit_img = Image.open(io.BytesIO(img_data))
            self.edit_history = []  # For undo functionality
            self.push_to_history()  # Save initial state

            edit_win = tk.Toplevel(self.root)
            edit_win.title("Image Editor")
            edit_win.geometry("800x600")  # Reduced default size
            edit_win.minsize(600, 400)  # Set smaller minimum window size
            
            
            # === Tambahkan Icon ke Window Editor ===
            try:
                edit_win.iconbitmap(r"c:\Users\User\Downloads\pixai\pixai\logo.ico")  # Windows (ICO)
            except:
                try:
                    icon_img = tk.PhotoImage(file=r"c:\Users\User\Downloads\pixai\pixai\logo.ico")  # PNG fallback
                    edit_win.iconphoto(False, icon_img)
                except:
                    pass  # Kalau gagal, lewati tanpa error
            
            # Make the window responsive
            edit_win.grid_columnconfigure(0, weight=1)
            edit_win.grid_rowconfigure(0, weight=1)
            
            # Main container with grid layout
            main_container = ttk.Frame(edit_win)
            main_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            main_container.grid_columnconfigure(0, weight=1)
            main_container.grid_rowconfigure(1, weight=1)
            
            # Toolbar frame at the top
            toolbar = ttk.Frame(main_container)
            toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
            
            # Canvas for preview with scrollbars
            preview_frame = ttk.Frame(main_container)
            preview_frame.grid(row=1, column=0, sticky="nsew")
            preview_frame.grid_columnconfigure(0, weight=1)
            preview_frame.grid_rowconfigure(0, weight=1)
            
            # Add scrollbars
            v_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL)
            h_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL)
            
            self.edit_preview = tk.Canvas(
                preview_frame, 
                yscrollcommand=v_scrollbar.set,
                xscrollcommand=h_scrollbar.set
            )
            
            v_scrollbar.config(command=self.edit_preview.yview)
            h_scrollbar.config(command=self.edit_preview.xview)
            
            # Grid layout for canvas and scrollbars
            self.edit_preview.grid(row=0, column=0, sticky="nsew")
            v_scrollbar.grid(row=0, column=1, sticky="ns")
            h_scrollbar.grid(row=1, column=0, sticky="ew")
            
            # Control panel at the bottom
            control_frame = ttk.Frame(main_container)
            control_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
            control_frame.grid_columnconfigure(0, weight=1)
            
            # Create a notebook for different adjustment categories
            notebook = ttk.Notebook(control_frame)
            notebook.grid(row=0, column=0, sticky="ew", pady=5)
            
            # Basic adjustments tab
            basic_frame = ttk.Frame(notebook)
            notebook.add(basic_frame, text="Basic")
            basic_frame.grid_columnconfigure(1, weight=1)
            
            # Transform controls
            ttk.Label(basic_frame, text="Transform:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
            transform_frame = ttk.Frame(basic_frame)
            transform_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
            
            ttk.Button(transform_frame, text="Rotate 90°", 
                    command=lambda: self.apply_edit("rotate")).pack(side=tk.LEFT, padx=2)
            ttk.Button(transform_frame, text="Flip H", 
                    command=lambda: self.apply_edit("flip_h")).pack(side=tk.LEFT, padx=2)
            ttk.Button(transform_frame, text="Flip V", 
                    command=lambda: self.apply_edit("flip_v")).pack(side=tk.LEFT, padx=2)
            
            # Filters
            ttk.Label(basic_frame, text="Filters:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
            filter_frame = ttk.Frame(basic_frame)
            filter_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
            
            ttk.Button(filter_frame, text="Blur", 
                    command=lambda: self.apply_edit("blur")).pack(side=tk.LEFT, padx=2)
            ttk.Button(filter_frame, text="Sharpen", 
                    command=lambda: self.apply_edit("sharpen")).pack(side=tk.LEFT, padx=2)
            ttk.Button(filter_frame, text="Grayscale", 
                    command=lambda: self.apply_edit("gray")).pack(side=tk.LEFT, padx=2)
            
            # Advanced adjustments tab
            advanced_frame = ttk.Frame(notebook)
            notebook.add(advanced_frame, text="Adjustments")
            advanced_frame.grid_columnconfigure(1, weight=1)
            
            # Brightness control
            ttk.Label(advanced_frame, text="Brightness:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
            self.brightness_var = tk.DoubleVar(value=0.0)
            brightness_scale = ttk.Scale(
                advanced_frame, 
                from_=-100.0, 
                to=100.0, 
                variable=self.brightness_var,
                orient=tk.HORIZONTAL
            )
            brightness_scale.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
            
            brightness_val_label = ttk.Label(advanced_frame, text="0.0")
            brightness_val_label.grid(row=0, column=2, padx=(2, 5), pady=2)
            
            # Contrast control
            ttk.Label(advanced_frame, text="Contrast:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
            self.contrast_var = tk.DoubleVar(value=0.0)
            contrast_scale = ttk.Scale(
                advanced_frame, 
                from_=-100.0, 
                to=100.0, 
                variable=self.contrast_var,
                orient=tk.HORIZONTAL
            )
            contrast_scale.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
            
            contrast_val_label = ttk.Label(advanced_frame, text="0.0")
            contrast_val_label.grid(row=1, column=2, padx=(2, 5), pady=2)
            
            # Apply adjustments button
            ttk.Button(advanced_frame, text="Apply Adjustments", 
                    command=self.apply_custom_adjustments).grid(row=2, column=0, columnspan=3, pady=5)
            
            # Action buttons
            action_frame = ttk.Frame(main_container)
            action_frame.grid(row=3, column=0, sticky="e", pady=5)
            
            ttk.Button(action_frame, text="Undo", command=self.undo_edit).pack(side=tk.LEFT, padx=2)
            ttk.Button(action_frame, text="Reset", command=self.reset_edits).pack(side=tk.LEFT, padx=2)
            ttk.Button(action_frame, text="Save", command=lambda: self.save_edited_image()).pack(side=tk.LEFT, padx=2)
            
            # Initialize preview
            self.update_edit_preview()
            
            # Update labels when scales change
            def update_brightness_label(*args):
                brightness_val_label.config(text=f"{self.brightness_var.get():.1f}")
                
            def update_contrast_label(*args):
                contrast_val_label.config(text=f"{self.contrast_var.get():.1f}")
                
            self.brightness_var.trace("w", update_brightness_label)
            self.contrast_var.trace("w", update_contrast_label)
            
            # Bind window resize event with debounce to prevent excessive updates
            self.resize_debounce = None
            def on_resize(event):
                if self.resize_debounce:
                    edit_win.after_cancel(self.resize_debounce)
                self.resize_debounce = edit_win.after(200, self.update_edit_preview)
                
            edit_win.bind("<Configure>", on_resize)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open editor: {e}")

    def apply_custom_adjustments(self):
        """Apply custom brightness and contrast adjustments"""
        self.push_to_history()
        
        # Convert image for enhancement if needed
        if self.edit_img.mode != 'RGB':
            img = self.edit_img.convert('RGB')
        else:
            img = self.edit_img
        
        # Apply brightness
        brightness_factor = 1.0 + (self.brightness_var.get() / 100.0)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness_factor)
        
        # Apply contrast
        contrast_factor = 1.0 + (self.contrast_var.get() / 100.0)
        enhancer = ImageEnhance.Contrast(img)
        self.edit_img = enhancer.enhance(contrast_factor)
        
        self.update_edit_preview()

    def push_to_history(self):
        """Save current image state to history for undo functionality"""
        if hasattr(self, 'edit_img'):
            self.edit_history.append(self.edit_img.copy())

    def undo_edit(self):
        """Revert to previous image state"""
        if len(self.edit_history) > 1:  # Keep at least the original
            self.edit_history.pop()  # Remove current state
            self.edit_img = self.edit_history[-1].copy()  # Restore previous
            self.update_edit_preview()
        elif len(self.edit_history) == 1:
            self.edit_img = self.edit_history[0].copy()  # Restore original
            self.update_edit_preview()

    def reset_edits(self):
        """Reset image to original state"""
        if len(self.edit_history) > 0:
            self.edit_img = self.edit_history[0].copy()
            self.edit_history = [self.edit_history[0].copy()]  # Reset history
            # Reset adjustment controls
            if hasattr(self, 'brightness_var'):
                self.brightness_var.set(0.0)
            if hasattr(self, 'contrast_var'):
                self.contrast_var.set(0.0)
            self.update_edit_preview()

    def apply_edit(self, action):
        # Save current state to history before applying changes
        self.push_to_history()
        
        if action == "rotate":
            self.edit_img = self.edit_img.rotate(90, expand=True)
        elif action == "flip_h":
            self.edit_img = self.edit_img.transpose(Image.FLIP_LEFT_RIGHT)
        elif action == "flip_v":
            self.edit_img = self.edit_img.transpose(Image.FLIP_TOP_BOTTOM)
        elif action == "blur":
            self.edit_img = self.edit_img.filter(ImageFilter.GaussianBlur(radius=2))
        elif action == "sharpen":
            enhancer = ImageEnhance.Sharpness(self.edit_img)
            self.edit_img = enhancer.enhance(1.5)
        elif action == "gray":
            self.edit_img = self.edit_img.convert("L").convert("RGB")
        
        self.update_edit_preview()

    def update_edit_preview(self):
        """Update the preview canvas with the current image"""
        if not hasattr(self, 'edit_img') or not hasattr(self, 'edit_preview'):
            return
            
        # Get current canvas size
        canvas_width = self.edit_preview.winfo_width()
        canvas_height = self.edit_preview.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not yet rendered, schedule update for later
            self.edit_preview.after(100, self.update_edit_preview)
            return
        
        # Calculate aspect ratio preserving dimensions
        img_width, img_height = self.edit_img.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        
        # Resize image for preview
        preview_img = self.edit_img.copy()
        if ratio < 1:  # Only resize if needed
            preview_img = preview_img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.edit_photo = ImageTk.PhotoImage(preview_img)
        
        # Update canvas
        self.edit_preview.delete("all")
        self.edit_preview.create_image(
            canvas_width//2, 
            canvas_height//2, 
            image=self.edit_photo, 
            anchor=tk.CENTER
        )
        
        # Update scroll region
        self.edit_preview.config(scrollregion=self.edit_preview.bbox(tk.ALL))

    def save_edited_image(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[
                ("JPEG Image", "*.jpg"), 
                ("PNG Image", "*.png"),
                ("BMP Image", "*.bmp"),
                ("TIFF Image", "*.tiff")
            ],
            title="Save Edited Image"
        )
        if file_path:
            # Save with quality options for JPEG
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                self.edit_img.save(file_path, "JPEG", quality=95)
            else:
                self.edit_img.save(file_path)
            messagebox.showinfo("Success", f"Image saved to:\n{file_path}")


    def pixelate_from_url(self, url, pixel_size=20):
        try:
            response = requests.get(url)
            img_data = response.content
            self.edit_img = Image.open(io.BytesIO(img_data))

            # Buat window baru
            self.pix_win = tk.Toplevel(self.root)
            self.pix_win.title("PixAI")
            self.pix_win.iconbitmap(r"c:\Users\User\Downloads\pixai\pixai\logo.ico")  # icon window (gunakan .ico)

            # Simpan ukuran asli
            self.original_img = self.edit_img.copy()

            # Default pixelation
            self.pixelated_img = pixelate_image(self.edit_img, pixel_size)

            # Label preview
            self.preview_lbl = tk.Label(self.pix_win)
            self.preview_lbl.pack(pady=10)

            self.update_preview()

            # Slider pixel size
            slider_frame = tk.Frame(self.pix_win)
            slider_frame.pack(pady=5)

            tk.Label(slider_frame, text="Pixel Size:").pack(side=tk.LEFT)
            self.pixel_slider = ttk.Scale(
                slider_frame,
                from_=2,
                to=100,
                orient="horizontal",
                command=self.update_from_slider
            )
            self.pixel_slider.set(pixel_size)
            self.pixel_slider.pack(side=tk.LEFT, padx=5)

            # Tombol Simpan & Reset
            btn_frame = tk.Frame(self.pix_win)
            btn_frame.pack(pady=10)

            save_btn = ttk.Button(
                btn_frame, text="💾 Simpan",
                command=lambda: self.save_pixelated(self.pixelated_img)
            )
            save_btn.pack(side=tk.LEFT, padx=5)

            reset_btn = ttk.Button(
                btn_frame, text="🔄 Reset",
                command=self.reset_preview
            )
            reset_btn.pack(side=tk.LEFT, padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat pixel art: {e}")

    def update_from_slider(self, val):
        """Update preview saat slider digeser"""
        pixel_size = max(2, int(float(val)))
        self.pixelated_img = pixelate_image(self.original_img, pixel_size)
        self.update_preview()

    def update_preview(self):
        """Update tampilan preview"""
        preview = self.pixelated_img.copy()
        preview.thumbnail((400, 400), Image.NEAREST)

        self.preview_photo = ImageTk.PhotoImage(preview)
        self.preview_lbl.config(image=self.preview_photo)

    def reset_preview(self):
        """Kembali ke default pixel size"""
        self.pixel_slider.set(20)
        self.pixelated_img = pixelate_image(self.original_img, 20)
        self.update_preview()

    def save_pixelated(self, img):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")],
            title="Simpan Pixel Art"
        )
        if file_path:
            img.save(file_path)
            messagebox.showinfo("Berhasil", f"Pixel art disimpan ke:\n{file_path}")



    def download_image(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".jpg",
                    filetypes=[("JPEG Image", "*.jpg"), ("PNG Image", "*.png")],
                    title="Simpan Gambar"
                )
                if file_path:
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    messagebox.showinfo("Berhasil", f"Gambar disimpan ke:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal download gambar: {e}")

    def handle_error(self, error_msg):
        self.is_loading = False
        self.status_var.set(f"Error: {error_msg}")
        messagebox.showerror("Error", error_msg)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        # cek jika posisi scroll dekat bawah untuk infinity scroll
        if self.canvas.bbox("all") and self.canvas.canvasy(self.canvas.winfo_height()) >= self.canvas.bbox("all")[3] - 200:
            self.search_media()

    def choose_custom_colors(self):
        # pilih warna background
        bg_color = colorchooser.askcolor(title="Pilih Warna Background")[1]
        if not bg_color:
            return
        # pilih warna teks
        fg_color = colorchooser.askcolor(title="Pilih Warna Teks")[1]
        if not fg_color:
            fg_color = "black"

        self.custom_theme = "custom"
        self.is_dark = False

        widget_bg = bg_color
        widget_fg = fg_color
        entry_bg = "white"

        # Terapkan ke semua widget
        self.style.configure(".", background=bg_color, foreground=fg_color)
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("TButton", background=widget_bg, foreground=widget_fg)
        self.style.configure("TEntry", fieldbackground=entry_bg, foreground=fg_color)
        self.style.configure("TScrollbar", background=widget_bg, troughcolor=bg_color)

        # Apply ke komponen
        self.content_frame.configure(style="TFrame")
        self.search_frame.configure(style="TFrame")
        self.container.configure(style="TFrame")
        self.scrollable_frame.configure(style="TFrame")

        self.title_label.configure(style="TLabel")
        self.status_bar.configure(style="TLabel")

        self.search_entry.configure(style="TEntry")
        self.search_btn.configure(style="TButton")

        self.canvas.configure(bg=widget_bg)
        self.scrollbar.configure(style="TScrollbar")

        self.menubar.configure(bg=bg_color, fg=fg_color)

        self.status_var.set("Tema: Custom Warna Sendiri")

    def set_dark_theme(self):
        self.is_dark = True
        self.custom_theme = None
        
        # Configure colors
        bg_color = "#1e1e1e"
        fg_color = "white"
        widget_bg = "#2b2b2b"
        widget_fg = "#FF0000"
        entry_bg = "#3c3c3c"
        
        # Apply to all widgets
        self.style.configure(".", background=bg_color, foreground=fg_color)
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("TButton", background=widget_bg, foreground=widget_fg)
        self.style.configure("TEntry", fieldbackground=entry_bg, foreground=fg_color)
        self.style.configure("TScrollbar", background=widget_bg, troughcolor=bg_color)
        
        # Apply to specific widgets
        self.content_frame.configure(style="TFrame")
        self.search_frame.configure(style="TFrame")
        self.container.configure(style="TFrame")
        self.scrollable_frame.configure(style="TFrame")
        
        self.title_label.configure(style="TLabel")
        self.status_bar.configure(style="TLabel")
        
        self.search_entry.configure(style="TEntry")
        self.search_btn.configure(style="TButton")
        
        self.canvas.configure(bg=widget_bg)
        self.scrollbar.configure(style="TScrollbar")
        
        # Configure menu
        self.menubar.configure(bg=widget_bg, fg=widget_fg)
        for menu_name in self.menubar.winfo_children():
            if isinstance(menu_name, tk.Menu):
                menu_name.configure(bg=widget_bg, fg=widget_fg)
                try:
                    menu_name.entryconfig(0, background=widget_bg, foreground=widget_fg)
                    menu_name.entryconfig(1, background=widget_bg, foreground=widget_fg)
                except:
                    pass
        
        # Draw gradient background
        self.draw_gradient()
        
        self.status_var.set("Tema: Dark Mode")

    def set_light_theme(self):
        self.is_dark = False
        self.custom_theme = None
        
        # Configure colors
        bg_color = "#fafafa"
        fg_color = "black"
        widget_bg = "SystemButtonFace"
        widget_fg = "black"
        entry_bg = "white"
        
        # Apply to all widgets
        self.style.configure(".", background=bg_color, foreground=fg_color)
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("TButton", background=widget_bg, foreground=widget_fg)
        self.style.configure("TEntry", fieldbackground=entry_bg, foreground=fg_color)
        self.style.configure("TScrollbar", background=widget_bg, troughcolor=bg_color)
        
        # Apply to specific widgets
        self.content_frame.configure(style="TFrame")
        self.search_frame.configure(style="TFrame")
        self.container.configure(style="TFrame")
        self.scrollable_frame.configure(style="TFrame")
        
        self.title_label.configure(style="TLabel")
        self.status_bar.configure(style="TLabel")
        
        self.search_entry.configure(style="TEntry")
        self.search_btn.configure(style="TButton")
        
        self.canvas.configure(bg="white")
        self.scrollbar.configure(style="TScrollbar")
        
        # Configure menu
        self.menubar.configure(bg=bg_color, fg=fg_color)
        for menu_name in self.menubar.winfo_children():
            if isinstance(menu_name, tk.Menu):
                menu_name.configure(bg=bg_color, fg=fg_color)
                try:
                    menu_name.entryconfig(0, background=bg_color, foreground=fg_color)
                    menu_name.entryconfig(1, background=bg_color, foreground=fg_color)
                except:
                    pass
        
        # Draw gradient background
        self.draw_gradient()
        
        self.status_var.set("Tema: Light Mode")

    def __del__(self):
        """Destructor untuk menyimpan riwayat pencarian saat aplikasi ditutup"""
        self.save_search_history()
        
    def pixelate_image(self, img, pixel_size=16):
        # Convert PhotoImage to PIL Image
        if hasattr(img, '_PhotoImage__photo'):
            # This is a PhotoImage object
            img_data = img._PhotoImage__photo
            # This conversion might not work perfectly, but we'll try
            try:
                pil_img = Image.open(io.BytesIO(img_data))
            except:
                # Fallback: create a blank image
                pil_img = Image.new('RGB', (100, 100), 'white')
        else:
            # Assume it's already a PIL Image
            pil_img = img
            
        # Resize to smaller dimensions
        small = pil_img.resize((pixel_size, pixel_size), resample=Image.NEAREST)
        # Resize back to original size
        result = small.resize(pil_img.size, Image.NEAREST)
        return result

    def open_pixel_editor(self, grid_size=16, cell_size=20):
        editor = tk.Toplevel(self.root)
        editor.title("Pixel Editor")
        editor.resizable(False, False)
        
        # Set icon for the editor window
        try:
            editor.iconbitmap(r"c:\Users\User\Downloads\pixai\pixai\logo.ico")  # Make sure to have this icon file
        except:
            pass  # Skip if icon file is not available
        
        # Frame untuk canvas dan scrollbar
        canvas_frame = ttk.Frame(editor)
        canvas_frame.pack(padx=10, pady=10)
        
        # Canvas dengan scrollbar
        canvas = tk.Canvas(canvas_frame, width=grid_size*cell_size, height=grid_size*cell_size, 
                        bg="white", highlightthickness=0)
        scroll_x = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        scroll_y = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        
        # Grid untuk layout
        canvas.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        # Frame untuk tools
        tool_frame = ttk.Frame(editor)
        tool_frame.pack(pady=5, fill=tk.X)
        
        # Frame untuk color palette
        color_frame = ttk.Frame(editor)
        color_frame.pack(pady=5, fill=tk.X)
        
        # Frame untuk tombol
        button_frame = ttk.Frame(editor)
        button_frame.pack(pady=5)
        
        # Dictionary untuk menyimpan pixels
        pixels = {}
        current_color = "black"
        is_drawing = False
        is_erasing = False
        current_tool = "pencil"  # Default tool
        
        # Draw grid
        def draw_grid():
            canvas.delete("grid")
            for i in range(grid_size + 1):
                # Garis vertikal
                canvas.create_line(i * cell_size, 0, i * cell_size, grid_size * cell_size, 
                                fill="gray", tags="grid")
                # Garis horizontal
                canvas.create_line(0, i * cell_size, grid_size * cell_size, i * cell_size, 
                                fill="gray", tags="grid")
        
        draw_grid()
        
        # Fungsi untuk mendapatkan koordinat grid dari event
        def get_grid_coords(event):
            x = int(event.x / cell_size)
            y = int(event.y / cell_size)
            return x, y
        
        # Fungsi untuk menggambar pixel
        def draw_pixel(x, y, color):
            if 0 <= x < grid_size and 0 <= y < grid_size:
                # Hapus pixel sebelumnya jika ada
                if (x, y) in pixels:
                    canvas.delete(pixels[(x, y)])
                
                # Gambar pixel baru
                pixel_id = canvas.create_rectangle(
                    x * cell_size, y * cell_size, 
                    (x + 1) * cell_size, (y + 1) * cell_size,
                    fill=color, outline="", tags="pixel"
                )
                pixels[(x, y)] = pixel_id
        
        # Fungsi untuk menghapus pixel
        def erase_pixel(x, y):
            if (x, y) in pixels:
                canvas.delete(pixels[(x, y)])
                del pixels[(x, y)]
        
        # Fill bucket tool
        def fill_area(x, y, target_color, replacement_color):
            if target_color == replacement_color:
                return
            if x < 0 or x >= grid_size or y < 0 or y >= grid_size:
                return
            
            # Get current color at position
            if (x, y) in pixels:
                current_color_hex = canvas.itemcget(pixels[(x, y)], "fill")
            else:
                current_color_hex = "white"
            
            if current_color_hex != target_color:
                return
            
            draw_pixel(x, y, replacement_color)
            
            # Recursively fill adjacent pixels
            fill_area(x+1, y, target_color, replacement_color)
            fill_area(x-1, y, target_color, replacement_color)
            fill_area(x, y+1, target_color, replacement_color)
            fill_area(x, y-1, target_color, replacement_color)
        
        # Event handlers
        def on_click(event):
            nonlocal is_drawing
            x, y = get_grid_coords(event)
            
            if current_tool == "pencil":
                if is_erasing:
                    erase_pixel(x, y)
                else:
                    draw_pixel(x, y, current_color)
            elif current_tool == "fill":
                # Get the color at the clicked position
                if (x, y) in pixels:
                    target_color = canvas.itemcget(pixels[(x, y)], "fill")
                else:
                    target_color = "white"
                fill_area(x, y, target_color, current_color)
            
            is_drawing = True
        
        def on_drag(event):
            nonlocal is_drawing
            if not is_drawing:
                return
                
            x, y = get_grid_coords(event)
            
            if current_tool == "pencil":
                if is_erasing:
                    erase_pixel(x, y)
                else:
                    draw_pixel(x, y, current_color)
        
        def on_release(event):
            nonlocal is_drawing
            is_drawing = False
        
        # Bind events
        canvas.bind("<Button-1>", on_click)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        
        # Fungsi untuk memilih warna
        def choose_color():
            nonlocal current_color, is_erasing
            color = colorchooser.askcolor(title="Pilih Warna")[1]
            if color:
                current_color = color
                is_erasing = False
                color_btn.configure(background=color)
                update_tool_indicators()
        
        # Fungsi untuk menghapus semua
        def clear_all():
            for pixel_id in pixels.values():
                canvas.delete(pixel_id)
            pixels.clear()
        
        # Fungsi untuk menyimpan pixel art
        def save_pixel_art():
            # Buat gambar baru
            img = Image.new("RGB", (grid_size, grid_size), "white")
            draw = ImageDraw.Draw(img)
            
            # Gambar setiap pixel
            for (x, y) in pixels:
                # Dapatkan warna dari canvas
                color_hex = canvas.itemcget(pixels[(x, y)], "fill")
                # Konversi hex ke RGB
                if color_hex:
                    r = int(color_hex[1:3], 16)
                    g = int(color_hex[3:5], 16)
                    b = int(color_hex[5:7], 16)
                    img.putpixel((x, y), (r, g, b))
            
            # Simpan gambar
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("GIF Image", "*.gif")],
                title="Simpan Pixel Art"
            )
            if file_path:
                # Scale up image sebelum menyimpan
                scaled_img = img.resize((grid_size * 10, grid_size * 10), Image.NEAREST)
                scaled_img.save(file_path)
                messagebox.showinfo("Berhasil", f"Pixel art disimpan ke:\n{file_path}")
        
        # Function to import and convert image to pixel art
        def import_image():
            nonlocal grid_size
            file_path = filedialog.askopenfilename(
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")],
                title="Pilih Gambar"
            )
            if file_path:
                try:
                    img = Image.open(file_path)
                    # Resize image to grid size
                    img = img.resize((grid_size, grid_size), Image.Resampling.NEAREST)
                    
                    # Clear current canvas
                    clear_all()
                    
                    # Draw pixels from image
                    for y in range(grid_size):
                        for x in range(grid_size):
                            r, g, b = img.getpixel((x, y))[:3]  # Handle RGBA images
                            color_hex = f"#{r:02x}{g:02x}{b:02x}"
                            draw_pixel(x, y, color_hex)
                    
                    messagebox.showinfo("Berhasil", "Gambar berhasil diimpor dan dikonversi ke pixel art!")
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal memuat gambar: {str(e)}")
        
        # Function to change grid size
        def change_grid_size():
            nonlocal grid_size
            new_size = simpledialog.askinteger("Ubah Ukuran Grid", "Masukkan ukuran grid (8-64):", 
                                            initialvalue=grid_size, minvalue=8, maxvalue=64)
            if new_size:
                grid_size = new_size
                canvas.config(width=grid_size*cell_size, height=grid_size*cell_size)
                clear_all()
                draw_grid()
        
        # Function to change cell size
        def change_cell_size():
            nonlocal cell_size
            new_size = simpledialog.askinteger("Ubah Ukuran Sel", "Masukkan ukuran sel (10-30):", 
                                            initialvalue=cell_size, minvalue=10, maxvalue=30)
            if new_size:
                cell_size = new_size
                canvas.config(width=grid_size*cell_size, height=grid_size*cell_size)
                draw_grid()
                # Redraw all pixels with new size
                for (x, y), pixel_id in list(pixels.items()):
                    canvas.delete(pixel_id)
                    new_pixel_id = canvas.create_rectangle(
                        x * cell_size, y * cell_size, 
                        (x + 1) * cell_size, (y + 1) * cell_size,
                        fill=canvas.itemcget(pixel_id, "fill"), outline="", tags="pixel"
                    )
                    pixels[(x, y)] = new_pixel_id
        
        # Function to set current tool
        def set_tool(tool):
            nonlocal current_tool, is_erasing
            current_tool = tool
            is_erasing = False
            update_tool_indicators()
        
        # Function to update tool indicators
        def update_tool_indicators():
            pencil_btn.config(relief="sunken" if current_tool == "pencil" else "raised")
            fill_btn.config(relief="sunken" if current_tool == "fill" else "raised")
            color_btn.config(bg=current_color)
            erase_btn.config(relief="sunken" if is_erasing else "raised")
        
        # Function to set erase mode
        def set_erase_mode():
            nonlocal is_erasing
            is_erasing = not is_erasing
            if is_erasing:
                current_tool = "pencil"
            update_tool_indicators()
        
        # Create color palette
        def create_color_palette():
            colors = [
                "#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF",
                "#FFFF00", "#00FFFF", "#FF00FF", "#C0C0C0", "#808080",
                "#800000", "#808000", "#008000", "#800080", "#008080", "#000080"
            ]
            
            for i, color in enumerate(colors):
                btn = tk.Button(color_frame, bg=color, width=2, height=1,
                            command=lambda c=color: set_color(c))
                btn.grid(row=0, column=i, padx=1, pady=1)
        
        # Function to set color from palette
        def set_color(color):
            nonlocal current_color, is_erasing
            current_color = color
            is_erasing = False
            update_tool_indicators()
        
        # Create tools
        pencil_btn = tk.Button(tool_frame, text="Pensil", width=8, 
                            command=lambda: set_tool("pencil"))
        pencil_btn.pack(side=tk.LEFT, padx=2)
        
        fill_btn = tk.Button(tool_frame, text="Isi", width=8,
                        command=lambda: set_tool("fill"))
        fill_btn.pack(side=tk.LEFT, padx=2)
        
        # Tombol warna
        color_btn = tk.Button(tool_frame, text="Warna", command=choose_color, 
                            bg=current_color, width=8)
        color_btn.pack(side=tk.LEFT, padx=2)
        
        # Tombol hapus
        erase_btn = tk.Button(tool_frame, text="Hapus", command=set_erase_mode, width=8)
        erase_btn.pack(side=tk.LEFT, padx=2)
        
        # Create color palette
        create_color_palette()
        
        # Additional buttons
        import_btn = tk.Button(button_frame, text="Gen PixAi", command=import_image, width=12)
        import_btn.pack(side=tk.LEFT, padx=5)
        
        grid_btn = tk.Button(button_frame, text="Ubah Grid", command=change_grid_size, width=10)
        grid_btn.pack(side=tk.LEFT, padx=5)
        
        cell_btn = tk.Button(button_frame, text="Ubah Sel", command=change_cell_size, width=10)
        cell_btn.pack(side=tk.LEFT, padx=5)
        
        # Tombol bersihkan
        clear_btn = tk.Button(button_frame, text="Bersihkan", command=clear_all, width=10)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Tombol simpan
        save_btn = tk.Button(button_frame, text="Simpan", command=save_pixel_art, width=10)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Set initial tool state
        update_tool_indicators()
        
        # Atur ukuran window
        editor.update()
        editor.minsize(editor.winfo_width(), editor.winfo_height())

def run_gui():
    root = tk.Tk()
    
    # Set Windows style if available
    if sys.platform == "win32":
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)

    app = MediaSearchApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()