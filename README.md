<h1 align="center">Picturify</h1>

<p align="center">
    <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/-Flask-grey?style=flat&logo=flask" alt="Flask">
    <img src="https://img.shields.io/badge/-Docker-grey?logo=docker" alt="Docker">
  <a href="https://github.com/ClementLG/Picturify/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/ClementLG/Picturify" alt="License">
  </a>
</p>

<p align="center">
  <a href="https://www.buymeacoffee.com/clementlg">
    <img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee">
  </a>
</p>

> **Analyze, understand, and purify your images.**

## 1. Project Overview

**Picturify** is a modern and secure web application dedicated to managing image metadata (EXIF). It allows users to understand what information is hidden in their photos (GPS location, device type, date, etc.) and control this data by modifying or completely removing it ("purifying") before publication.

It features a polished, responsive web interface based on **Bulma** with custom glassmorphism styling, and a fully functional **REST API** for programmatic access.

---

## 2. Key Features

### Homepage & Upload
- **Interface:** Modern Hero section with entrance animations.
- **Drop Zone:** Interactive, responsive drag & drop area with visual feedback.
- **Action:** Automatic submission to server for analysis.

### Analysis & Dashboard ("Analyze" Mode)
- **Layout:** Responsive 2-column dashboard (Image preview + Data editor).
- **Interactive Map:** Visualize GPS coordinates directly on a Leaflet map.
- **Data Categorization:**
  - 📍 **Location:** GPS Latitude/Longitude (editable via map).
  - 📷 **Device:** Model, Brand, Lens.
  - 📅 **Temporal:** Date taken.

### Advanced Data Editing ("Understand & Edit" Mode)
- **Standard Fields:** Easy edit for Artist, Copyright, and Description.
- **GPS Editor:** Click on the map to set or modify location data.
- **Custom Fields:** Dynamic form to add specific EXIF tags based on the standard.

### Purification ("Purify" Mode)
- **"Purify & Clean" Button:** Removes **all** metadata to anonymize the image and immediately prompts for download.
- **Smart Workflow:** Optimized flow to download and offer to "Finish" (delete from server) or "Continue Editing".

### Security & Privacy
- **Automatic Cleanup:** Files older than 1 hour (configurable) are automatically deleted.
- **Strict Validation:** Magic number checks and PIL verification for all uploads.
- **CSRF Protection:** Full protection against Cross-Site Request Forgery.
- **Security Headers:** HSTS, X-Content-Type-Options, etc., via Flask-Talisman.
- **Path Traversal Protection:** Secure filename handling.

---

## 3. Installation and Setup

### Docker (Recommended)
*Prerequisites: Docker Engine, Docker Compose*

1. **Clone and run:**
   ```bash
   git clone https://github.com/ClementLG/Picturify.git
   cd Picturify
   docker compose up --build
   ```
2. **Access:** Navigate to `http://localhost:5000`.

### Environment Configuration
You can control the running mode via the `FLASK_ENV` environment variable in `docker-compose.yml`:

- **Production (Default):** Uses **Gunicorn** with 4 workers. Optimized for performance and concurrency.
  ```yaml
  environment:
    - FLASK_ENV=production
  ```
- **Development:** Uses `python run.py` with Debug Mode and Hot Reload.
  ```yaml
  environment:
    - FLASK_ENV=development
  ```

### Configuration (config.py)
Adjustable settings:
- `MAX_CONTENT_LENGTH`: Max upload size (default 25 MB).
- `MAX_STORED_FILES`: Max files stored before oldest are deleted.
- `CLEANUP_PROBABILITY` & `MAX_FILE_AGE_SECONDS`: Tunable garbage collection parameters.

---

## 4. API Documentation

Picturify exposes a RESTful API for integration.

**Base URL:** `/api/v1`

### 1. Analyze Image
Extracts metadata from an uploaded image.

- **Endpoint:** `POST /analyze`
- **Body (Multipart/Form-Data):**
  - `image`: The image file.
- **Response (JSON):**
  ```json
  {
      "filename": "uuid_original.jpg",
      "exif_data": {
          "Model": "iPhone 12",
          "GPSInfo": {...}
      }
  }
  ```

### 2. Purify Image
Removes all EXIF metadata and returns the cleaned image.

- **Endpoint:** `POST /purify`
- **Body (Multipart/Form-Data):**
  - `image`: The image file.
- **Response:** Binary image file (JPEG/PNG) without metadata.
- **Note:** The server deletes the file immediately after processing to conserve space.

---

## 5. Tech Stack

### Backend
- **Python 3.11+**
- **Flask:** Web Framework.
- **Gunicorn:** Production WSGI Server.
- **Pillow / Piexif:** Image & Metadata processing.

### Frontend
- **Bulma CSS:** Responsive UI.
- **Leaflet.js:** Interactive Maps.
- **Vanilla JS:** Dynamic interactions.

---

## 6. License
[GPLv3](LICENSE)