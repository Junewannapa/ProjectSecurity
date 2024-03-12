import cv2
import numpy as np
import subprocess
import os
from tqdm import tqdm
import wave
import subprocess
import sys

# กำหนดค่าของ encryption
if not os.path.exists("enc"): os.mkdir("enc") 
if not os.path.exists("out"): os.mkdir("out") 

# ใส่วิดีโอคลิปหลักและคลิปที่จะซ่อน
# cover_path = "v1.mp4"
# secret_path = "v2.mp4"
cover_path = sys.argv[1]  
secret_path = sys.argv[2]
fn = 0

# -- ปรับขนาด -- #
def resize(src, w=None, h=None, ar=None):


    if w is not None and h is not None:
        return cv2.resize(src, (w, h))
    assert(ar != None)
    if w is not None:
        return cv2.resize(src, (w, int(w/ar)))
    if h is not None:
        return cv2.resize(src, (int(h*ar), h))

# ใช้ OpenCV เพื่อดึงข้อมูลของวิดีโอจากไฟล์ ทั้ง 2
src = cv2.VideoCapture(cover_path)
src_w = int(src.get(3))
src_h = int(src.get(4))
src_fps = src.get(cv2.CAP_PROP_FPS)
src_frame_cnt = src.get(cv2.CAP_PROP_FRAME_COUNT)

sec = cv2.VideoCapture(secret_path)
sec_w = int(sec.get(3))
sec_h = int(sec.get(4))
sec_fps = sec.get(cv2.CAP_PROP_FPS)
sec_frame_cnt = sec.get(cv2.CAP_PROP_FRAME_COUNT)

if src_frame_cnt < sec_frame_cnt:
    print("เลือกวิดีโอหน้าปกที่มีระยะเวลานานกว่าวิดีโอลับ")
    exit()

# ทำงานกับเสียง
sec_duration = sec_frame_cnt/sec_fps
subprocess.call(f"ffmpeg -ss 0 -t {sec_duration} -i {cover_path} enc/cvr.wav", shell=True)
subprocess.call(f"ffmpeg -ss 0 -t {sec_duration} -i {secret_path} enc/scr.wav", shell=True)

# encoding เสียง
with wave.open("enc/enc.wav", 'wb') as e:
    s = wave.open("enc/scr.wav", 'rb')
    c = wave.open("enc/cvr.wav", 'rb')
    s_frames = np.array(list(s.readframes(s.getnframes())), dtype='uint8')
    c_frames = np.array(list(c.readframes(c.getnframes())), dtype='uint8')

    # ทำให้กรอบเหมือนกัน
    if s_frames.shape[0] > c_frames.shape[0]:
        c_frames = np.concatenate((c_frames, np.zeros((s_frames.shape[0] - c_frames.shape[0],), dtype='uint8')), axis=0)
    elif s_frames.shape[0] < c_frames.shape[0]:
        s_frames = np.concatenate((s_frames, np.zeros((c_frames.shape[0] - s_frames.shape[0],), dtype='uint8')), axis=0)

    # encoding เสียง
    enc_frames = (c_frames & 0b11110000) | (s_frames & 0b11110000) >> 4

    e.setparams(s.getparams())
    e.writeframes(np.ndarray.tobytes(enc_frames))

    s.close()
    c.close()

# สร้างแถบความคืบหน้า
pbar = tqdm(total=sec_frame_cnt*2, unit='frames')

while(1):
    _, src_frame = src.read()
    ret, sec_frame = sec.read()

    if src_frame is None or sec_frame is None:
        print("Reached end of one of the videos.")
        break
    
    # รับอัตราส่วนภาพ
    src_ar = src_w/src_h
    sec_ar = sec_w/sec_h

    # ใส่กรอบครอบได้พอดี
    if src_ar == sec_ar and src_frame.shape < sec_frame.shape:
        sec_frame = resize(sec_frame, src_w, src_h)
    elif src_ar != sec_ar and (src_w < sec_w or src_h < sec_h):
        if sec_w>sec_h:
            sec_frame = resize(sec_frame, w=src_w, ar=sec_ar)
            if sec_frame.shape[0]>src_h:
                sec_frame = resize(sec_frame, h=src_h, ar=sec_ar)
        else:
            sec_frame = resize(sec_frame, h=src_h, ar=sec_ar)
            if sec_frame.shape[1]>src_w:
                sec_frame = resize(sec_frame, w=src_w, ar=sec_ar)

    
    sec_frame = cv2.hconcat([sec_frame, np.zeros((sec_frame.shape[0], src_w-sec_frame.shape[1], 3), dtype='uint8')])
    sec_frame = cv2.vconcat([sec_frame, np.zeros((src_h-sec_frame.shape[0], sec_frame.shape[1], 3), dtype='uint8')])

    # encryption สำหรับน้อยกว่า 2 บิต
    encrypted_img = (src_frame&0b11111100)|(sec_frame>>4&0b00000011)
    fn = fn + 1
    cv2.imwrite("enc/{}.png".format(fn), encrypted_img)

    #  encryption บิตที่ 3 และ 4 
    encrypted_img = (src_frame&0b11111100)|(sec_frame>>6)
    fn = fn + 1
    cv2.imwrite("enc/{}.png".format(fn), encrypted_img)

    pbar.update(2)
    
    if ret == False:
	    break
    
 
pbar.close()

src.release()
sec.release()

# ลบวิดีโอที่เข้ารหัส ถ้ามีอยู่แล้ว
if os.path.exists("out/covered.mkv"): subprocess.call("rm -r out/covered.mkv", shell=True)

# บันทึกวิดีโอโดยใช้ ffmpeg 
# เพิ่มสองเท่าของอัตราเฟรมเพื่อรักษาความเร็วของวิดีโอหลัก
save_vid = "ffmpeg -framerate {} -i enc/%d.png -i enc/enc.wav -c:v copy -c:a copy out/covered.mkv".format(src_fps * 2)
subprocess.call(save_vid, shell=True)

# ลบวิดีโอที่เข้ารหัส ถ้ามีอยู่แล้ว
if os.path.exists("out/covered.mp4"):
    subprocess.call("rm -r out/covered.mp4", shell=True)

# บันทึกวิดีโอโดยใช้ ffmpeg 
# เพิ่มสองเท่าของอัตราเฟรมเพื่อรักษาความเร็วของวิดีโอหลัก
save_vid = "ffmpeg -framerate {} -i enc/%d.png -i enc/enc.wav -c:v libx264 -c:a aac -strict experimental -b:a 192k out/covered.mp4".format(src_fps * 2)
subprocess.call(save_vid, shell=True)

# ลบโฟเดอร์ลำดับภาพชั่วคราว enc
subprocess.call("rm -r enc", shell=True)
