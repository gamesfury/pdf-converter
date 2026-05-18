from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import PyPDF2
from PyPDF2.generic import RectangleObject
from io import BytesIO
import zipfile
import os

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

HTML = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Conversor PDF</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}.container{background:white;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,0.3);max-width:600px;width:100%;padding:40px}.header{text-align:center;margin-bottom:30px}.header h1{font-size:28px;color:#333;margin-bottom:10px}.header p{color:#666;font-size:14px}.config-section{margin-bottom:25px;padding:15px;background:#f8f9fa;border-radius:8px;border-left:4px solid #667eea}.config-section label{display:block;font-size:13px;font-weight:600;color:#333;margin-bottom:8px}.config-section input{width:100%;padding:10px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px;font-family:monospace}.config-section input:focus{outline:none;border-color:#667eea;box-shadow:0 0 0 3px rgba(102,126,234,0.1)}.config-hint{font-size:12px;color:#999;margin-top:5px}.dropzone{border:2px dashed #667eea;border-radius:12px;padding:40px 20px;text-align:center;cursor:pointer;background:#f8f9fa;margin-bottom:20px}.dropzone:hover{border-color:#764ba2;background:#f0f1ff}.dropzone.drag-over{border-color:#764ba2;background:#e8e9ff;transform:scale(1.02)}.dropzone-text{color:#333;font-weight:600;margin-bottom:5px}.dropzone-hint{color:#999;font-size:13px}#fileInput{display:none}.file-list{margin-bottom:20px;max-height:200px;overflow-y:auto}.file-item{display:flex;align-items:center;gap:10px;padding:10px 12px;background:#f8f9fa;border-radius:6px;margin-bottom:8px;font-size:13px;color:#333}.file-item .remove{margin-left:auto;color:#999;cursor:pointer;font-size:16px}.file-item .remove:hover{color:#e74c3c}.button-group{display:flex;gap:10px}button{flex:1;padding:12px 20px;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer}.btn-convert{background:linear-gradient(135deg,#667eea,#764ba2);color:white}.btn-convert:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 10px 20px rgba(102,126,234,0.3)}.btn-convert:disabled{opacity:0.5;cursor:not-allowed}.btn-clear{background:#f0f0f0;color:#333}.btn-clear:hover{background:#e0e0e0}.status{padding:15px;border-radius:8px;margin-bottom:20px;font-size:14px;display:none}.status.success{background:#d4edda;border-left:4px solid #28a745;color:#155724;display:block}.status.error{background:#f8d7da;border-left:4px solid #dc3545;color:#721c24;display:block}</style></head><body><div class="container"><div class="header"><h1>📄 Conversor PDF</h1><p>Convierte tus PDFs de Mercado Libre</p></div><div class="config-section"><label>🌐 URL del servidor</label><input type="text" id="serverUrl" placeholder="https://pdf-converter-xxxxx.onrender.com"><div class="config-hint">Pega la URL de tu servidor</div></div><div class="status" id="status"></div><div class="dropzone" id="dropzone"><div style="font-size:40px;margin-bottom:10px">☁️</div><div class="dropzone-text">Arrastra tus PDFs</div><div class="dropzone-hint">o haz click (máx. 500MB)</div></div><div class="file-list" id="fileList"></div><div class="button-group"><button class="btn-convert" id="convertBtn" disabled>⚙️ Convertir</button><button class="btn-clear" id="clearBtn">🗑️ Limpiar</button></div></div><input type="file" id="fileInput" accept=".pdf" multiple><script>let selectedFiles=[];const dropzone=document.getElementById('dropzone');const fileInput=document.getElementById('fileInput');const fileList=document.getElementById('fileList');const convertBtn=document.getElementById('convertBtn');const clearBtn=document.getElementById('clearBtn');const serverUrlInput=document.getElementById('serverUrl');const statusDiv=document.getElementById('status');dropzone.addEventListener('click',()=>fileInput.click());dropzone.addEventListener('dragover',(e)=>{e.preventDefault();dropzone.classList.add('drag-over')});dropzone.addEventListener('dragleave',()=>dropzone.classList.remove('drag-over'));dropzone.addEventListener('drop',(e)=>{e.preventDefault();dropzone.classList.remove('drag-over');handleFiles(e.dataTransfer.files)});fileInput.addEventListener('change',(e)=>handleFiles(e.target.files));clearBtn.addEventListener('click',clearFiles);convertBtn.addEventListener('click',convertFiles);function handleFiles(files){selectedFiles=Array.from(files).filter(f=>f.type==='application/pdf');renderFileList()}function renderFileList(){fileList.innerHTML=selectedFiles.map((file,idx)=>`<div class="file-item"><span>📄 ${file.name} (${(file.size/1024/1024).toFixed(1)}MB)</span><span class="remove" onclick="removeFile(${idx})">✕</span></div>`).join('');convertBtn.disabled=selectedFiles.length===0}window.removeFile=function(idx){selectedFiles.splice(idx,1);renderFileList()};function clearFiles(){selectedFiles=[];fileInput.value='';renderFileList();statusDiv.style.display='none'}async function convertFiles(){const serverUrl=serverUrlInput.value.trim();if(!serverUrl){showStatus('⚠️ Ingresa URL del servidor','error');return}if(selectedFiles.length===0){showStatus('⚠️ Selecciona archivos','error');return}convertBtn.disabled=true;const formData=new FormData();selectedFiles.forEach(file=>formData.append('files',file));try{const apiUrl=serverUrl.endsWith('/')?serverUrl:serverUrl+'/';const response=await fetch(apiUrl+'convert',{method:'POST',body:formData});if(response.ok){const blob=await response.blob();const url=window.URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=selectedFiles.length===1?selectedFiles[0].name:'pdfs_convertidos.zip';document.body.appendChild(a);a.click();window.URL.revokeObjectURL(url);a.remove();showStatus('✓ Archivos convertidos','success');clearFiles()}else{showStatus('❌ Error en conversión','error')}}catch(error){showStatus('❌ Error: '+error.message,'error')}finally{convertBtn.disabled=false}}function showStatus(message,type){statusDiv.textContent=message;statusDiv.className='status '+type;statusDiv.style.display='block'}</script></body></html>"""

@app.route('/', methods=['GET'])
def index():
    return HTML

@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'files' not in request.files or len(request.files.getlist('files')) == 0:
        return jsonify({'error': 'No files'}), 400
    
    files = request.files.getlist('files')
    output_files = []
    
    for file in files:
        try:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            for page in reader.pages:
                w = float(page.mediabox.width)
                h = float(page.mediabox.height)
                
                if w > h:
                    page.mediabox = RectangleObject([0, 0, h, w])
                
                writer.add_page(page)
            
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            output_files.append((file.filename, output.getvalue()))
            
        except Exception as e:
            return jsonify({'error': f'Error: {str(e)}'}), 500
    
    if len(output_files) == 1:
        return send_file(
            BytesIO(output_files[0][1]),
            as_attachment=True,
            download_name=output_files[0][0],
            mimetype='application/pdf'
        )
    
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        for filename, content in output_files:
            zf.writestr(filename, content)
    
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
