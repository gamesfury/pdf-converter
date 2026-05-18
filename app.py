from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import PyPDF2
from io import BytesIO
import zipfile
import os

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

@app.route('/', methods=['GET'])
def serve_index():
    """Sirve el archivo index.html"""
    try:
        html_path = os.path.join(os.path.dirname(__file__), 'index.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}", 404

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Servidor funcionando'})

@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'files' not in request.files or len(request.files.getlist('files')) == 0:
        return jsonify({'error': 'No se enviaron archivos'}), 400
    
    files = request.files.getlist('files')
    output_files = []
    errors = []
    
    for file in files:
        if file.filename == '':
            continue
            
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            pdf_writer = PyPDF2.PdfWriter()
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                mediabox = page.mediabox
                page_width = float(mediabox.width)
                page_height = float(mediabox.height)
                
                if page_width > page_height:
                    page.rotate(180)
                
                pdf_writer.add_page(page)
            
            output = BytesIO()
            pdf_writer.write(output)
            output.seek(0)
            output_files.append((file.filename, output.getvalue()))
            
        except Exception as e:
            errors.append({'file': file.filename, 'error': str(e)})
    
    if errors and not output_files:
        return jsonify({'error': f'Error procesando archivos: {errors}'}), 500
    
    if len(output_files) == 1:
        output_buffer = BytesIO(output_files[0][1])
        return send_file(
            output_buffer,
            as_attachment=True,
            download_name=output_files[0][0],
            mimetype='application/pdf'
        )
    
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in output_files:
            zip_file.writestr(filename, content)
    
    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name='pdfs_convertidos.zip',
        mimetype='application/zip'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
