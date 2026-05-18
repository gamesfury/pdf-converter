from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import PyPDF2
from io import BytesIO
import zipfile
import os

app = Flask(__name__)
CORS(app)

# Límite de tamaño: 500MB
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Servidor funcionando'})

@app.route('/convert', methods=['POST'])
def convert_pdf():
    """Convierte PDFs de landscape a portrait"""
    
    # Verificar que hay archivos
    if 'files' not in request.files or len(request.files.getlist('files')) == 0:
        return jsonify({'error': 'No se enviaron archivos'}), 400
    
    files = request.files.getlist('files')
    output_files = []
    errors = []
    
    for file in files:
        if file.filename == '':
            continue
            
        try:
            # Leer PDF
            pdf_reader = PyPDF2.PdfReader(file)
            pdf_writer = PyPDF2.PdfWriter()
            
            # Procesar cada página
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                
                # Si está en landscape (ancho > alto), rotar a portrait
                mediabox = page.mediabox
                page_width = float(mediabox.width)
                page_height = float(mediabox.height)
                
                if page_width > page_height:
                    # Rotar -90 grados para pasar de landscape a portrait
                    page.rotate(-90)
                
                pdf_writer.add_page(page)
            
            # Guardar en memoria
            output = BytesIO()
            pdf_writer.write(output)
            output.seek(0)
            output_files.append((file.filename, output.getvalue()))
            
        except Exception as e:
            errors.append({'file': file.filename, 'error': str(e)})
    
    # Si hay errores pero también archivos procesados
    if errors and not output_files:
        return jsonify({'error': f'Error procesando archivos: {errors}'}), 500
    
    # Si solo hay un archivo, descargarlo directamente
    if len(output_files) == 1:
        output_buffer = BytesIO(output_files[0][1])
        return send_file(
            output_buffer,
            as_attachment=True,
            download_name=output_files[0][0],
            mimetype='application/pdf'
        )
    
    # Si hay múltiples archivos, crear ZIP
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

@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'API de conversión de PDFs. POST /convert con archivos.'})

if __name__ == '__main__':
    # En producción, Render asignará el puerto automáticamente
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
