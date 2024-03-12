import cv2 
import numpy as np 
import os
import subprocess
import wave
from tqdm import tqdm

# ตรวจสอบว่ามีไดเร็กทอรี out กับ enc มั้ย
if not os.path.exists("out"): os.mkdir("out")
if not os.path.exists("enc"): os.mkdir("enc")

# path ไปไฟล์ที่เข้ารหัส
enc_path = "out/covered.mkv"

# อ่านไฟล์วิดีโอที่เข้ารหัส
enc = cv2.VideoCapture(enc_path)
enc_w = int(enc.get(3))
enc_h = int(enc.get(4))
enc_fps = enc.get(cv2.CAP_PROP_FPS)
enc_frame_cnt = enc.get(cv2.CAP_PROP_FRAME_COUNT)

# ถอดรหัสวิดีโอลับที่ซ่อน
out = cv2.VideoWriter('enc/decrypted_secret.avi', cv2.VideoWriter_fourcc(*"MJPG"), enc_fps/2, (enc_w, enc_h))

# ส่วนนี้ทำงานกับเสียง
subprocess.call(f"ffmpeg -i {enc_path} enc/enc.wav", shell=True)

# decoding ไฟล์เสียง
with wave.open("enc/dec.wav", 'wb') as d:
    e = wave.open("enc/enc.wav", 'rb')
    e_frames = np.array(list(e.readframes(e.getnframes())), dtype='uint8')

    # ถอดรหัสเสียง
    dec_frames = (e_frames&0b00001111)<<4

    d.setparams(e.getparams())
    d.writeframes(np.ndarray.tobytes(dec_frames))

    e.close()


fn = 0

# สร้างแถบความคืบหน้า
pbar = tqdm(total=enc_frame_cnt, unit='frames')

while (1): 
   
    ret, frame = enc.read() 
  
    if ret == False:
        break

    fn = fn + 1

    # สำหรับ บิตที่ 3 และ 4 จะถูกแยกออกมา
    if (fn%2):
        decrypted_frame = (frame&0b00000011)<<4   
    else:
        decrypted_frame = decrypted_frame|(frame&0b00000011)<<6
        out.write(decrypted_frame)       
    
    pbar.update(1)

enc.release()
out.release()

# ลบวิดีโอที่ถอดรหัสแล้ว ถ้ามีอยู่แล้ว
if os.path.exists("out/secret_revealed2.mp4"): subprocess.call("rm -r out/secret_revealed.mp4", shell=True)

# บันทึกวิดีโอที่ซ่อนลงในไฟล์
save_vid = "ffmpeg -i enc/decrypted_secret.avi -i enc/dec.wav -c:v copy -c:a copy out/secret_revealed2.mp4"
subprocess.call(save_vid, shell=True)

# ลบโฟลเดอร์ชั่วคราว
subprocess.call("rm -r enc", shell=True)
