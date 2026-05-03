# 🚦 Traffic AI - YOLOv8 CCTV Monitoring

Real-time traffic monitoring system using **YOLOv8** and **CCTV streaming API** to detect and count vehicles.

---

## ✨ Features

* 🚗 Vehicle detection (car, motor, bus, truck)
* 📊 Real-time vehicle counting
* 🎯 Noise filtering & smoothing
* 📡 Live CCTV stream (.m3u8)
* ⚡ Fast and lightweight processing

---

## 🧠 Tech Stack

* Python
* YOLOv8 (Ultralytics)
* OpenCV
* CCTV API (Kudus)

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/USERNAME/REPO_NAME.git
cd REPO_NAME
```

---

### 2. Install Dependencies

**Cara biasa:**

```bash
pip install ultralytics opencv-python requests
```

**Jika terjadi error, gunakan:**

```bash
python -m pip install ultralytics opencv-python requests
```

💡 Catatan:

* Disarankan menggunakan Python 3.9 – 3.11
* Gunakan virtual environment jika perlu:

```bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac
```

---

### 3. (Optional) Install FFmpeg

Agar stream `.m3u8` berjalan lancar:

**Linux**

```bash
sudo apt install ffmpeg
```

**Windows**

* Install FFmpeg
* Tambahkan ke PATH

---

## ▶️ Run Project

```bash
python main.py
```

---

## 📡 CCTV Source

Contoh stream:

```
https://stream.kuduskab.go.id/memfs/8d4f74b4-28e2-409c-9593-525c3d594bc4.m3u8
```

Atau ambil dari API:

```
https://kudussehat.kuduskab.go.id/api/get-cctv
```

---

## 🧪 API Testing

API dapat diuji menggunakan:

* Bruno (recommended)
* Postman
* Insomnia
* Curl

### Header

```
X-SDC: sdsi72392knqw2hhuhsi21380sdisidSHSIAbA12bhsjk23Sndj
```

---

## 📌 Notes

* Gunakan stream `.m3u8` (bukan YouTube)
* Pastikan koneksi internet stabil
* Beberapa kamera mungkin offline

---

## 🚀 Future Improvements

* Multi-camera detection
* Traffic congestion analysis
* Real-time dashboard
* Smart city integration

---
