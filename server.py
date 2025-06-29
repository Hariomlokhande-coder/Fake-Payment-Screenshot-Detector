import os
import logging
import hashlib
import random
import string
from datetime import datetime

import cv2
import numpy as np
import pytesseract
from flask import Flask, request, jsonify, make_response, send_file
from flask_cors import CORS
from PIL import Image, ExifTags, ImageChops, ImageEnhance
from pymongo import MongoClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image

# 🔧 Configuration
UPLOAD_FOLDER = "uploads"
REPORTS_FOLDER = "reports"
MODEL_PATH = "model/fake_payment_detector_model.h5"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ✅ Flask Setup
app = Flask(__name__)
CORS(app)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["REPORTS_FOLDER"] = REPORTS_FOLDER

# ✅ Logger
logging.basicConfig(level=logging.DEBUG)

# ✅ MongoDB Setup
client = MongoClient("localhost", 27017)
db = client["payment_detector"]
results_collection = db["analysis_results"]

# ✅ Load Deep Learning Model
model = load_model(MODEL_PATH)

@app.route("/")
def home():
    return "✅ Fake Payment Screenshot Detector API Running"

@app.route("/upload", methods=["POST"])
def upload_image():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file found"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        ext = os.path.splitext(file.filename)[1].lower()
        filename = f"{timestamp}_{rand_str}{ext}"
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

        if not os.path.exists(path):
            return jsonify({"error": "File was not saved properly!"}), 500

        result, metadata = analyze_image(path)

        results_collection.insert_one({
            "filename": filename,
            "original_filename": file.filename,
            "result": result,
            "metadata": metadata,
            "timestamp": datetime.now()
        })

        report_name = f"{timestamp}_{rand_str}.pdf"
        report_path = os.path.join(REPORTS_FOLDER, report_name)
        generate_pdf_report(report_path, file.filename, result, metadata)

        return make_response(jsonify({
            "filename": filename,
            "result": result,
            "metadata": metadata,
            "report_url": f"http://127.0.0.1:5000/download_report/{report_name}"
        }))

    except Exception as e:
        logging.error(f"❌ Upload error: {e}")
        return jsonify({"error": str(e)}), 500

def analyze_image(image_path):
    try:
        # ✅ Deep learning prediction
        img = keras_image.load_img(image_path, target_size=(224, 224))
        img_array = keras_image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0
        pred = model.predict(img_array)[0][0]
        result = "Real" if pred > 0.5 else "Fake"

        # ✅ Edge pixel count
        edge_pixels = get_edge_pixel_count(image_path)

        # ✅ ELA
        ela_path = generate_ela(image_path)

        # ✅ Metadata & OCR
        metadata = extract_metadata(image_path)
        metadata["OCR Text"] = extract_text(image_path)
        metadata["ML Confidence"] = float(pred)
        metadata["ML Result"] = result
        metadata["Edge Pixel Count"] = edge_pixels
        metadata["ELA Image"] = ela_path

        return result, metadata

    except Exception as e:
        logging.error(f"❌ Analyze error: {e}")
        return "Error", {}

def extract_metadata(image_path):
    try:
        image = Image.open(image_path)
        metadata = {}
        exif_data = image.getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                metadata[tag] = str(value)

        file_stat = os.stat(image_path)
        metadata.update({
            "File Name": os.path.basename(image_path),
            "File Size (Bytes)": file_stat.st_size,
            "Last Modified": datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            "Image Format": image.format,
            "Image Mode": image.mode,
            "Image Size": f"{image.width}x{image.height}",
            "File Hash (MD5)": hashlib.md5(open(image_path, 'rb').read()).hexdigest()
        })

        return metadata
    except Exception as e:
        logging.error(f"❌ Metadata extraction failed: {e}")
        return {}

def extract_text(image_path):
    try:
        return pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        logging.error(f"❌ OCR failed: {e}")
        return ""

def generate_ela(image_path, quality=90):
    try:
        original = Image.open(image_path).convert('RGB')
        temp_path = image_path.replace(".jpg", "_compressed.jpg")
        original.save(temp_path, 'JPEG', quality=quality)
        compressed = Image.open(temp_path)
        ela_img = ImageChops.difference(original, compressed)
        max_diff = max([ex[1] for ex in ela_img.getextrema()])
        scale = 255.0 / max_diff if max_diff != 0 else 1
        ela_img = ImageEnhance.Brightness(ela_img).enhance(scale)
        ela_output = image_path.replace(".jpg", "_ELA.jpg")
        ela_img.save(ela_output)
        return os.path.basename(ela_output)
    except Exception as e:
        logging.error(f"❌ ELA failed: {e}")
        return ""

def get_edge_pixel_count(image_path):
    try:
        gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if gray is None:
            return 0
        edges = cv2.Canny(gray, 50, 150)
        return int(np.sum(edges > 0))
    except Exception as e:
        logging.error(f"❌ Edge detection failed: {e}")
        return 0

def generate_pdf_report(path, filename, result, metadata):
    try:
        c = canvas.Canvas(path, pagesize=letter)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 750, "Fake Transaction Detection Report")
        c.setFont("Helvetica", 12)
        c.drawString(100, 730, f"File Name: {filename}")
        c.drawString(100, 710, f"Result: {result}")

        y = 690
        for k, v in metadata.items():
            c.drawString(100, y, f"{k}: {v}")
            y -= 20
            if y < 50:
                c.showPage()
                y = 750
        c.save()
    except Exception as e:
        logging.error(f"❌ PDF generation failed: {e}")

@app.route("/download_report/<filename>")
def download_report(filename):
    path = os.path.join(REPORTS_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return jsonify({"error": "Report not found"}), 404

@app.route("/results", methods=["GET"])
def get_results():
    docs = list(results_collection.find({}, {'_id': 0}))
    return jsonify(docs)

if __name__ == "__main__":
    logging.debug("🚀 Starting Flask Server...")
    app.run(debug=False, threaded=False, use_reloader=False, host="0.0.0.0", port=5000)