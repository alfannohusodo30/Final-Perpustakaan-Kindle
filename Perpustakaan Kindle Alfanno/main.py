import hashlib
import json
import os
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

# =========================================================
# KONFIGURASI & TEMA
# =========================================================

APP_NAME = "Perpustakaan Kindle"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

USERS_FILE = os.path.join(BASE_DIR, "users.json")
BOOKS_FILE = os.path.join(BASE_DIR, "books.json")
BORROWINGS_FILE = os.path.join(BASE_DIR, "borrowings.json")

COLOR_BG = "#0F172A"
COLOR_SIDEBAR = "#1E293B"
COLOR_CARD = "#1E293B"
COLOR_INPUT = "#334155"

COLOR_TEXT = "#F8FAFC"
COLOR_MUTED = "#94A3B8"

COLOR_ACCENT = "#10B981"
COLOR_ACCENT_HOVER = "#059669"

COLOR_DANGER = "#EF4444"
COLOR_DANGER_HOVER = "#DC2626"

COLOR_WARNING = "#F59E0B"

DEFAULT_BOOKS = [
    {
        "id": 1,
        "judul": "Laskar Pelangi",
        "penulis": "Andrea Hirata",
        "tahun": "2005",
        "stok": 5,
    },
    {
        "id": 2,
        "judul": "Bumi",
        "penulis": "Tere Liye",
        "tahun": "2014",
        "stok": 4,
    },
    {
        "id": 3,
        "judul": "Atomic Habits",
        "penulis": "James Clear",
        "tahun": "2018",
        "stok": 3,
    },
    {
        "id": 4,
        "judul": "Harry Potter",
        "penulis": "J.K. Rowling",
        "tahun": "1997",
        "stok": 4,
    },
]


# =========================================================
# HELPER DATA JSON
# =========================================================


def load_json(filename, default):
  if not os.path.exists(filename):
    save_json(filename, default)
    return default.copy() if isinstance(default, list) else default.copy()
  try:
    with open(filename, "r", encoding="utf-8") as file:
      return json.load(file)
  except Exception:
    return default.copy() if isinstance(default, list) else default.copy()


def save_json(filename, data):
  with open(filename, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)


def hash_password(password):
  return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_users():
  return load_json(USERS_FILE, {})


def save_users(users):
  save_json(USERS_FILE, users)


def register_user(username, email, password):
  users = load_users()
  if username in users:
    return False, "Username sudah terdaftar."
  for user in users.values():
    if user["email"].lower() == email.lower():
      return False, "Email sudah terdaftar."
  users[username] = {"email": email, "password": hash_password(password)}
  save_users(users)
  return True, "Akun berhasil dibuat! Silakan Sign In."


def login_user(username, password):
  users = load_users()
  if username not in users:
    return False, "Username tidak ditemukan."
  if users[username]["password"] != hash_password(password):
    return False, "Password salah."
  return True, "Sign In berhasil."


def delete_user(username):
  users = load_users()
  if username in users:
    del users[username]
    save_users(users)
    return True
  return False


def load_books():
  return load_json(BOOKS_FILE, DEFAULT_BOOKS)


def save_books(books):
  save_json(BOOKS_FILE, books)


def add_book(judul, penulis, tahun, stok):
  books = load_books()
  next_id = max([b["id"] for b in books], default=0) + 1
  books.append({
      "id": next_id,
      "judul": judul,
      "penulis": penulis,
      "tahun": tahun,
      "stok": stok,
  })
  save_books(books)


def update_book(book_id, judul, penulis, tahun, stok):
  books = load_books()
  for book in books:
    if book["id"] == book_id:
      book["judul"] = judul
      book["penulis"] = penulis
      book["tahun"] = tahun
      book["stok"] = stok
      save_books(books)
      return True
  return False


def delete_book(book_id):
  books = load_books()
  borrowings = load_borrowings()
  for borrow in borrowings:
    if borrow["book_id"] == book_id and borrow["status"] == "Dipinjam":
      return False
  books = [b for b in books if b["id"] != book_id]
  save_books(books)
  return True


def load_borrowings():
  return load_json(BORROWINGS_FILE, [])


def save_borrowings(data):
  save_json(BORROWINGS_FILE, data)


def borrow_book(username, book_id):
  books = load_books()
  borrowings = load_borrowings()

  target_book = next((b for b in books if b["id"] == book_id), None)
  if not target_book:
    return False, "Buku tidak ditemukan."
  if target_book["stok"] <= 0:
    return False, "Stok buku habis."

  for b in borrowings:
    if (
        b["username"] == username
        and b["book_id"] == book_id
        and b["status"] == "Dipinjam"
    ):
      return False, "Kamu sedang meminjam buku ini."

  target_book["stok"] -= 1
  save_books(books)

  next_id = max([b["id"] for b in borrowings], default=0) + 1
  today = date.today().strftime("%Y-%m-%d")
  borrowings.append({
      "id": next_id,
      "username": username,
      "book_id": book_id,
      "judul": target_book["judul"],
      "tanggal_pinjam": today,
      "tanggal_kembali": "-",
      "status": "Dipinjam",
  })
  save_borrowings(borrowings)
  return True, f"Berhasil meminjam '{target_book['judul']}'."


def return_book(borrow_id):
  books = load_books()
  borrowings = load_borrowings()

  target_borrow = next((b for b in borrowings if b["id"] == borrow_id), None)
  if not target_borrow:
    return False, "Data transaksi tidak ditemukan."
  if target_borrow["status"] == "Dikembalikan":
    return False, "Buku sudah dikembalikan."

  for book in books:
    if book["id"] == target_borrow["book_id"]:
      book["stok"] += 1
      break
  save_books(books)

  today = date.today().strftime("%Y-%m-%d")
  target_borrow["status"] = "Dikembalikan"
  target_borrow["tanggal_kembali"] = today
  save_borrowings(borrowings)
  return True, "Buku berhasil dikembalikan."


# =========================================================
# KOMPONEN CUSTOM GUI
# =========================================================


class HoverButton(tk.Button):

  def __init__(self, parent, bg_normal, bg_hover, **kwargs):
      super().__init__(
          parent,
          bg=bg_normal,
          activebackground=bg_hover,
          activeforeground="white",
          bd=0,
          cursor="hand2",
          **kwargs,
      )
      self.bg_normal = bg_normal
      self.bg_hover = bg_hover
      self.bind("<Enter>", lambda e: self.config(bg=self.bg_hover))
      self.bind("<Leave>", lambda e: self.config(bg=self.bg_normal))


def setup_theme():
  style = ttk.Style()
  style.theme_use("clam")
  style.configure(
      "Treeview",
      background="#1E293B",
      foreground="#F8FAFC",
      fieldbackground="#1E293B",
      rowheight=34,
      font=("Segoe UI", 10),
      borderwidth=0,
  )
  style.configure(
      "Treeview.Heading",
      background="#334155",
      foreground="#F8FAFC",
      font=("Segoe UI", 10, "bold"),
      borderwidth=0,
  )
  style.map(
      "Treeview",
      background=[("selected", COLOR_ACCENT)],
      foreground=[("selected", "#FFFFFF")],
  )


# =========================================================
# JENDELA SIGN IN & SIGN UP (GERBANG AWAL)
# =========================================================


class AuthWindow(tk.Tk):

  def __init__(self):
    super().__init__()
    self.title(f"{APP_NAME} - Akses Masuk")
    self.geometry("500x620")

    # Bikin window bisa di-resize dan di-maximize
    self.resizable(True, True)
    self.minsize(420, 550)

    self.configure(bg=COLOR_BG)

    self.active_tab = "signin"
    self.build_ui()

  def build_ui(self):
    for w in self.winfo_children():
      w.destroy()

    wrapper = tk.Frame(self, bg=COLOR_BG, padx=20, pady=20)
    wrapper.pack(fill="both", expand=True)

    tk.Label(
        wrapper,
        text="📖 Perpustakaan Kindle",
        bg=COLOR_BG,
        fg=COLOR_ACCENT,
        font=("Segoe UI", 20, "bold"),
    ).pack(pady=(10, 15))

    card = tk.Frame(wrapper, bg=COLOR_CARD, padx=25, pady=20)
    card.pack(fill="both", expand=True)

    tab_frame = tk.Frame(card, bg=COLOR_CARD)
    tab_frame.pack(fill="x", pady=(0, 15))

    btn_in_bg = COLOR_ACCENT if self.active_tab == "signin" else COLOR_INPUT
    btn_up_bg = COLOR_ACCENT if self.active_tab == "signup" else COLOR_INPUT

    tk.Button(
        tab_frame,
        text="Sign In",
        bg=btn_in_bg,
        fg="white",
        font=("Segoe UI", 10, "bold"),
        bd=0,
        cursor="hand2",
        pady=7,
        command=lambda: self.switch_tab("signin"),
    ).pack(side="left", fill="x", expand=True, padx=(0, 3))

    tk.Button(
        tab_frame,
        text="Sign Up",
        bg=btn_up_bg,
        fg="white",
        font=("Segoe UI", 10, "bold"),
        bd=0,
        cursor="hand2",
        pady=7,
        command=lambda: self.switch_tab("signup"),
    ).pack(side="right", fill="x", expand=True, padx=(3, 0))

    form = tk.Frame(card, bg=COLOR_CARD)
    form.pack(fill="both", expand=True)

    if self.active_tab == "signin":
      self.render_signin(form)
    else:
      self.render_signup(form)

  def switch_tab(self, tab):
    self.active_tab = tab
    self.build_ui()

  def render_signin(self, parent):
    tk.Label(
        parent,
        text="Selamat Datang!",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 14, "bold"),
    ).pack(anchor="w")
    tk.Label(
        parent,
        text="Masukkan akun kamu untuk mengakses perpustakaan",
        bg=COLOR_CARD,
        fg=COLOR_MUTED,
        font=("Segoe UI", 9),
    ).pack(anchor="w", pady=(0, 15))

    tk.Label(
        parent,
        text="Username",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 9, "bold"),
    ).pack(anchor="w")
    self.in_user = tk.Entry(
        parent,
        bg=COLOR_INPUT,
        fg="white",
        insertbackground="white",
        bd=0,
        font=("Segoe UI", 11),
    )
    self.in_user.pack(fill="x", pady=(3, 12), ipady=6)

    tk.Label(
        parent,
        text="Password",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 9, "bold"),
    ).pack(anchor="w")
    self.in_pass = tk.Entry(
        parent,
        show="*",
        bg=COLOR_INPUT,
        fg="white",
        insertbackground="white",
        bd=0,
        font=("Segoe UI", 11),
    )
    self.in_pass.pack(fill="x", pady=(3, 20), ipady=6)

    HoverButton(
        parent,
        text="SIGN IN",
        bg_normal=COLOR_ACCENT,
        bg_hover=COLOR_ACCENT_HOVER,
        fg="white",
        font=("Segoe UI", 10, "bold"),
        pady=8,
        command=self.handle_signin,
    ).pack(fill="x")

  def render_signup(self, parent):
    tk.Label(
        parent,
        text="Buat Akun Baru",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 14, "bold"),
    ).pack(anchor="w")
    tk.Label(
        parent,
        text="Daftar akun pengguna baru",
        bg=COLOR_CARD,
        fg=COLOR_MUTED,
        font=("Segoe UI", 9),
    ).pack(anchor="w", pady=(0, 10))

    tk.Label(
        parent,
        text="Username",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 9, "bold"),
    ).pack(anchor="w")
    self.up_user = tk.Entry(
        parent,
        bg=COLOR_INPUT,
        fg="white",
        insertbackground="white",
        bd=0,
        font=("Segoe UI", 10),
    )
    self.up_user.pack(fill="x", pady=(2, 8), ipady=5)

    tk.Label(
        parent,
        text="Email",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 9, "bold"),
    ).pack(anchor="w")
    self.up_email = tk.Entry(
        parent,
        bg=COLOR_INPUT,
        fg="white",
        insertbackground="white",
        bd=0,
        font=("Segoe UI", 10),
    )
    self.up_email.pack(fill="x", pady=(2, 8), ipady=5)

    tk.Label(
        parent,
        text="Password",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 9, "bold"),
    ).pack(anchor="w")
    self.up_pass = tk.Entry(
        parent,
        show="*",
        bg=COLOR_INPUT,
        fg="white",
        insertbackground="white",
        bd=0,
        font=("Segoe UI", 10),
    )
    self.up_pass.pack(fill="x", pady=(2, 8), ipady=5)

    tk.Label(
        parent,
        text="Konfirmasi Password",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 9, "bold"),
    ).pack(anchor="w")
    self.up_confirm = tk.Entry(
        parent,
        show="*",
        bg=COLOR_INPUT,
        fg="white",
        insertbackground="white",
        bd=0,
        font=("Segoe UI", 10),
    )
    self.up_confirm.pack(fill="x", pady=(2, 15), ipady=5)

    HoverButton(
        parent,
        text="SIGN UP",
        bg_normal=COLOR_ACCENT,
        bg_hover=COLOR_ACCENT_HOVER,
        fg="white",
        font=("Segoe UI", 10, "bold"),
        pady=8,
        command=self.handle_signup,
    ).pack(fill="x")

  def handle_signin(self):
    username = self.in_user.get().strip()
    password = self.in_pass.get()

    if not username or not password:
      messagebox.showwarning("Peringatan", "Username dan Password wajib diisi.")
      return

    success, msg = login_user(username, password)
    if success:
      messagebox.showinfo("Berhasil", msg)
      self.destroy()
      app = MainWindow(username)
      app.mainloop()
    else:
      messagebox.showerror("Gagal", msg)

  def handle_signup(self):
    username = self.up_user.get().strip()
    email = self.up_email.get().strip()
    password = self.up_pass.get()
    confirm = self.up_confirm.get()

    if not username or not email or not password:
      messagebox.showwarning("Peringatan", "Semua kolom wajib diisi.")
      return

    if password != confirm:
      messagebox.showerror("Error", "Konfirmasi password tidak cocok.")
      return

    success, msg = register_user(username, email, password)
    if success:
      messagebox.showinfo("Berhasil", msg)
      self.switch_tab("signin")
    else:
      messagebox.showerror("Gagal", msg)


# =========================================================
# DASHBOARD UTAMA (BISA FULLSCREEN & RESIZABLE)
# =========================================================


class MainWindow(tk.Tk):

  def __init__(self, username):
    super().__init__()
    self.current_user = username

    self.title(APP_NAME)

    # Mengatur ukuran awal dan memperbolehkan di-resize secara bebas
    self.geometry("1200x720")
    self.resizable(True, True)
    self.minsize(900, 600)

    # Otomatis buka jendela dalam posisi Maximized (Layar Penuh Windowed)
    try:
      self.state("zoomed")
    except Exception:
      pass

    # Menambahkan opsi toggle True Fullscreen pakai tombol F11
    self.is_fullscreen = False
    self.bind("<F11>", self.toggle_fullscreen)
    self.bind("<Escape>", self.end_fullscreen)

    self.configure(bg=COLOR_BG)
    setup_theme()

    self.sidebar_frame = tk.Frame(self, bg=COLOR_SIDEBAR, width=240)
    self.sidebar_frame.pack_propagate(False)
    self.sidebar_frame.pack(side="left", fill="y")

    self.main_container = tk.Frame(self, bg=COLOR_BG)
    self.main_container.pack(side="right", fill="both", expand=True)

    self.frames = {}
    for Page in (HomePage, BookPage, BorrowPage, UserPage):
      frame = Page(self.main_container, self)
      self.frames[Page.__name__] = frame
      frame.grid(row=0, column=0, sticky="nsew")

    self.main_container.grid_rowconfigure(0, weight=1)
    self.main_container.grid_columnconfigure(0, weight=1)

    self.render_sidebar()
    self.show_page("HomePage")

  def toggle_fullscreen(self, event=None):
    self.is_fullscreen = not self.is_fullscreen
    self.attributes("-fullscreen", self.is_fullscreen)

  def end_fullscreen(self, event=None):
    self.is_fullscreen = False
    self.attributes("-fullscreen", False)

  def render_sidebar(self):
    for w in self.sidebar_frame.winfo_children():
      w.destroy()

    brand = tk.Frame(self.sidebar_frame, bg=COLOR_SIDEBAR)
    brand.pack(fill="x", pady=25, padx=20)

    tk.Label(
        brand,
        text="📖 KINDLE",
        bg=COLOR_SIDEBAR,
        fg=COLOR_ACCENT,
        font=("Segoe UI", 18, "bold"),
    ).pack(anchor="w")
    tk.Label(
        brand,
        text="Library Portal",
        bg=COLOR_SIDEBAR,
        fg=COLOR_MUTED,
        font=("Segoe UI", 9),
    ).pack(anchor="w")

    nav = tk.Frame(self.sidebar_frame, bg=COLOR_SIDEBAR)
    nav.pack(fill="x", pady=10)

    menu_items = [
        ("🏠  Beranda", "HomePage"),
        ("📚  Koleksi Buku", "BookPage"),
        ("🔄  Peminjaman", "BorrowPage"),
        ("👥  Pengguna", "UserPage"),
    ]

    for text, page in menu_items:
      HoverButton(
          nav,
          text=text,
          bg_normal=COLOR_SIDEBAR,
          bg_hover="#334155",
          fg=COLOR_TEXT,
          font=("Segoe UI", 11),
          anchor="w",
          padx=20,
          pady=12,
          command=lambda p=page: self.show_page(p),
      ).pack(fill="x", pady=2)

    # Tombol toggle Layar Penuh di Sidebar
    HoverButton(
        nav,
        text="🖥️  Layar Penuh (F11)",
        bg_normal=COLOR_SIDEBAR,
        bg_hover="#334155",
        fg=COLOR_MUTED,
        font=("Segoe UI", 10),
        anchor="w",
        padx=20,
        pady=8,
        command=self.toggle_fullscreen,
    ).pack(fill="x", pady=(15, 2))

    user_panel = tk.Frame(self.sidebar_frame, bg="#0F172A", padx=15, pady=15)
    user_panel.pack(side="bottom", fill="x", padx=15, pady=20)

    tk.Label(
        user_panel,
        text=f"👤 {self.current_user}",
        bg="#0F172A",
        fg=COLOR_TEXT,
        font=("Segoe UI", 10, "bold"),
    ).pack(anchor="w", pady=(0, 8))

    HoverButton(
        user_panel,
        text="Sign Out",
        bg_normal=COLOR_DANGER,
        bg_hover=COLOR_DANGER_HOVER,
        fg="white",
        font=("Segoe UI", 9, "bold"),
        pady=5,
        command=self.logout,
    ).pack(fill="x")

  def show_page(self, page_name):
    frame = self.frames[page_name]
    if hasattr(frame, "on_show"):
      frame.on_show()
    frame.tkraise()

  def logout(self):
    self.destroy()
    auth_app = AuthWindow()
    auth_app.mainloop()


# =========================================================
# PAGE DASHBOARD / BERANDA
# =========================================================


class HomePage(tk.Frame):

  def __init__(self, parent, controller):
    super().__init__(parent, bg=COLOR_BG)
    self.controller = controller

  def on_show(self):
    for w in self.winfo_children():
      w.destroy()

    container = tk.Frame(self, bg=COLOR_BG, padx=35, pady=35)
    container.pack(fill="both", expand=True)

    hero = tk.Frame(container, bg=COLOR_CARD, padx=30, pady=25)
    hero.pack(fill="x", pady=(0, 25))

    tk.Label(
        hero,
        text=f"Selamat Datang, {self.controller.current_user}! 👋",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 22, "bold"),
    ).pack(anchor="w")
    tk.Label(
        hero,
        text="Ringkasan inventaris dan peminjaman buku perpustakaan.",
        bg=COLOR_CARD,
        fg=COLOR_MUTED,
        font=("Segoe UI", 11),
    ).pack(anchor="w", pady=(5, 0))

    cards = tk.Frame(container, bg=COLOR_BG)
    cards.pack(fill="x", pady=(0, 25))

    books = load_books()
    borrowings = load_borrowings()

    total_titles = len(books)
    total_stok = sum(b["stok"] for b in books)
    total_borrowed = sum(1 for b in borrowings if b["status"] == "Dipinjam")

    self.create_card(
        cards, "📚  Judul Buku", str(total_titles), COLOR_ACCENT
    ).pack(side="left", fill="both", expand=True, padx=(0, 10))
    self.create_card(cards, "📦  Total Stok", str(total_stok), "#3B82F6").pack(
        side="left", fill="both", expand=True, padx=5
    )
    self.create_card(
        cards, "🔖  Buku Dipinjam", str(total_borrowed), COLOR_WARNING
    ).pack(side="left", fill="both", expand=True, padx=(10, 0))

    info = tk.Frame(container, bg=COLOR_CARD, padx=25, pady=20)
    info.pack(fill="both", expand=True)

    tk.Label(
        info,
        text="Akses Cepat",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 14, "bold"),
    ).pack(anchor="w", pady=(0, 10))
    quick_text = (
        "• 'Koleksi Buku' untuk menambah, mengedit, atau menghapus buku.\n"
        "• 'Peminjaman' untuk proses pinjam dan pengembalian buku.\n"
        "• 'Pengguna' untuk mengelola daftar akun terdaftar.\n"
        "• Tekan 'F11' atau tombol di sidebar untuk mode Fullscreen."
    )
    tk.Label(
        info,
        text=quick_text,
        bg=COLOR_CARD,
        fg=COLOR_MUTED,
        font=("Segoe UI", 11),
        justify="left",
    ).pack(anchor="w")

  def create_card(self, parent, title, value, color):
    card = tk.Frame(parent, bg=COLOR_CARD, padx=20, pady=20)
    tk.Frame(card, bg=color, height=4).pack(fill="x", side="top", pady=(0, 10))
    tk.Label(
        card, text=title, bg=COLOR_CARD, fg=COLOR_MUTED, font=("Segoe UI", 11)
    ).pack(anchor="w")
    tk.Label(
        card,
        text=value,
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 26, "bold"),
    ).pack(anchor="w", pady=(5, 0))
    return card


# =========================================================
# PAGE BOOK MANAGEMENT
# =========================================================


class BookPage(tk.Frame):

  def __init__(self, parent, controller):
    super().__init__(parent, bg=COLOR_BG)
    self.controller = controller
    self.selected_id = None

    container = tk.Frame(self, bg=COLOR_BG, padx=30, pady=25)
    container.pack(fill="both", expand=True)

    tk.Label(
        container,
        text="Koleksi & Inventaris Buku",
        bg=COLOR_BG,
        fg=COLOR_TEXT,
        font=("Segoe UI", 20, "bold"),
    ).pack(anchor="w", pady=(0, 15))

    form_card = tk.Frame(container, bg=COLOR_CARD, padx=20, pady=15)
    form_card.pack(fill="x", pady=(0, 15))

    self.entries = {}
    inputs_frame = tk.Frame(form_card, bg=COLOR_CARD)
    inputs_frame.pack(fill="x", pady=(0, 10))

    fields = [
        ("Judul", "judul", 22),
        ("Penulis", "penulis", 18),
        ("Tahun", "tahun", 8),
        ("Stok", "stok", 8),
    ]
    for label, name, w in fields:
      col = tk.Frame(inputs_frame, bg=COLOR_CARD)
      col.pack(side="left", padx=(0, 10), fill="x", expand=True)
      tk.Label(
          col,
          text=label,
          bg=COLOR_CARD,
          fg=COLOR_MUTED,
          font=("Segoe UI", 9, "bold"),
      ).pack(anchor="w")
      e = tk.Entry(
          col,
          bg=COLOR_INPUT,
          fg="white",
          insertbackground="white",
          bd=0,
          font=("Segoe UI", 10),
      )
      e.pack(fill="x", ipady=5, pady=(3, 0))
      self.entries[name] = e

    btn_frame = tk.Frame(form_card, bg=COLOR_CARD)
    btn_frame.pack(fill="x")

    HoverButton(
        btn_frame,
        text="Tambah Buku",
        bg_normal=COLOR_ACCENT,
        bg_hover=COLOR_ACCENT_HOVER,
        fg="white",
        font=("Segoe UI", 9, "bold"),
        padx=12,
        pady=5,
        command=self.add,
    ).pack(side="left", padx=(0, 5))
    HoverButton(
        btn_frame,
        text="Update Buku",
        bg_normal="#3B82F6",
        bg_hover="#2563EB",
        fg="white",
        font=("Segoe UI", 9, "bold"),
        padx=12,
        pady=5,
        command=self.update,
    ).pack(side="left", padx=5)
    HoverButton(
        btn_frame,
        text="Hapus Buku",
        bg_normal=COLOR_DANGER,
        bg_hover=COLOR_DANGER_HOVER,
        fg="white",
        font=("Segoe UI", 9, "bold"),
        padx=12,
        pady=5,
        command=self.delete,
    ).pack(side="left", padx=5)
    HoverButton(
        btn_frame,
        text="Clear",
        bg_normal="#64748B",
        bg_hover="#475569",
        fg="white",
        font=("Segoe UI", 9, "bold"),
        padx=12,
        pady=5,
        command=self.clear,
    ).pack(side="left", padx=5)

    table_card = tk.Frame(container, bg=COLOR_CARD, padx=20, pady=15)
    table_card.pack(fill="both", expand=True)

    search_frame = tk.Frame(table_card, bg=COLOR_CARD)
    search_frame.pack(fill="x", pady=(0, 10))

    tk.Label(
        search_frame,
        text="🔍 Cari Buku:",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 10, "bold"),
    ).pack(side="left", padx=(0, 8))
    self.search = tk.Entry(
        search_frame,
        bg=COLOR_INPUT,
        fg="white",
        insertbackground="white",
        bd=0,
        font=("Segoe UI", 10),
        width=35,
    )
    self.search.pack(side="left", ipady=5)
    self.search.bind("<KeyRelease>", lambda e: self.refresh())

    columns = ("id", "judul", "penulis", "tahun", "stok")
    self.tree = ttk.Treeview(table_card, columns=columns, show="headings")

    widths = {"id": 60, "judul": 350, "penulis": 220, "tahun": 100, "stok": 90}
    headers = {
        "id": "ID",
        "judul": "Judul Buku",
        "penulis": "Penulis",
        "tahun": "Tahun",
        "stok": "Stok",
    }

    for col in columns:
      self.tree.heading(col, text=headers[col])
      self.tree.column(col, width=widths[col], stretch=True)

    self.tree.pack(fill="both", expand=True)
    self.tree.bind("<<TreeviewSelect>>", self.select)

  def on_show(self):
    self.refresh()

  def refresh(self):
    for item in self.tree.get_children():
      self.tree.delete(item)

    keyword = self.search.get().lower()
    for book in load_books():
      if (
          keyword
          and keyword not in book["judul"].lower()
          and keyword not in book["penulis"].lower()
      ):
        continue
      self.tree.insert(
          "",
          "end",
          values=(
              book["id"],
              book["judul"],
              book["penulis"],
              book["tahun"],
              book["stok"],
          ),
      )

  def select(self, event):
    selected = self.tree.selection()
    if not selected:
      return
    values = self.tree.item(selected[0], "values")
    self.selected_id = int(values[0])

    self.entries["judul"].delete(0, tk.END)
    self.entries["judul"].insert(0, values[1])
    self.entries["penulis"].delete(0, tk.END)
    self.entries["penulis"].insert(0, values[2])
    self.entries["tahun"].delete(0, tk.END)
    self.entries["tahun"].insert(0, values[3])
    self.entries["stok"].delete(0, tk.END)
    self.entries["stok"].insert(0, values[4])

  def add(self):
    judul = self.entries["judul"].get().strip()
    penulis = self.entries["penulis"].get().strip()
    tahun = self.entries["tahun"].get().strip()
    stok = self.entries["stok"].get().strip()

    if not judul or not penulis or not tahun or not stok:
      messagebox.showwarning("Peringatan", "Semua kolom wajib diisi.")
      return

    try:
      stok = int(stok)
      if stok < 0:
        raise ValueError
    except ValueError:
      messagebox.showerror("Error", "Stok harus angka positif.")
      return

    add_book(judul, penulis, tahun, stok)
    messagebox.showinfo("Berhasil", "Buku berhasil ditambahkan.")
    self.clear()
    self.refresh()

  def update(self):
    if self.selected_id is None:
      messagebox.showwarning("Peringatan", "Pilih buku dari tabel dahulu.")
      return

    judul = self.entries["judul"].get().strip()
    penulis = self.entries["penulis"].get().strip()
    tahun = self.entries["tahun"].get().strip()

    try:
      stok = int(self.entries["stok"].get().strip())
      if stok < 0:
        raise ValueError
    except ValueError:
      messagebox.showerror("Error", "Stok harus angka positif.")
      return

    if update_book(self.selected_id, judul, penulis, tahun, stok):
      messagebox.showinfo("Berhasil", "Buku diperbarui.")
      self.clear()
      self.refresh()
    else:
      messagebox.showerror("Gagal", "Buku tidak ditemukan.")

  def delete(self):
    if self.selected_id is None:
      messagebox.showwarning("Peringatan", "Pilih buku dari tabel dahulu.")
      return

    if messagebox.askyesno("Konfirmasi", "Hapus buku ini?"):
      if delete_book(self.selected_id):
        messagebox.showinfo("Berhasil", "Buku berhasil dihapus.")
        self.clear()
        self.refresh()
      else:
        messagebox.showerror("Gagal", "Buku sedang dipinjam.")

  def clear(self):
    self.selected_id = None
    for entry in self.entries.values():
      entry.delete(0, tk.END)
    if self.tree.selection():
      self.tree.selection_remove(self.tree.selection())


# =========================================================
# PAGE BORROWING
# =========================================================


class BorrowPage(tk.Frame):

  def __init__(self, parent, controller):
    super().__init__(parent, bg=COLOR_BG)
    self.controller = controller
    self.selected_borrow_id = None

    container = tk.Frame(self, bg=COLOR_BG, padx=30, pady=25)
    container.pack(fill="both", expand=True)

    tk.Label(
        container,
        text="Peminjaman & Pengembalian",
        bg=COLOR_BG,
        fg=COLOR_TEXT,
        font=("Segoe UI", 20, "bold"),
    ).pack(anchor="w", pady=(0, 15))

    control_card = tk.Frame(container, bg=COLOR_CARD, padx=20, pady=20)
    control_card.pack(fill="x", pady=(0, 15))

    tk.Label(
        control_card,
        text="Pilih Buku Tersedia:",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 10, "bold"),
    ).pack(side="left", padx=(0, 10))

    self.book_combo = ttk.Combobox(control_card, width=45, state="readonly")
    self.book_combo.pack(side="left", padx=(0, 15))

    HoverButton(
        control_card,
        text="Pinjam Buku",
        bg_normal=COLOR_ACCENT,
        bg_hover=COLOR_ACCENT_HOVER,
        fg="white",
        font=("Segoe UI", 9, "bold"),
        padx=15,
        pady=6,
        command=self.handle_borrow,
    ).pack(side="left", padx=(0, 5))
    HoverButton(
        control_card,
        text="Kembalikan Buku",
        bg_normal="#3B82F6",
        bg_hover="#2563EB",
        fg="white",
        font=("Segoe UI", 9, "bold"),
        padx=15,
        pady=6,
        command=self.handle_return,
    ).pack(side="left")

    table_card = tk.Frame(container, bg=COLOR_CARD, padx=20, pady=20)
    table_card.pack(fill="both", expand=True)

    columns = ("id", "username", "judul", "pinjam", "kembali", "status")
    self.tree = ttk.Treeview(table_card, columns=columns, show="headings")

    widths = {
        "id": 50,
        "username": 140,
        "judul": 280,
        "pinjam": 120,
        "kembali": 120,
        "status": 100,
    }
    headers = {
        "id": "ID",
        "username": "Peminjam",
        "judul": "Judul Buku",
        "pinjam": "Tgl Pinjam",
        "kembali": "Tgl Kembali",
        "status": "Status",
    }

    for col in columns:
      self.tree.heading(col, text=headers[col])
      self.tree.column(col, width=widths[col], stretch=True)

    self.tree.pack(fill="both", expand=True)
    self.tree.bind("<<TreeviewSelect>>", self.select)

  def on_show(self):
    self.refresh_combobox()
    self.refresh_table()

  def refresh_combobox(self):
    books = load_books()
    self.book_list = [b for b in books if b["stok"] > 0]
    self.book_combo["values"] = [
        f"{b['id']} - {b['judul']} (Stok: {b['stok']})" for b in self.book_list
    ]
    if self.book_list:
      self.book_combo.current(0)
    else:
      self.book_combo.set("")

  def refresh_table(self):
    for item in self.tree.get_children():
      self.tree.delete(item)

    for b in load_borrowings():
      self.tree.insert(
          "",
          "end",
          values=(
              b["id"],
              b["username"],
              b["judul"],
              b["tanggal_pinjam"],
              b["tanggal_kembali"],
              b["status"],
          ),
      )

  def select(self, event):
    selected = self.tree.selection()
    if selected:
      values = self.tree.item(selected[0], "values")
      self.selected_borrow_id = int(values[0])

  def handle_borrow(self):
    if not self.book_combo.get():
      messagebox.showwarning("Peringatan", "Pilih buku terlebih dahulu.")
      return

    index = self.book_combo.current()
    if index < 0 or index >= len(self.book_list):
      return

    book_id = self.book_list[index]["id"]
    username = self.controller.current_user

    success, msg = borrow_book(username, book_id)
    if success:
      messagebox.showinfo("Berhasil", msg)
      self.refresh_combobox()
      self.refresh_table()
    else:
      messagebox.showerror("Gagal", msg)

  def handle_return(self):
    if self.selected_borrow_id is None:
      messagebox.showwarning(
          "Peringatan", "Pilih data dari tabel untuk mengembalikan buku."
      )
      return

    success, msg = return_book(self.selected_borrow_id)
    if success:
      messagebox.showinfo("Berhasil", msg)
      self.selected_borrow_id = None
      self.refresh_combobox()
      self.refresh_table()
    else:
      messagebox.showerror("Gagal", msg)


# =========================================================
# PAGE USER MANAGEMENT
# =========================================================


class UserPage(tk.Frame):

  def __init__(self, parent, controller):
    super().__init__(parent, bg=COLOR_BG)
    self.controller = controller
    self.selected_username = None

    container = tk.Frame(self, bg=COLOR_BG, padx=30, pady=25)
    container.pack(fill="both", expand=True)

    tk.Label(
        container,
        text="Manajemen Pengguna",
        bg=COLOR_BG,
        fg=COLOR_TEXT,
        font=("Segoe UI", 20, "bold"),
    ).pack(anchor="w", pady=(0, 15))

    top_card = tk.Frame(container, bg=COLOR_CARD, padx=20, pady=15)
    top_card.pack(fill="x", pady=(0, 15))

    HoverButton(
        top_card,
        text="Hapus User Terpilih",
        bg_normal=COLOR_DANGER,
        bg_hover=COLOR_DANGER_HOVER,
        fg="white",
        font=("Segoe UI", 9, "bold"),
        padx=15,
        pady=6,
        command=self.handle_delete,
    ).pack(side="left")

    table_card = tk.Frame(container, bg=COLOR_CARD, padx=20, pady=20)
    table_card.pack(fill="both", expand=True)

    columns = ("username", "email")
    self.tree = ttk.Treeview(table_card, columns=columns, show="headings")

    self.tree.heading("username", text="Username")
    self.tree.heading("email", text="Email")
    self.tree.column("username", width=300, stretch=True)
    self.tree.column("email", width=400, stretch=True)

    self.tree.pack(fill="both", expand=True)
    self.tree.bind("<<TreeviewSelect>>", self.select)

  def on_show(self):
    self.refresh()

  def refresh(self):
    for item in self.tree.get_children():
      self.tree.delete(item)

    for username, info in load_users().items():
      self.tree.insert("", "end", values=(username, info["email"]))

  def select(self, event):
    selected = self.tree.selection()
    if selected:
      values = self.tree.item(selected[0], "values")
      self.selected_username = values[0]

  def handle_delete(self):
    if not self.selected_username:
      messagebox.showwarning("Peringatan", "Pilih pengguna dari tabel.")
      return

    if self.selected_username == self.controller.current_user:
      messagebox.showerror(
          "Gagal", "Tidak bisa menghapus akun yang sedang aktif."
      )
      return

    if messagebox.askyesno(
        "Konfirmasi", f"Hapus pengguna '{self.selected_username}'?"
    ):
      if delete_user(self.selected_username):
        messagebox.showinfo("Berhasil", "Pengguna berhasil dihapus.")
        self.selected_username = None
        self.refresh()
      else:
        messagebox.showerror("Gagal", "Pengguna tidak ditemukan.")


# =========================================================
# EXECUTION MAIN
# =========================================================

if __name__ == "__main__":
  auth_app = AuthWindow()
  auth_app.mainloop()
  