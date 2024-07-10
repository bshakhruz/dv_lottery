import os
import re
from flask import Flask, request, render_template, jsonify
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import logging

app = Flask(__name__)

# Configure logging
if not os.path.exists("logs"):
    os.makedirs("logs")
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("logs/app.log", mode="w"), logging.StreamHandler()]
                    )

# Ensure the uploads directory exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

def extract_text(file_path):
    logging.debug(f"Starting OCR on: {file_path}")
    try:
        if file_path.lower().endswith('.pdf'):
            doc = DocumentFile.from_pdf(file_path)
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            doc = DocumentFile.from_images(file_path)
        else:
            logging.error("Unsupported file format.")
            return "Unsupported file format."
        
        predictor = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
        result = predictor(doc)
        
        extracted_text = []
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = ' '.join([word.value for word in line.words])
                    extracted_text.append(line_text)
        
        extracted_text = '\n'.join(extracted_text)
        logging.debug(f"Extracted Text: {extracted_text}")
        return extracted_text
    except Exception as e:
        logging.error(f"Error during OCR: {e}", exc_info=True)
        return "OCR failed."

def format_extracted_text(extracted_text):
    MAP_KEYS = {
        "Entrant Name": "",
        "Year of Birth": "",
        "Confirmation Number": ""
    }
    
    text = extracted_text.lower()

    patterns = {
        "Entrant Name": re.compile(r"entrant name:\s*(.*)", re.IGNORECASE),
        "Year of Birth": re.compile(r"year of birth:\s*(\d{4})", re.IGNORECASE),
        "Confirmation Number": re.compile(r"confirmation number:\s*([0-9a-zA-Z]{16})", re.IGNORECASE)
    }

    for key, pattern in patterns.items():
        match = pattern.search(text)
        if match:
            value = match.group(1).strip()
            MAP_KEYS[key] = value

    if "Entrant Name" in MAP_KEYS:
        names = MAP_KEYS["Entrant Name"].split(',')
        if len(names) == 2:
            surname = names[0].strip().upper()
            given_name = names[1].strip().upper()
            MAP_KEYS["Entrant Name"] = f"{surname}, {given_name}"

    if "Confirmation Number" in MAP_KEYS:
        conf_number = MAP_KEYS["Confirmation Number"]
        if re.match(r"2025[0-9A-Z]{12}", conf_number):
            MAP_KEYS["Confirmation Number"] = conf_number.upper()

    logging.debug(f"Formatted Data: {MAP_KEYS}")
    return MAP_KEYS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    logging.debug("Received file upload request.")
    if 'file' not in request.files:
        logging.error("No file part in the request.")
        return jsonify({"error": "No file uploaded."}), 400
    
    file = request.files['file']
    if file.filename == '':
        logging.error("No selected file.")
        return jsonify({"error": "No file uploaded."}), 400

    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)
    logging.debug(f"File saved to {file_path}")

    extracted_text = extract_text(file_path)
    if extracted_text != "OCR failed." and extracted_text != "Unsupported file format.":
        formatted_data = format_extracted_text(extracted_text)
        return jsonify(formatted_data)
    else:
        return jsonify({"error": extracted_text}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5002)