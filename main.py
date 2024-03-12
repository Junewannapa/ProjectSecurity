import subprocess
import sys
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import shutil
import cv2

cover_path = ""
secret_path = ""
enc_path = "out/covered.mkv"

def select_cover_video():
    global cover_path
    cover_path = filedialog.askopenfilename(title="Select Cover Video")
    update_cover_label()

def select_secret_video():
    global secret_path
    secret_path = filedialog.askopenfilename(title="Select Secret Video")
    update_secret_label()

def update_cover_label():
    cover_label.config(text=f"วิดีโอหลัก... {os.path.basename(cover_path)}")

def update_secret_label():
    secret_label.config(text=f"วิดีโอลับ... {os.path.basename(secret_path)}")


def encrypt():
    global src_frame_cnt, sec_frame_cnt

    if cover_path and secret_path:
        # เรียกโปรแกรมหลักที่ทำการเข้ารหัส
        encrypt_process = subprocess.Popen([sys.executable, "encrypt.py", cover_path, secret_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        progress_label = tk.Label(encrypt_frame, text="Encrypting...", fg="white")
        progress_label.pack(pady=5)

        progress_bar = ttk.Progressbar(encrypt_frame, orient="horizontal", length=300, mode="determinate")
        progress_bar.pack(pady=5)

        while True:
            output = encrypt_process.stdout.readline()
            if output == '' and encrypt_process.poll() is not None:
                break
            if output:
                try:
                    # แปลง output เป็นตัวเลข
                    progress_value = float(output.strip())
                    # ตั้งค่าค่าความคืบหน้าให้กับ progress bar
                    progress_bar["value"] = progress_value
                    # อัพเดท GUI
                    root.update_idletasks()
                except ValueError:
                    pass

        encrypt_process.communicate()

        # หลังจากที่เสร็จสิ้นการเข้ารหัส
        progress_label.destroy()
        progress_bar.destroy()

        src = cv2.VideoCapture(cover_path)
        src_frame_cnt = int(src.get(cv2.CAP_PROP_FRAME_COUNT))
        src.release()

        sec = cv2.VideoCapture(secret_path)
        sec_frame_cnt = int(sec.get(cv2.CAP_PROP_FRAME_COUNT))
        sec.release()

        # ตรวจสอบเงื่อนไขและแสดงผลตามที่ท่านต้องการ
        if src_frame_cnt < sec_frame_cnt:
            # แสดงข้อความผลลัพธ์ที่ GUI
            error_label = tk.Label(encrypt_frame, text="Error: The secret video must not be longer than the cover video.", font=("Helvetica", 12), fg="red")
            error_label.pack(pady=5)
            
        else:
            # แสดงข้อความผลลัพธ์ที่ GUI
            success_label = tk.Label(encrypt_frame, text="Encryption Successful", font=("Helvetica", 16), fg="green")
            success_label.pack(pady=10)


def decrypt():
    global enc_path
    if enc_path:
        # เรียกโปรแกรมหลักที่ทำการถอดรหัส
        decrypt_process = subprocess.Popen([sys.executable, "decrypt.py", enc_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        progress_label = tk.Label(decrypt_frame, text="Decrypting...")
        progress_label.pack(pady=5)

        progress_bar = ttk.Progressbar(decrypt_frame, orient="horizontal", length=300, mode="determinate")
        progress_bar.pack(pady=5)

        while True:
            output = decrypt_process.stdout.readline()
            if output == '' and decrypt_process.poll() is not None:
                break
            if output:
                try:
                    # แปลง output เป็นตัวเลข
                    progress_value = float(output.strip())
                    # ตั้งค่าค่าความคืบหน้าให้กับ progress bar
                    progress_bar["value"] = progress_value
                    # อัพเดท GUI
                    root.update_idletasks()
                except ValueError:
                    pass

        decrypt_process.communicate()

        # หลังจากที่เสร็จสิ้นการถอดรหัส
        progress_label.destroy()
        progress_bar.destroy()
     
        decryption_label = tk.Label(decrypt_frame, text="Decryption Successful", font=("Helvetica", 16), fg="green")
        decryption_label.pack(pady=10)

      

root = tk.Tk()
root.title("Video Encryption and Decryption")
root.geometry("800x600")

def reset_all():
    global cover_path, secret_path, enc_path
    cover_path = ""
    secret_path = ""
    enc_path = "out/covered.mkv"
    cover_label.config(text="")
    secret_label.config(text="")

label = tk.Label(root, text="Video Steganography", font=("Helvetica", 24))
label.pack(pady=10)


# สร้าง Frame สำหรับปุ่ม Select Cover Video
cover_frame = tk.Frame(root)
cover_frame.pack(pady=10)
cover_label = tk.Label(cover_frame, text="")
cover_label.pack(fill=tk.BOTH)
cover_button = tk.Button(cover_frame, text="Select Cover Video", command=select_cover_video)
cover_button.pack(fill=tk.BOTH)

# สร้าง Frame สำหรับปุ่ม Select Secret Video
secret_frame = tk.Frame(root)
secret_frame.pack(pady=10)
secret_label = tk.Label(secret_frame, text="")
secret_label.pack(fill=tk.BOTH)
secret_button = tk.Button(secret_frame, text="Select Secret Video", command=select_secret_video)
secret_button.pack(fill=tk.BOTH)

# สร้าง Frame สำหรับปุ่ม Encrypt
encrypt_frame = tk.Frame(root)
encrypt_frame.pack(side=tk.LEFT, padx=(150, 5), pady=10)
encrypt_button = tk.Button(encrypt_frame, text="Encrypt", command=encrypt, width=15)
encrypt_button.pack(fill=tk.BOTH)

# สร้าง Frame สำหรับปุ่ม Decrypt
decrypt_frame = tk.Frame(root)
decrypt_frame.pack(side=tk.RIGHT, padx=(5, 150), pady=10)
decrypt_button = tk.Button(decrypt_frame, text="Decrypt", command=decrypt, width=15)
decrypt_button.pack(fill=tk.BOTH)

refresh_button = tk.Button(root, text="Refresh", command=reset_all)
refresh_button.pack(side=tk.BOTTOM, pady=10)

def download_hidden_video(hidden_video_path):
    # สร้างไฟล์ที่จะให้ดาวน์โหลด
    download_path = os.path.join("out", os.path.basename(hidden_video_path))

    # คัดลอกไฟล์ที่ถูกซ่อนไปยังไฟล์ที่ให้ดาวน์โหลด
    subprocess.run(["cp", hidden_video_path, download_path])

    print(f"Hidden video downloaded to: {download_path}")

def show_hidden_video():
    hidden_video_path = os.path.join("out", "covered.mp4")

    # ตรวจสอบว่าไฟล์ถูกสร้างและมีอยู่จริง
    if os.path.exists(hidden_video_path):
        # แสดงชื่อไฟล์ที่ถูกสร้าง
        print(f"Hidden video file: {os.path.basename(hidden_video_path)}")


    else:
        # แสดงข้อความว่าไม่พบวิดีโอที่ถูกซ่อน
        print("Video reveal failed.")



# รันหน้า UI
root.mainloop()