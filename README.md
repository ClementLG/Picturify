<h1 align="center">Picturify</h1>

<p align="center">
    <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/-Flask-grey?style=flat&logo=flask" alt="Flask">
    <img src="https://img.shields.io/badge/-Docker-grey?logo=docker" alt="Docker">
  <a href="https://github.com/ClementLG/Picturify/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/ClementLG/Picturify" alt="License">
  </a>
</p>

> **Analyze, understand, and purify your images.**

## 1. Project Overview

**Picturify** is a modern and secure web application dedicated to managing image metadata (EXIF). It enables users to visualize hidden data (GPS, Device, Dates), filter it using smart templates, or completely remove it for privacy.

Built with **Flask** and **Bulma**, it offers a premium, responsive glassmorphism UI with robust batch processing capabilities.

---

## 2. Key Features

### 🚀 Batch Processing (New!)
- **Drag & Drop:** Upload multiple images (up to 10) simultaneously.
- **Batch Grid:** View all uploaded images in a card grid with status indicators.
- **Global Actions:**
  - **Purify All:** Remove metadata from all images in one click.
  - **Apply Smart Templates:** Apply "Flickr Mode" or "Basic Clean" to the entire batch.
- **Individual Control:** Delete specific images from the batch dynamically.
- **Management:** Reset the session with "Start Over" or Download All as a ZIP.
- **Smart Privacy:** Prompt to immediately clean files from the server after downloading.

### 📊 Analysis & Dashboard ("Analyze" Mode)
- **Interactive Map:** Visualize GPS coordinates on a Leaflet map.
- **Metadata Viewer:** clear display of Device, Lens, Aperture, ISO, and Date.
- **Raw Data:** Access the full EXIF key-value pairings.

### 🛠️ Advanced Editing ("Understand & Edit" Mode)
- **Editor:** Modify Copyright, Artist, Description, and Software fields.
- **GPS Editor:** Set, Change, or Remove GPS location by clicking on the map.
- **Smart Templates:**
  - **Flickr Mode:** Keeps Title, Description, Artist, Copyright, GPS, and Technical stats.
  - **Copyright Only:** Strips everything except Copyright and Artist.
  - **Basic Clean:** Removes GPS and sensitive info but keeps technical data.

### 🛡️ Purification ("Purify" Mode)
- **Deep Clean:** Removes **all** metadata (EXIF, XMP, IPTC, Photoshop) by re-encoding the image.
- **Lossless Handling:** Prevents image degradation while ensuring files are scrubbed clean.

---

## 3. Configuration

Tune the application via `config.py` variables:

### Image Quality
- `IMAGE_QUALITY`: JPEG output quality (1-100). Default `100` (Max quality). Set to `85` for smaller files.
- `IMAGE_SUBSAMPLING`: Color sampling. `0` (4:4:4 Best), `2` (4:2:0 Standard).

### Application Limits
- `MAX_BATCH_SIZE`: Files per session (Default: 10).
- `MAX_CONTENT_LENGTH`: Upload size limit (Default: 150 MB).
- `MAX_FILE_AGE_SECONDS`: Auto-cleanup age (Default: 600s).
- `CLEANUP_PROBABILITY`: Chance of triggering cleanup on request (0.0-1.0).

---

## 4. Installation and Setup

### Docker (Recommended)
*Prerequisites: Docker Engine*

1. **Clone and run:**
   ```bash
   git clone https://github.com/ClementLG/Picturify.git
   cd Picturify
   docker compose up --build
   ```
2. **Access:** `http://localhost:5000`

### Manual Setup
1. **Install dependencies:** `pip install -r requirements.txt`
2. **Run:** `python run.py`

### Environment
Control the mode via `docker-compose.yml` `FLASK_ENV`:
- `production`: Uses **Gunicorn** (high performance).
- `development`: Uses Flask Debug Server (hot reload).

---

## 5. Security Features
- **Auto-Cleanup:** Stale files are automatically deleted to prevent storage overflow.
- **Secure Handling:** Filenames are sanitized; uploads are validated via PIL.
- **Headers:** HSTS and security headers enabled via `Flask-Talisman`.
- **CSRF:** All forms protected by `Flask-WTF`.

---

## 6. License
[GPLv3](LICENSE)