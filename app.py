from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import PyPDF2
from io import BytesIO
import zipfile
import os

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

HTML_CONTENT = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Conversor PDF Mercado Libre</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 600px;
            width: 100%;
            padding: 40px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 28px;
            color: #333;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 14px;
        }
        
        .config-section {
            margin-bottom: 25px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .config-section label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        
        .config-section input {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            font-family: monospace;
            transition: border-color 0.3s;
        }
        
        .config-section input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .config-hint {
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }
        
        .dropzone {
            border: 2px dashed #667eea;
            border-radius: 12px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: #f8f9fa;
            margin-bottom: 20px;
        }
        
        .dropzone:hover {
            border-color: #764ba2;
            background: #f0f1ff;
        }
        
        .dropzone.drag-over {
            border-color: #764ba2;
            background: #e8e9ff;
            transform: scale(1.02);
        }
        
        .dropzone-text {
            color: #333;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .dropzone-hint {
            color: #999;
            font-size: 13px;
        }
        
        #fileInput {
            display: none;
        }
        
        .file-list {
            margin-bottom: 20px;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .file-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 12px;
            background: #f8f9fa;
            border-radius: 6px;
            margin-bottom: 8px;
            font-size: 13px;
            color: #333;
        }
        
        .file-item .remove {
            margin-left: auto;
            color: #999;
            cursor: pointer;
            font-size: 16px;
        }
        
        .file-item .remove:hover {
            color: #e74c3c;
        }
        
        .progress-section {
            display: none;
            margin-bottom: 20px;
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s;
        }
        
        .progress-text {
            font-size: 12px;
            color: #666;
            text-align: center;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
        }
        
        button {
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-convert {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        
        .btn-convert:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-convert:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn-clear {
            background: #f0f0f0;
            color: #333;
        }
        
        .btn-clear:hover {
            background: #e0e0e0;
        }
        
        .status {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            display: none;
        }
        
        .status.success {
            background: #d4edda;
            border-left: 4px solid #28a745;
            color: #155724;
            display: block;
        }
        
        .status.error {
            background: #f8d7da;
            border-left: 4px solid #dc3545;
            color: #721c24;
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 Conversor PDF</h1>
            <p>Convierte tus PDFs de Mercado Libre de landscape a portrait</p>
        </div>
        
        <div class="config-section">
            <label for="serverUrl">🌐 URL del servidor</label>
            <input type="text" id="serverUrl" placeholder="https://pdf-converter-xxxxx.onrender.com" value="">
            <div class="config-hint">Pega aquí la URL de tu servidor Render después de deployar</div>
        </div>
        
        <div class="status" id="status"></div>
        
        <div class="dropzone" id="dropzone">
            <div style="font-size: 40px; margin-bottom: 10px;">☁️</div>
            <div class="dropzone-text">Arrastra tus PDFs aquí</div>
            <div class="dropzone-hint">o haz click para seleccionar (máx. 500MB)</div>
        </div>
        
        <div class="file-list" id="fileList"></div>
        
        <div class="progress-section" id="progressSection">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div class="progress-text" id="progressText">Procesando...</div>
        </div>
        
        <div class="button-group">
            <button class="btn-convert" id="convertBtn" disabled>
                ⚙️ Convertir
            </button>
            <button class="btn-clear" id="clearBtn">
                🗑️ Limpiar
            </button>
        </div>
    </div>
    
    <input type="file" id="fileInput" accept=".pdf" multiple>
    
    <script>
        let selectedFiles = [];
        
        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const convertBtn = document.getElementById('convertBtn');
        const clearBtn = document.getElementById('clearBtn');
        const progressSection = document.getElementById('progressSection');
        const serverUrlInput = document.getElementById('serverUrl');
        const statusDiv = document.getElementById('status');
        
        dropzone.addEventListener('click', () => fileInput.click());
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('drag-over');
        });
