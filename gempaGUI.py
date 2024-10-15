import requests, os, sys, winreg, subprocess
from datetime import datetime
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
from tkinter import messagebox

# URL BMKG
url = "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json"

datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

if not os.path.exists("database") and not os.path.exists("database/gempa.txt"):
    os.mkdir("database")
    with open("database/gempa.txt", "w") as f:
        f.write("")
        f.close()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}

# Mendapatkan data gempa terkini
def get_gempa_terkini():
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return data["Infogempa"]["gempa"]
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        return None
    except ValueError as e:
        print("Error decoding JSON:", e)
        return None

# Menampilkan informasi gempa di aplikasi Tkinter
def show_info_in_tk(gempa):
    try:
        # Membersihkan konten sebelumnya (jika ada)
        for widget in window.winfo_children():
            widget.destroy()

        # Mencoba mengambil data gambar hingga berhasil
        img_url = f"https://data.bmkg.go.id/DataMKG/TEWS/{gempa['Shakemap']}"
        success = False
        while not success:
            response = requests.get(img_url, headers=headers)
            if 'image' in response.headers['Content-Type']:
                print("Gambar tersedia untuk ditampilkan.")
                messagebox.showinfo("Informasi", "Gambar tersedia untuk ditampilkan.")
                success = True
                break
            else:
                print("Tidak ada gambar yang tersedia untuk ditampilkan.")
                print(response.headers['Content-Type'])
                gempa = get_gempa_terkini()
                if gempa is None:
                    messagebox.showerror("Error", "Tidak dapat mengambil data gempa")
                    return
                img_url = f"https://data.bmkg.go.id/DataMKG/TEWS/{gempa['Shakemap']}"

        # Menampilkan gambar menggunakan buffer
        image_data = BytesIO(response.content)
        image = Image.open(image_data)
        # image = image.resize((200, 200), Image.ANTIALIAS)
        # lebar, tinggi
        image = image.resize((380, 350))
        photo = ImageTk.PhotoImage(image)
        label_gambar = tk.Label(window, image=photo)
        label_gambar.image = photo
        label_gambar.pack()

        # Menampilkan informasi gempa
        label_date = tk.Label(window, text=f"Tanggal: {gempa['Tanggal']}")
        label_date.pack()
        label_time = tk.Label(window, text=f"Jam: {gempa['Jam']}")
        label_time.pack()
        label_datetime = tk.Label(window, text=f"Tenggat Waktu: {gempa['DateTime']}")
        label_datetime.pack()
        label_coord = tk.Label(window, text=f"Koordinat: {gempa['Coordinates']}")
        label_coord.pack()
        label_maps = tk.Label(window, text=f"Maps: https://www.google.com/maps/place/{gempa['Coordinates']}")
        label_maps.pack()
        label_lintang = tk.Label(window, text=f"Lintang: {gempa['Lintang']}")
        label_lintang.pack()
        label_bujur = tk.Label(window, text=f"Bujur: {gempa['Bujur']}")
        label_bujur.pack()
        label_kedalaman = tk.Label(window, text=f"Kedalaman: {gempa['Kedalaman']} km")
        label_kedalaman.pack()
        label_location = tk.Label(window, text=f"Lokasi: {gempa['Wilayah']}")
        label_location.pack()
        label_magnitude = tk.Label(window, text=f"Magnitudo: {gempa['Magnitude']}")
        label_magnitude.pack()
        label_potensi = tk.Label(window, text=f"Potensi: {gempa['Potensi']}")
        label_potensi.pack()
        label_dirasakan = tk.Label(window, text=f"Dirasakan: {gempa['Dirasakan']}")
        label_dirasakan.pack()
        label_shakemap = tk.Label(window, text=f"Shakemap: https://data.bmkg.go.id/DataMKG/TEWS/{gempa['Shakemap']}")
        label_shakemap.pack()

        save_button = tk.Button(window, text="Simpan", command=save_gempa)
        save_button.pack()

        google_maps = tk.Button(window, text="Google Maps", command=open_google_maps)
        google_maps.pack()

    except Exception as e:
        print("Error:", e)
        messagebox.showerror("Error", f"Terjadi kesalahan saat menampilkan informasi gempa: {e}")

def open_google_maps():
    subprocess.Popen(f"start https://www.google.com/maps/search/{gempa['Coordinates']}?sa=X&ved=1t:242&ictx=111", shell=True)

def save_gempa():
    # berikan petunjuk ke pengguna letak file gempa.txt
    lokasi = os.getcwd() + r"\database\gempa.txt"
    try:
        # Menyimpan informasi gempa
        messagebox.showinfo("Informasi", "Informasi gempa telah disimpan. " + lokasi)
        if os.path.exists(lokasi):
            subprocess.Popen(r'explorer /select,"{}"'.format(lokasi))
        else:
            subprocess.call(['start', lokasi], shell=True)
        gempa = get_gempa_terkini()

        if gempa is not None or not os.path.exists(r"database\gempa.txt"):
            with open(r"database\gempa.txt", "a") as f:
                f.write(f"Informasi Gempa {datetime}\n\n")
                f.write(f"Tanggal: {gempa['Tanggal']}\n")
                f.write(f"Jam: {gempa['Jam']}\n")
                f.write(f"Tenggat Waktu: {gempa['DateTime']}\n")
                f.write(f"Koordinat: {gempa['Coordinates']}\n")
                f.write(f"Lintang: {gempa['Lintang']}\n")
                f.write(f"Bujur: {gempa['Bujur']}\n")
                f.write(f"Kedalaman: {gempa['Kedalaman']} km\n")
                f.write(f"Lokasi: {gempa['Wilayah']}\n")
                f.write(f"Magnitudo: {gempa['Magnitude']}\n")
                f.write(f"Potensi: {gempa['Potensi']}\n")
                f.write(f"Dirasakan: {gempa['Dirasakan']}\n")
                f.write(f"Shakemap: {gempa['Shakemap']}\n")
                f.write(f"URL Gempa: https://data.bmkg.go.id/DataMKG/TEWS/{gempa['Shakemap']}")
                f.write("\n\n" + "====================="*2 + "\n\n")
                f.close()
        else:
            messagebox.showerror("Error", "Tidak dapat mengambil data gempa")
    except Exception as e:
        print("Error:", e)
        messagebox.showerror("Error", f"Terjadi kesalahan saat menyimpan informasi gempa: {e}")

def refresh_data():
    # Membersihkan konten sebelumnya
    for widget in window.winfo_children():
        widget.destroy()
    # Memanggil fungsi untuk menampilkan data gempa terkini
    gempa = get_gempa_terkini()
    if gempa is not None:
        show_info_in_tk(gempa)
    else:
        messagebox.showerror("Error", "Tidak dapat mengambil data gempa")

    # refresh_button = tk.Button(window, text="Refresh", command=refresh_data)
    # refresh_button.pack()
    while True:
        if gempa is not None:
            refresh_button = tk.Button(window, text="Refresh", command=refresh_data)
            refresh_button.pack()
            break
        else:
            messagebox.showerror("Error", "Tidak dapat mengambil data gempa")

# Membuat window Tkinter
window = tk.Tk()
window.title("Informasi Gempa")
window.geometry("420x695")

# icon_path = r"gempa.ico"
# if os.path.exists(icon_path):
#     window.iconbitmap(icon_path)

# os.chdir(os.path.dirname(os.path.abspath(__file__)))
icon_path = os.path.abspath(r"Bahan_Koding\gempa.ico")

if os.path.exists(icon_path):
    window.iconbitmap(icon_path)
else:
    print(icon_path)
    print("File ikon tidak ditemukan.")

# Menampilkan informasi gempa
gempa = get_gempa_terkini()
if gempa is not None:
    show_info_in_tk(gempa)
else:
    messagebox.showerror("Error", "Tidak dapat mengambil data gempa")

# Tombol refresh
# refresh_button = tk.Button(window, text="Refresh", command=refresh_data)
# refresh_button.pack()
    
while True:
    if gempa is not None:
        refresh_button = tk.Button(window, text="Refresh", command=refresh_data)
        refresh_button.pack()
        break
    else:
        messagebox.showerror("Error", "Tidak dapat mengambil data gempa")

def add_to_startup(file_path):
    key = winreg.HKEY_CURRENT_USER
    key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"
    with winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS) as reg_key:
        winreg.SetValueEx(reg_key, "InformasiGempa", 0, winreg.REG_SZ, file_path)

# Get current script file path
script_path = os.path.abspath(sys.argv[0])

# Add script to startup
add_to_startup(script_path)

# Menampilkan window Tkinter
window.mainloop()
