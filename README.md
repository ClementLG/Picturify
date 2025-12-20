# Picturify

> **Analyze, understand, and purify your images.**

## 1. Project Overview

**Picturify** is a modern and secure web application dedicated to managing image metadata (EXIF). It allows users to understand what information is hidden in their photos (GPS location, device type, date, etc.) and control this data by modifying or completely removing it ("purifying") before publication.

It features a polished, responsive web interface based on **Bulma** with custom glassmorphism styling, and a fully functional **REST API** for programmatic access.

---

## 2. Tech Stack

### Backend
- **Language:** Python 3.11+
- **Web Framework:** Flask (lightweight, extensible)
- **Image Processing:**
  - **Pillow (PIL):** Basic image manipulation
  - **piexif:** Advanced reading/writing of EXIF metadata

### Frontend
- **Structure:** HTML5 / Jinja2
- **Style:** [Bulma CSS](https://bulma.io/) + Custom CSS (Animations, Gradients, Responsive Design)
- **Interactivity:** Vanilla JavaScript (ES6+) for Drag & Drop, Dynamic Forms, and Mobile Menu.
- **Icons:** FontAwesome

### Infrastructure (DevOps)
- **Containerization:** Docker (to create a portable image of the app)
- **Orchestration:** Docker Compose (simplify running the app with a single command)

---

## 3. Key Features

### Homepage & Upload
- **Interface:** Modern Hero section with entrance animations.
- **Drop Zone:** Interactive, responsive drag & drop area with visual feedback.
- **Action:** Automatic submission to server for analysis.

### Analysis & Dashboard ("Analyze" Mode)
- **Layout:** Responsive 2-column dashboard (Image preview + Data editor).
- **Data Categorization:**
  - 📍 **Location:** GPS Latitude/Longitude.
  - 📷 **Device:** Model, Brand, Lens.
  - ⚙️ **Technical:** ISO, Aperture, Shutter Speed.
  - 📅 **Temporal:** Date taken, Date modified.

### Advanced Data Editing ("Understand & Edit" Mode)
- **Standard Fields:** Easy edit for Artist, Copyright, and Description.
- **Custom Fields:** Dynamic form to add specific EXIF tags (Make, Model, Lens, DateTime, etc.) from a supported list.
- **Validation:** Ensures tags are written to the correct IFD group.

### Purification ("Purify" Mode)
- **"Purify All" Button:** Removes **all** metadata to anonymize the image.
- **Download:** Dedicated button to download the processed image at any time.

### Export / Download
- Generate download link for the modified/purified image.
- Automatic cleanup of files on the server (background task).

### REST API Integration
The application exposes a RESTful API (JSON) for third-party integration.
- `POST /api/v1/analyze`: Returns extraction EXIF tags.
- `POST /api/v1/purify`: Returns binary image with stripped metadata.
- `POST /api/v1/edit`: Accepts image + JSON tags to modify.

---

## 4. Code Architecture

The project follows the Flask "Application Factory" pattern with a clear MVC (Model View Controller) separation.

```text
picturify/
├── app/
│   ├── __init__.py          # App initialization
│   ├── main/                # Web routes
│   │   ├── __init__.py
│   │   └── routes.py        # Controllers
│   ├── api/                 # API Blueprint
│   │   ├── __init__.py
│   │   └── endpoints.py     # JSON endpoints
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── image_handler.py # Upload/save/cleanup
│   │   └── exif_manager.py  # EXIF logic (Pillow/piexif)
│   ├── static/
│   │   ├── css/             # Custom styles (Modern UI)
│   │   ├── js/              # Scripts (Drag&Drop, UI Logic)
│   │   └── uploads/         # Temporary folder
│   └── templates/           # Jinja2 Views
├── config.py                # Configuration
├── requirements.txt         # Dependencies
├── Dockerfile               # Docker build
├── docker-compose.yml       # Docker Compose
└── run.py
```

---

## 5. Design System

- **Modern Palette:** Indigo & Pink gradients.
- **Components:** Card-based layout with soft shadows and "Glassmorphism" touches.
- **Animations:** Fade-in entrance effects for a premium feel.
- **Responsiveness:** Fully adapted for Mobile, Tablet, and Desktop.

---

## 6. Installation and Setup

### Option A: Docker (Recommended)
*Prerequisites: Docker Engine, Docker Compose*

1. **Clone and run:**
   ```bash
   git clone https://github.com/ClementLG/Picturify.git
   cd Picturify
   docker-compose up --build -d
   ```
2. **Access:** Navigate to `http://localhost:5000`.
3. **Stop:**
   ```bash
   docker-compose down
   ```

### Option B: Local Python Installation
*Prerequisites: Python 3.11+, pip*

```bash
# Clone the project
git clone https://github.com/ClementLG/Picturify.git
cd Picturify

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python run.py
```

---

## 7. Security & Limitations
- **File Validation:** Strict extension checking (no .exe, .php, etc).
- **Upload Limit:** Configurable max size (default: 16 MB).
- **Privacy:** Automatic cleanup of uploaded files.

## 8. Future Improvements
- [ ] Batch processing support.
- [ ] Embedded interactive map for GPS data (LeafletJS).