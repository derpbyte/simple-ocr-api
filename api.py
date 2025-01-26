from flask import Flask, request
import tempfile
import os
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang='en')

def image_to_text(file_path):
    result = ocr.ocr(file_path, cls=False, det=False)
    return {'data': result[0][0][0]}, 200

app = Flask(__name__)

@app.route("/health")
def health():
    return "HEALTHY"

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return 'No file found', 400

    file = request.files['file']
    
    if file.filename == '':
        return 'No file selected', 400

    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, file.filename)
    file.save(temp_file_path)

    return image_to_text(temp_file_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)



# curl -X POST -F "file=@path_to_your_image.jpg" http://localhost:5001/process
