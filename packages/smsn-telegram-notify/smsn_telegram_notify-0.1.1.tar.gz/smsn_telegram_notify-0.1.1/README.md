# smsn_telegram_notify

ไลบรารี Python สำหรับส่งข้อความ รูปภาพ ไฟล์ หรือวิดีโอไปยัง Telegram ได้อย่างรวดเร็ว

## การติดตั้ง

ติดตั้งจาก PyPI:

```bash
pip install smsn-telegram-notify
```

ติดตั้งจากซอร์สโค้ดในเครื่อง:

```bash
pip install .
```

## เริ่มต้นใช้งาน

```python
from smsn_telegram_notify import TelegramNotify

# อ่านค่าจากไฟล์ config.toml
notifier = TelegramNotify(config_path="config.toml")

# หรือกำหนด token และ chat_id โดยตรง
notifier = TelegramNotify(token="YOUR_TOKEN", chat_id="CHAT_ID")
```

ตัวอย่างสคริปต์แบบง่ายในการส่งข้อความหนึ่งครั้ง:

```python
from smsn_telegram_notify import TelegramNotify
import time

if __name__ == "__main__":
    notifier = TelegramNotify(config_path="config.toml")
    notifier.start_send_text("Hello, World")
    time.sleep(2)  # รอให้คิวส่งเสร็จก่อนปิดโปรแกรม
```

ตัวอย่างไฟล์ `config.toml`:

```toml
[smsn_telegram_notify]
token = "123456:ABCDEFG"
chat_id = "-100123456"
notify_interval_sec = 60
```

## การหา Chat ID

หากยังไม่ทราบ `chat_id` ของกลุ่ม สามารถใช้สคริปต์ `get_chat_id.py` ในโปรเจกต์ได้ดังนี้:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_TOKEN"
python get_chat_id.py
```

สคริปต์จะพิมพ์ชื่อกลุ่มและ `chat_id` ที่พบจากข้อมูล `getUpdates` ของบอท

> ฟังก์ชันที่เกี่ยวข้องกับภาพหรือวิดีโอจำเป็นต้องติดตั้ง `opencv-python` เพิ่มเติม

## Public Send Methods
เมทอดทั้งหมดเป็น **non-blocking** และมีตัวเลือก `time_interval` เพื่อกำหนดช่วงเวลาขั้นต่ำระหว่างการส่ง (ค่าเริ่มต้น 5 วินาที หรือค่าจาก `notify_interval_sec`).

### `start_send_text(msg, time_interval=None)`
ส่งข้อความตัวอักษรธรรมดา

```python
import time
notifier.start_send_text("hello")
time.sleep(3)          # เมทอดนี้ทำงานแบบไม่รอผล จึงควรรอให้คิวส่งเสร็จก่อนปิดโปรแกรม
# หรือ notifier.send_queue.join()

# หากต้องการส่งแบบ synchronous
notifier.tg_send_text("hello")
```

### `start_send_image(msg, image, time_interval=None)`
ส่งรูปภาพจากอ็อบเจ็กต์ภาพของ OpenCV

```python
import cv2
img = cv2.imread("test.jpg")
notifier.start_send_image("รูปทดสอบ", img)
```

### `start_bytes_send_file(msg, bytes_data, time_interval=None)`
ส่งไฟล์จากข้อมูลแบบไบต์โดยตรง

```python
with open("report.pdf", "rb") as f:
    data = f.read()
notifier.start_bytes_send_file("ส่งจาก bytes", data)
```

### `start_frame_send_file(msg, frame, time_interval=None)`
ส่งเฟรมภาพ (เช่น เฟรมจากกล้อง)

```python
frame = cv2.imread("frame.jpg")
notifier.start_frame_send_file("ส่งเฟรม", frame)
```

### `start_send_file(msg, path_file, time_interval=None)`
ส่งไฟล์จากพาธบนดิสก์

```python
notifier.start_send_file("ส่งไฟล์", "document.txt")
```

### `start_send_video(msg, path_file, time_interval=None)`
ส่งวิดีโอจากพาธบนดิสก์

```python
notifier.start_send_video("ส่งวิดีโอ", "clip.mp4")
```

## การทดสอบ

ใช้ `pytest` เพื่อรันชุดการทดสอบของโปรเจกต์

```bash
pytest
```
