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

**Picturify** is a modern and secure web application dedicated to managing image metadata (EXIF). It allows users to understand what information is hidden in their photos (GPS location, device type, date, etc.) and control this data by modifying or completely removing it ("purifying") before publication.

It features a polished, responsive web interface based on **Bulma** with custom glassmorphism styling, drag-and-drop batch processing, and a REST API.

---

## 2. Key Features

### Homepage & Batch Upload
- **Drag & Drop:** Interactive area to upload multiple images at once (up to 10 by default).
- **Batch Management:** 
  - View all uploaded images in a grid.
  - Delete specific images from the batch.
  - **"Start Over"**: Clear the entire batch in one click.
  - **Download All**: Get a ZIP of all processed images.
- **Smart Privacy**: Download workflow prompts you to immediately delete files from the server after downloading.

### Analysis & Dashboard ("Analyze" Mode)
- **Interactive Map:** Visualize GPS coordinates directly on a Leaflet map.
- **Data Categorization:** View Location (editable), Device info, and Date taken.

### Advanced Data Editing ("Understand & Edit" Mode)
- **Standard Fields:** Easy edit for Artist, Copyright, and Description.
- **GPS Editor:** Click on the map to set or modify location data.
- **Smart Templates:** Apply preset metadata templates (e.g., "Flickr Mode").

### Purification ("Purify" Mode)
- **Deep Clean:** Removes **all** metadata (EXIF, XMP, IPTC) by re-encoding the image.
- **Configurable Quality:** Choose between maximum quality (larger files) or optimized compression.

---

## 3. Configuration (config.py)

Picturify is highly configurable. You can tune performance and security settings in `config.py`:

### Image Quality
- `IMAGE_QUALITY`: JPEG quality (1-100). Default is `100` (Max quality, larger files). Set to `85-95` for smaller files.
- `IMAGE_SUBSAMPLING`: Chroma subsampling. `0` (4:4:4) is best quality, `2` (4:2:0) is standard.

### Safety & Limits
- `MAX_BATCH_SIZE`: Max files per session (Default: 10).
- `MAX_CONTENT_LENGTH`: Max upload size (Default: 150 MB).
- `MAX_FILE_AGE_SECONDS`: Time before old files are auto-deleted (Default: 600s).

---

## 4. Installation and Setup

### Docker (Recommended)
*Prerequisites: Docker Engine, Docker Compose*

1. **Clone and run:**
   ```bash
   git clone https://github.com/ClementLG/Picturify.git
   cd Picturify
   docker compose up --build
   ```
2. **Access:** Navigate to `http://localhost:5000`.

### Environment Variables
You can control the running mode via `docker-compose.yml`:

- **Production (Default):** Uses **Gunicorn** with 4 workers.
  ```yaml
  environment:
    - FLASK_ENV=production
  ```
- **Development:** Uses Flask debug server with hot reload.
  ```yaml
  environment:
    - FLASK_ENV=development
  ```

---

## 5. API Documentation

**Base URL:** `/api/v1`

### 1. Analyze Image
- **Endpoint:** `POST /analyze`
- **Body:** `image` file.
- **Response:** JSON with EXIF data.

### 2. Purify Image
- **Endpoint:** `POST /purify`
- **Body:** `image` file.
- **Response:** Binary image file (JPEG/PNG) without metadata.

---

## 6. License
[GPLv3](LICENSE)