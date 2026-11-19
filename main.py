import tkinter as tk
from tkinter import filedialog, messagebox
import os
import hashlib
import subprocess
import json
import hmac
from cryptography.fernet import Fernet
from PIL import Image, ImageTk

# ==========================================
# DASHBOARD OPERATION STATISTICS
# ==========================================

STATS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vault_stats.json")
MODULE_NAMES = ["Text", "Image", "Audio", "Video"]
def load_operation_stats():
    stats = {name: {"Encryption": 0, "Decryption": 0} for name in MODULE_NAMES}
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as stats_file:
            saved = json.load(stats_file)
        for name in MODULE_NAMES:
            for action in ("Encryption", "Decryption"):
                value = saved.get(name, {}).get(action, 0)
                if isinstance(value, int) and value >= 0:
                    stats[name][action] = value
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return stats
operation_stats = load_operation_stats()

def record_operation(module, action):

    if module not in operation_stats or action not in ("Encryption", "Decryption"):

        return

    operation_stats[module][action] += 1

    try:

        with open(STATS_FILE, "w", encoding="utf-8") as stats_file:

            json.dump(operation_stats, stats_file, indent=4)

    except OSError:

        pass

# ==========================================

# 🔐 SECURE HIDDEN VAULT

# ==========================================

VAULT_FOLDER = os.path.join(

    os.path.dirname(os.path.abspath(__file__)),

    ".secure_storage"

)

def create_secure_vault():

    """

    Create the secure storage folder and hide it on Windows.

    """

    if not os.path.exists(VAULT_FOLDER):

        os.makedirs(VAULT_FOLDER)

    # Hide folder on Windows

    try:

        subprocess.run(

            ["attrib", "+h", VAULT_FOLDER],

            shell=False,

            check=False

        )

    except Exception:

        pass

    return VAULT_FOLDER

def get_vault_path(file_name):

    """

    Return the complete path of a file inside the hidden vault.

    """

    create_secure_vault()

    return os.path.join(

        VAULT_FOLDER,

        file_name

    )

def hide_secure_vault():

    """

    Make the Secure Vault hidden again.

    """

    try:

        subprocess.run(

            ["attrib", "+h", VAULT_FOLDER],

            shell=False,

            check=False

        )

    except Exception:

        pass

create_secure_vault()

# ==========================================

# ENCRYPTION KEY

# ==========================================

KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "secret.key")

if not os.path.exists(KEY_FILE):

    key = Fernet.generate_key()

    with open(KEY_FILE, "wb") as key_file:

        key_file.write(key)

else:

    with open(KEY_FILE, "rb") as key_file:

        key = key_file.read()

try:

    cipher = Fernet(key)

except (TypeError, ValueError):

    raise RuntimeError(

        "The existing secret.key file is invalid. Restore its original backup; "

        "do not generate a new key if you need to decrypt existing vault files."

    )

# ==========================================

# SHA-256 FILE INTEGRITY

# ==========================================

def calculate_sha256(file_path):

    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as file:

        for block in iter(lambda: file.read(4096), b""):

            sha256_hash.update(block)

    return sha256_hash.hexdigest()

# ==========================================

# FILE SIZE LIMITS

# ==========================================

MAX_TEXT_SIZE = 10 * 1024 * 1024      # 10 MB

MAX_IMAGE_SIZE = 20 * 1024 * 1024     # 20 MB

MAX_AUDIO_SIZE = 50 * 1024 * 1024     # 50 MB

MAX_VIDEO_SIZE = 200 * 1024 * 1024    # 200 MB

def check_file_size(file_path, max_size, file_type):

    file_size = os.path.getsize(file_path)

    if file_size > max_size:

        actual_mb = file_size / (1024 * 1024)

        max_mb = max_size / (1024 * 1024)

        messagebox.showerror(

            "File Too Large",

            f"❌ {file_type} file is too large!\n\n"

            f"Selected size: {actual_mb:.2f} MB\n"

            f"Maximum allowed: {max_mb:.0f} MB"

        )

        return False

    return True

# ==========================================

# MAIN WINDOW

# ==========================================

window = tk.Tk()

window.title("Multimedia Cryptography")

window.attributes("-fullscreen", True)

window.bind("<Escape>", lambda event: window.attributes("-fullscreen", False))

window.configure(bg="#F4F7FB")

# window.resizable(False, False)

# ==========================================

# TITLE

# ==========================================

title_label = tk.Label(

    window,

    text="🔐 MULTIMEDIA CRYPTOGRAPHY",

    font=("Arial", 20, "bold"),

    bg="#F4F7FB",

    fg="#172554"

)

title_label.pack(pady=20)

# ==========================================

# SUB TITLE

# ==========================================

subtitle_label = tk.Label(

    window,

    text="Secure Text, Image, Audio and Video Files",

    font=("Arial", 10),

    bg="#F4F7FB",

    fg="#64748B"

)

subtitle_label.pack(pady=2)

# ==========================================

# FILE STATUS

# ==========================================

file_label = tk.Label(

    window,

    text="No file selected",

    font=("Arial", 10),

    bg="#F4F7FB",

    fg="#374151",

    wraplength=600

)

file_label.pack(pady=12)

def show_operation_report(module, action, source_path, output_path, extra=""):

    """Show a clear success report after a completed operation."""

    record_operation(module, action)

    report = (

        f"{action} completed successfully!\n\n"

        f"Module: {module}\n"

        f"Original file: {os.path.basename(source_path)}\n"

        f"Output file: {os.path.basename(output_path)}\n"

        f"Saved location: {output_path}\n"

    )

    if extra:

        report += f"\n{extra}"

    messagebox.showinfo(f"{module} {action} Report", report, parent=window)

def encrypt_text():

    file_path = filedialog.askopenfilename(

        title="Select Text File",

        filetypes=[

            ("Text File", "*.txt")

        ]

    )

    if not file_path:

        return

    if not check_file_size(file_path, MAX_TEXT_SIZE, "Text"):

        return

    try:

        with open(file_path, "rb") as file:

            data = file.read()

        encrypted_data = cipher.encrypt(data)

        output_path = get_vault_path(

            os.path.splitext(os.path.basename(file_path))[0] + ".enc"

        )

        with open(output_path, "wb") as file:

            file.write(encrypted_data)

        # Display encrypted text in a separate window

        encrypted_window = tk.Toplevel(window)

        encrypted_window.transient(window)

        encrypted_window.lift()

        encrypted_window.focus_force()

        encrypted_window.title("🔐 Encrypted Text")

        encrypted_window.geometry("750x450")

        encrypted_window.configure(bg="#F4F7FB")

        tk.Label(

            encrypted_window,

            text="🔐 ENCRYPTED TEXT",

            font=("Arial", 16, "bold"),

            bg="#F4F7FB",

            fg="#172554"

        ).pack(pady=15)

        encrypted_box = tk.Text(

            encrypted_window,

            height=18,

            width=85,

            font=("Consolas", 10),

            wrap="word"

        )

        encrypted_box.pack(

            padx=20,

            pady=10,

            fill="both",

            expand=True

        )

        encrypted_box.insert(

            "1.0",

            encrypted_data.decode("utf-8")

        )

        encrypted_box.config(state="disabled")

        tk.Button(encrypted_window, text="CLOSE", command=encrypted_window.destroy, width=15, bg="#2563EB", fg="white", relief="flat", font=("Arial", 10, "bold"), cursor="hand2").pack(pady=10)

        file_label.config(

            text="✅ Text encrypted successfully!"

        )

        show_operation_report("Text", "Encryption", file_path, output_path, "Encrypted file stored in the hidden Secure Vault.")

    except Exception as error:

        messagebox.showerror(

            "Encryption Error",

            str(error)

        )

def decrypt_text():

    create_secure_vault()

    encrypted_path = filedialog.askopenfilename(

        title="Select Encrypted Text",

        initialdir=VAULT_FOLDER,

        filetypes=[

            ("Encrypted File", "*.enc")

        ]

    )

    if not encrypted_path:

        return

    try:

        with open(encrypted_path, "rb") as file:

            encrypted_data = file.read()

        decrypted_data = cipher.decrypt(encrypted_data)

        output_path = filedialog.asksaveasfilename(

            title="Save Decrypted Text",

            defaultextension=".txt",

            filetypes=[

                ("Text File", "*.txt")

            ]

        )

        if not output_path:

            return

        with open(output_path, "wb") as file:

            file.write(decrypted_data)

        decrypted_window = tk.Toplevel(window)

        decrypted_window.transient(window)

        decrypted_window.lift()

        decrypted_window.focus_force()

        decrypted_window.title("🔓 Decrypted Text")

        decrypted_window.geometry("750x450")

        decrypted_window.configure(bg="#F4F7FB")

        tk.Label(decrypted_window, text="🔓 DECRYPTED TEXT", font=("Arial", 16, "bold"), bg="#F4F7FB", fg="#166534").pack(pady=15)

        decrypted_box = tk.Text(decrypted_window, height=18, width=85, font=("Consolas", 10), wrap="word")

        decrypted_box.pack(padx=20, pady=10, fill="both", expand=True)

        decrypted_box.insert("1.0", decrypted_data.decode("utf-8"))

        decrypted_box.config(state="disabled")

        tk.Button(decrypted_window, text="CLOSE", command=decrypted_window.destroy, width=15, bg="#16A34A", fg="white", relief="flat", font=("Arial", 10, "bold"), cursor="hand2").pack(pady=10)

        file_label.config(

            text="✅ Text decrypted successfully!"

        )

        show_operation_report("Text", "Decryption", encrypted_path, output_path, "Original text file restored successfully.")

    except Exception:

        messagebox.showerror(

            "Decryption Error",

            "Invalid encrypted file or encryption key."

        )

def show_file_details(title, file_path, file_type, extra=""):

    try:

        size_mb = os.path.getsize(file_path) / (1024 * 1024)

        details_window = tk.Toplevel(window)

        details_window.transient(window)

        details_window.lift()

        details_window.focus_force()

        details_window.title(title)

        details_window.geometry("700x450")

        details_window.configure(bg="#F4F7FB")

        tk.Label(

            details_window, text=title, font=("Arial", 16, "bold"),

            bg="#F4F7FB", fg="#172554"

        ).pack(pady=15)

        info = (

            f"File type: {file_type}\n"

            f"File: {os.path.basename(file_path)}\n"

            f"Size: {size_mb:.2f} MB\n"

            f"Path: {file_path}\n\n"

            f"{extra}"

        )

        box = tk.Text(

            details_window, height=12, width=78,

            font=("Consolas", 10), wrap="word"

        )

        box.pack(padx=20, pady=10, fill="both", expand=True)

        box.insert("1.0", info)

        box.config(state="disabled")

        tk.Button(

            details_window, text="Close", command=details_window.destroy,

            width=15, bg="#2563EB", fg="white", relief="flat",

            font=("Arial", 10, "bold")

        ).pack(pady=10)

    except Exception as error:

        messagebox.showerror("Display Error", str(error))

def create_encrypted_preview(encrypted_data):

    import math

    # Use only a limited amount of encrypted data for preview

    data = encrypted_data[:2000000]

    # Convert bytes into RGB values

    remainder = len(data) % 3

    if remainder:

        data += b"\x00" * (3 - remainder)

    pixels = len(data) // 3

    width = max(1, int(math.sqrt(pixels)))

    height = math.ceil(pixels / width)

    required = width * height * 3

    if len(data) < required:

        data += b"\x00" * (required - len(data))

    image = Image.frombytes(

        "RGB",

        (width, height),

        data[:required]

    )

    image.thumbnail((700, 520))

    return image

def show_image_preview(title, file_path):

    try:

        preview_window = tk.Toplevel(window)

        preview_window.transient(window)

        preview_window.lift()

        preview_window.focus_force()

        preview_window.title(title)

        preview_window.geometry("800x650")

        preview_window.configure(bg="#F4F7FB")

        tk.Label(

            preview_window, text=title, font=("Arial", 16, "bold"),

            bg="#F4F7FB", fg="#172554"

        ).pack(pady=10)

        image = Image.open(file_path)

        image.thumbnail((700, 520))

        photo = ImageTk.PhotoImage(image)

        label = tk.Label(preview_window, image=photo, bg="#F4F7FB")

        label.image = photo

        label.pack(padx=20, pady=10)

        tk.Label(

            preview_window, text=os.path.basename(file_path),

            font=("Arial", 9), bg="#F4F7FB", fg="#64748B"

        ).pack(pady=5)

        tk.Button(preview_window, text="CLOSE", command=preview_window.destroy, width=15, bg="#2563EB", fg="white", relief="flat", font=("Arial", 10, "bold"), cursor="hand2").pack(pady=8)

    except Exception as error:

        messagebox.showerror("Image Display Error", str(error))

def open_media_file(file_path):

    try:

        os.startfile(file_path)

    except Exception as error:

        messagebox.showerror("Open File Error", str(error))

def encrypt_image():

    file_path = filedialog.askopenfilename(

        title="Select JPG Image",

        filetypes=[

            ("JPG Image", "*.jpg")

        ]

    )

    if not file_path:

        return

    if not check_file_size(file_path, MAX_IMAGE_SIZE, "Image"):

        return

    try:

        # Calculate SHA-256 hash of original image

        original_hash = calculate_sha256(file_path)

        # Read image

        with open(file_path, "rb") as file:

            data = file.read()

        # Encrypt image

        encrypted_data = cipher.encrypt(data)

        # Select save location

        output_path = get_vault_path(

            os.path.splitext(os.path.basename(file_path))[0] + ".enc"

        )

        # Save encrypted image

        with open(output_path, "wb") as file:

            file.write(encrypted_data)

        # Save original SHA-256 hash

        hash_path = output_path + ".hash"

        with open(hash_path, "w") as hash_file:

            hash_file.write(original_hash)

        show_image_preview("🖼️ ORIGINAL IMAGE - ENCRYPTED", file_path)

        show_file_details(

            "🔐 ENCRYPTED IMAGE DETAILS", output_path, "Encrypted JPG (.enc)",

            "The encrypted file cannot be displayed as a normal image because encryption changes the image data."

        )

        file_label.config(

            text="✅ Image encrypted successfully!"

        )

        show_operation_report("Image", "Encryption", file_path, output_path, "Encrypted file and SHA-256 hash stored in the hidden Secure Vault.")

    except Exception as error:

        messagebox.showerror(

            "Encryption Error",

            str(error)

        )

def decrypt_image():

    create_secure_vault()

    encrypted_path = filedialog.askopenfilename(

        title="Select Encrypted Image",

        initialdir=VAULT_FOLDER,

        filetypes=[

            ("Encrypted File", "*.enc")

        ]

    )

    if not encrypted_path:

        return

    try:

        # Read encrypted image

        with open(encrypted_path, "rb") as file:

            encrypted_data = file.read()

        # Decrypt image

        decrypted_data = cipher.decrypt(encrypted_data)

        # Select save location

        output_path = filedialog.asksaveasfilename(

            title="Save Decrypted Image",

            defaultextension=".jpg",

            filetypes=[

                ("JPG Image", "*.jpg")

            ]

        )

        if not output_path:

            return

        # Save decrypted image

        with open(output_path, "wb") as file:

            file.write(decrypted_data)

        record_operation("Image", "Decryption")

        show_image_preview("🔓 DECRYPTED IMAGE", output_path)

        # Calculate SHA-256 of decrypted image

        decrypted_hash = calculate_sha256(output_path)

        # Original hash file

        hash_path = encrypted_path + ".hash"

        if os.path.exists(hash_path):

            with open(hash_path, "r") as hash_file:

                original_hash = hash_file.read().strip()

            # Compare original and decrypted hash

            if hmac.compare_digest(original_hash, decrypted_hash):

                integrity_message = (

                    "✅ Image decrypted successfully!\n\n"

                    "🛡️ SHA-256 Integrity Verified\n\n"

                    "Original and decrypted files are identical."

                )

            else:

                integrity_message = (

                    "⚠️ Image decrypted, but integrity check failed!\n\n"

                    "The decrypted file does not match the original."

                )

        else:

            integrity_message = (

                "✅ Image decrypted successfully!\n\n"

                "⚠️ SHA-256 hash file not found."

            )

        file_label.config(

            text="✅ Image decrypted + integrity checked!"

        )

        messagebox.showinfo("Image Decryption Report", integrity_message + f"\n\nRestored file: {output_path}", parent=window)

    except Exception:

        messagebox.showerror(

            "Decryption Error",

            "Invalid encrypted file or encryption key."

        )

def encrypt_audio():

    file_path = filedialog.askopenfilename(

        title="Select MP3 Audio",

        filetypes=[

            ("MP3 Audio", "*.mp3")

        ]

    )

    if not file_path:

        return

    if not check_file_size(file_path, MAX_AUDIO_SIZE, "Audio"):

        return

    try:

        with open(file_path, "rb") as file:

            data = file.read()

        encrypted_data = cipher.encrypt(data)

        output_path = get_vault_path(

            os.path.splitext(os.path.basename(file_path))[0] + ".enc"

        )

        with open(output_path, "wb") as file:

            file.write(encrypted_data)

        show_file_details(

            "🔐 ENCRYPTED AUDIO", output_path, "Encrypted MP3 (.enc)",

            "Encrypted audio cannot be played directly. It must be decrypted first."

        )

        file_label.config(

            text="✅ Audio encrypted successfully!"

        )

        show_operation_report("Audio", "Encryption", file_path, output_path, "Encrypted file stored in the hidden Secure Vault.")

    except Exception as error:

        messagebox.showerror(

            "Encryption Error",

            str(error)

        )

def decrypt_audio():

    create_secure_vault()

    encrypted_path = filedialog.askopenfilename(

        title="Select Encrypted Audio",

        initialdir=VAULT_FOLDER,

        filetypes=[

            ("Encrypted File", "*.enc")

        ]

    )

    if not encrypted_path:

        return

    try:

        with open(encrypted_path, "rb") as file:

            encrypted_data = file.read()

        decrypted_data = cipher.decrypt(encrypted_data)

        output_path = filedialog.asksaveasfilename(

            title="Save Decrypted Audio",

            defaultextension=".mp3",

            filetypes=[

                ("MP3 Audio", "*.mp3")

            ]

        )

        if not output_path:

            return

        with open(output_path, "wb") as file:

            file.write(decrypted_data)

        show_file_details(

            "🔓 DECRYPTED AUDIO", output_path, "MP3 Audio (.mp3)",

            "Decryption completed successfully. The original MP3 file is restored and can be opened with your default media player."

        )

        file_label.config(

            text="✅ Audio decrypted successfully!"

        )

        show_operation_report("Audio", "Decryption", encrypted_path, output_path, "Original MP3 file restored successfully.")

    except Exception:

        messagebox.showerror(

            "Decryption Error",

            "Invalid encrypted file or encryption key."

        )

# ==========================================

# VIDEO ENCRYPTION

# ==========================================

def encrypt_video():

    file_path = filedialog.askopenfilename(

        title="Select MP4 Video",

        filetypes=[

            ("MP4 Video", "*.mp4")

        ]

    )

    if not file_path:

        return

    if not check_file_size(file_path, MAX_VIDEO_SIZE, "Video"):

        return

    try:

        with open(file_path, "rb") as file:

            data = file.read()

        encrypted_data = cipher.encrypt(data)

        output_path = get_vault_path(

            os.path.splitext(os.path.basename(file_path))[0] + ".enc"

        )

        with open(output_path, "wb") as file:

            file.write(encrypted_data)

        show_file_details(

            "🔐 ENCRYPTED VIDEO", output_path, "Encrypted MP4 (.enc)",

            "Encrypted video cannot be played directly. It must be decrypted first."

        )

        file_label.config(

            text="✅ Video encrypted successfully!"

        )

        show_operation_report("Video", "Encryption", file_path, output_path, "Encrypted file stored in the hidden Secure Vault.")

    except Exception as error:

        messagebox.showerror(

            "Encryption Error",

            str(error)

        )

def decrypt_video():

    create_secure_vault()

    encrypted_path = filedialog.askopenfilename(

        title="Select Encrypted Video",

        initialdir=VAULT_FOLDER,

        filetypes=[

            ("Encrypted File", "*.enc")

        ]

    )

    if not encrypted_path:

        return

    try:

        with open(encrypted_path, "rb") as file:

            encrypted_data = file.read()

        decrypted_data = cipher.decrypt(encrypted_data)

        output_path = filedialog.asksaveasfilename(

            title="Save Decrypted Video",

            defaultextension=".mp4",

            filetypes=[

                ("MP4 Video", "*.mp4")

            ]

        )

        if not output_path:

            return

        with open(output_path, "wb") as file:

            file.write(decrypted_data)

        show_file_details(

            "🔓 DECRYPTED VIDEO", output_path, "MP4 Video (.mp4)",

            "Decryption completed successfully. The original MP4 file is restored and can be opened with your default media player."

        )

        file_label.config(

            text="✅ Video decrypted successfully!"

        )

        show_operation_report("Video", "Decryption", encrypted_path, output_path, "Original MP4 file restored successfully.")

    except Exception:

        messagebox.showerror(

            "Decryption Error",

            "Invalid encrypted file or encryption key."

        )

# ==========================================

# OPERATIONS BAR GRAPH

# ==========================================

def show_dashboard_graph():

    stats = load_operation_stats()

    graph_window = tk.Toplevel(window)

    graph_window.title("SecureVault - Operations Dashboard")

    graph_window.geometry("860x570")

    graph_window.configure(bg="#F3F0FF")

    graph_window.transient(window)

    tk.Label(

        graph_window, text="📊 OPERATIONS BY MODULE",

        font=("Arial", 20, "bold"), bg="#F3F0FF", fg="#25204A"

    ).pack(pady=(18, 4))

    tk.Label(

        graph_window,

        text="Compare successful encryption and decryption operations",

        font=("Arial", 10), bg="#F3F0FF", fg="#77738F"

    ).pack(pady=(0, 14))

    total_enc = sum(stats[m]["Encryption"] for m in MODULE_NAMES)

    total_dec = sum(stats[m]["Decryption"] for m in MODULE_NAMES)

    summary = tk.Frame(graph_window, bg="#F3F0FF")

    summary.pack(fill="x", padx=25, pady=(0, 8))

    tk.Label(

        summary, text=f"🔒  Total Encryptions: {total_enc}",

        font=("Arial", 11, "bold"), bg="#EEE9FF", fg="#5B43C5",

        padx=12, pady=11

    ).pack(side="left", expand=True, fill="x", padx=5)

    tk.Label(

        summary, text=f"🔓  Total Decryptions: {total_dec}",

        font=("Arial", 11, "bold"), bg="#E5F7EF", fg="#167653",

        padx=12, pady=11

    ).pack(side="left", expand=True, fill="x", padx=5)

    chart = tk.Canvas(

        graph_window, bg="white", height=350,

        highlightthickness=1, highlightbackground="#E8E3F5"

    )

    chart.pack(fill="both", expand=True, padx=25, pady=10)

    chart.update_idletasks()

    width = max(chart.winfo_width(), 790)

    height = max(chart.winfo_height(), 330)

    left, right, top, bottom = 62, width - 25, 25, height - 52

    plot_height = bottom - top

    max_value = max(

        [stats[m][a] for m in MODULE_NAMES for a in ("Encryption", "Decryption")] + [1]

    )

    scale_max = max(4, ((max_value + 3) // 4) * 4)

    chart.create_line(left, top, left, bottom, fill="#AAA5B8", width=2)

    chart.create_line(left, bottom, right, bottom, fill="#AAA5B8", width=2)

    for tick in range(5):

        value = int(scale_max * tick / 4)

        y = bottom - plot_height * tick / 4

        chart.create_line(left, y, right, y, fill="#EEEAF5")

        chart.create_text(left - 12, y, text=str(value), anchor="e",

                          fill="#77738F", font=("Arial", 9))

    group_width = (right - left) / len(MODULE_NAMES)

    bar_width = min(38, group_width * 0.22)

    for index, module in enumerate(MODULE_NAMES):

        center = left + group_width * (index + 0.5)

        bars = [

            (-bar_width / 2, "Encryption", "#7657E8"),

            (bar_width / 2, "Decryption", "#19A7A0")

        ]

        for offset, action, color in bars:

            count = stats[module][action]

            bar_height = (count / scale_max) * plot_height

            x1 = center + offset - bar_width * 0.42

            x2 = center + offset + bar_width * 0.42

            y1 = bottom - bar_height

            chart.create_rectangle(x1, y1, x2, bottom, fill=color, outline="")

            chart.create_text(

                (x1 + x2) / 2, max(top + 9, y1 - 11),

                text=str(count), fill="#39334F",

                font=("Arial", 9, "bold")

            )

        chart.create_text(center, bottom + 22, text=module,

                          fill="#39334F", font=("Arial", 10, "bold"))

    legend = tk.Frame(graph_window, bg="#F3F0FF")

    legend.pack(pady=(2, 8))

    tk.Label(legend, text="■ Encryption", bg="#F3F0FF",

             fg="#7657E8", font=("Arial", 10, "bold")).pack(side="left", padx=12)

    tk.Label(legend, text="■ Decryption", bg="#F3F0FF",

             fg="#19A7A0", font=("Arial", 10, "bold")).pack(side="left", padx=12)

    tk.Button(

        graph_window, text="CLOSE", command=graph_window.destroy,

        font=("Arial", 10, "bold"), bg="#7657E8", fg="white",

        activebackground="#6244D0", activeforeground="white",

        relief="flat", padx=28, pady=9, cursor="hand2"

    ).pack(pady=(0, 14))

# ==========================================

# MODERN SECUREVAULT DASHBOARD

# ==========================================

for old_widget in (title_label, subtitle_label):

    old_widget.destroy()

# Keep file_label alive because encryption/decryption functions update it.

# Hide it from the redesigned dashboard instead of destroying it.

file_label.pack_forget()

window.title("SecureVault - Multimedia Cryptography")

window.configure(bg="#F3F0FF")

window.attributes("-fullscreen", True)

window.bind("<Escape>", lambda event: window.attributes("-fullscreen", False))

COLORS = {

    "bg": "#F3F0FF", "panel": "#FFFFFF", "ink": "#25204A",

    "muted": "#77738F", "purple": "#7657E8", "blue": "#3987E8",

    "pink": "#E65C9C", "teal": "#19A7A0", "green": "#159B72",

    "line": "#E8E3F5"

}

button_font = ("Arial", 10, "bold")

main = tk.Frame(window, bg=COLORS["bg"])

main.pack(fill="both", expand=True, padx=34, pady=20)

header = tk.Frame(main, bg=COLORS["bg"])

header.pack(fill="x", pady=(0, 14))

brand = tk.Frame(header, bg=COLORS["bg"])

brand.pack(side="left", anchor="w")

tk.Label(brand, text="🔐", font=("Segoe UI Emoji", 30),

         bg=COLORS["bg"], fg=COLORS["purple"]).pack(side="left", padx=(0, 12))

tk.Label(brand, text="SECUREVAULT", font=("Arial", 24, "bold"),

         bg=COLORS["bg"], fg=COLORS["ink"]).pack(anchor="w")

tk.Label(brand, text="Your personal multimedia protection space",

         font=("Arial", 10), bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w")

tk.Button(

    header, text="📊  VIEW DASHBOARD", command=show_dashboard_graph,

    font=button_font, bg="#E5F7EF", fg="#167653",

    activebackground="#D2F0E3", activeforeground="#116044",

    relief="flat", bd=0, padx=16, pady=12, cursor="hand2"

).pack(side="right", anchor="center", pady=10, padx=(0, 8))


welcome = tk.Frame(main, bg="#EAE4FF", highlightthickness=1,

                   highlightbackground="#DCD2FF")

welcome.pack(fill="x", pady=(0, 15))

tk.Label(welcome, text="✨  Secure your files with one simple workspace",

         font=("Arial", 13, "bold"), bg="#EAE4FF", fg="#4936A4"

         ).pack(anchor="w", padx=18, pady=(12, 3))

tk.Label(welcome,

         text="Choose a module below. Encrypt files into your hidden vault, then decrypt them whenever needed.",

         font=("Arial", 9), bg="#EAE4FF", fg="#625A85"

         ).pack(anchor="w", padx=18, pady=(0, 12))

section_head = tk.Frame(main, bg=COLORS["bg"])

section_head.pack(fill="x", pady=(0, 8))

tk.Label(section_head, text="SENDER  /  ENCRYPT FILES",

         font=("Arial", 12, "bold"), bg=COLORS["bg"],

         fg=COLORS["ink"]).pack(side="left")

tk.Label(section_head, text="4 supported types", font=("Arial", 9),

         bg=COLORS["bg"], fg=COLORS["muted"]).pack(side="right")

cards_area = tk.Frame(main, bg=COLORS["bg"])

cards_area.pack(fill="both", expand=True)

modules = [

    ("📝", "TEXT", "TXT documents", "#EEE9FF", "#7657E8", encrypt_text, decrypt_text),

    ("🖼️", "IMAGE", "JPG photographs", "#E5F1FF", "#3987E8", encrypt_image, decrypt_image),

    ("🎵", "AUDIO", "MP3 audio files", "#FFEAF3", "#D94F91", encrypt_audio, decrypt_audio),

    ("🎬", "VIDEO", "MP4 video files", "#E2F8F5", "#159B91", encrypt_video, decrypt_video),

]

for index, (icon, name, desc, tint, accent, enc_func, dec_func) in enumerate(modules):

    row, col = divmod(index, 2)

    card = tk.Frame(cards_area, bg=COLORS["panel"], highlightthickness=1,

                    highlightbackground=COLORS["line"])

    card.grid(row=row, column=col, sticky="nsew", padx=8, pady=7)

    cards_area.grid_columnconfigure(col, weight=1, uniform="module")

    cards_area.grid_rowconfigure(row, weight=1, uniform="module")

    top = tk.Frame(card, bg=COLORS["panel"])

    top.pack(fill="x", padx=16, pady=(13, 8))

    tk.Label(top, text=icon, font=("Segoe UI Emoji", 22),

             bg=tint, fg=accent, width=3, height=1

             ).pack(side="left", padx=(0, 12))

    details = tk.Frame(top, bg=COLORS["panel"])

    details.pack(side="left", anchor="center")

    tk.Label(details, text=name, font=("Arial", 13, "bold"),

             bg=COLORS["panel"], fg=COLORS["ink"]).pack(anchor="w")

    tk.Label(details, text=desc, font=("Arial", 9),

             bg=COLORS["panel"], fg=COLORS["muted"]).pack(anchor="w")

    actions = tk.Frame(card, bg=COLORS["panel"])

    actions.pack(fill="x", padx=16, pady=(2, 14))

    tk.Button(actions, text="🔒  ENCRYPT", command=enc_func,

              font=button_font, bg=accent, fg="white",

              activebackground=accent, activeforeground="white",

              relief="flat", bd=0, cursor="hand2", padx=12, pady=9

              ).pack(side="left", fill="x", expand=True, padx=(0, 6))

    tk.Button(actions, text="🔓  DECRYPT", command=dec_func,

              font=button_font, bg="#F0F2F8", fg=COLORS["ink"],

              activebackground="#E4E7F0", activeforeground=COLORS["ink"],

              relief="flat", bd=0, cursor="hand2", padx=12, pady=9

              ).pack(side="left", fill="x", expand=True, padx=(6, 0))

receiver = tk.Frame(main, bg="#E5F7EF", highlightthickness=1,

                    highlightbackground="#C8EBDD")

receiver.pack(fill="x", padx=8, pady=(8, 5))

tk.Label(receiver, text="👤  RECEIVER  •  RESTORE YOUR FILES",

         font=("Arial", 11, "bold"), bg="#E5F7EF", fg="#167653"

         ).pack(anchor="w", padx=16, pady=(10, 2))

tk.Label(receiver,

         text="Use any DECRYPT button above, choose the encrypted .enc file from the vault, and save the restored original file.",

         font=("Arial", 9), bg="#E5F7EF", fg="#4C7969",

         wraplength=1000).pack(anchor="w", padx=16, pady=(0, 10))

footer = tk.Frame(main, bg=COLORS["bg"])

footer.pack(fill="x", padx=8, pady=(5, 0))

tk.Label(footer,

         text="🛡️  Fernet encryption  •  SHA-256 image integrity  •  Local hidden storage",

         font=("Arial", 9), bg=COLORS["bg"], fg=COLORS["muted"]

         ).pack(side="left")

tk.Label(footer, text="SECUREVAULT  |  PRIVACY FIRST",

         font=("Arial", 8, "bold"), bg=COLORS["bg"],

         fg=COLORS["purple"]).pack(side="right")

# ==========================================

window.mainloop()
