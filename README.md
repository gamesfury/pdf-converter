# Conversor de PDFs: Landscape → Portrait

Herramienta para convertir automáticamente PDFs de formato horizontal (landscape) a vertical (portrait).

## 🚀 Despliegue Rápido en Render.com (Gratis)

### Paso 1: Crear cuenta en GitHub (si no tienes)
1. Entra a https://github.com/signup
2. Completa el formulario (usa tu email personal o de trabajo)
3. Verifica tu email
4. ¡Listo!

### Paso 2: Subir el código a GitHub
1. Ve a https://github.com/new
2. Llena:
   - Repository name: `pdf-converter-mercadolibre`
   - Description: `Conversor de PDFs Landscape a Portrait`
   - ☑️ Public
3. Click "Create repository"
4. Verás instrucciones. Copia los comandos y pégalos en tu terminal (o usa GitHub Desktop si no sabes terminal)

**Si usas terminal (opción más fácil):**
```bash
cd ruta/donde/guardaste/los/archivos
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/pdf-converter-mercadolibre.git
git push -u origin main
```

### Paso 3: Desplegar en Render.com
1. Ve a https://render.com
2. Click "Sign Up" → regístrate con GitHub (recomendado)
3. Click "+ New +" → "Web Service"
4. Conecta tu repositorio `pdf-converter-mercadolibre`
5. Llena:
   - **Name:** `pdf-converter`
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free (gratis)
6. Click "Create Web Service"
7. **Espera 2-5 minutos** a que se despliegue (verás logs)
8. Cuando diga "Live", tu URL estará lista (algo como `https://pdf-converter-xxxxx.onrender.com`)

---

## 📋 Usar la Herramienta

Una vez desplegada en Render, usa la interfaz web:
- **URL:** `https://pdf-converter-xxxxx.onrender.com`
- Arrastra tus PDFs o haz click para seleccionar
- Haz click "Convertir"
- Descarga automáticamente

---

## 💻 Uso Local (Opcional)

Si quieres probar localmente:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Correr servidor
python app.py

# La app estará en http://localhost:5000
```

---

## ❓ Solución de problemas

**Problema:** "ModuleNotFoundError: No module named 'flask'"
- **Solución:** `pip install -r requirements.txt`

**Problema:** Render tarda en desplegar
- **Solución:** Es normal. Los planes gratis pueden tardar 2-5 min. Ten paciencia.

**Problema:** La URL de Render expira después de 15 min sin uso
- **Solución:** Es limitación del plan gratis. Entra de nuevo y se reiniciará.
- Para evitar esto, upgrade a plan pagado o usa una herramienta de "keep-alive"

---

## 📞 Soporte

Si tienes problemas:
1. Revisa que todos los archivos estén en la carpeta correcta
2. Verifica que el archivo `requirements.txt` existe
3. Abre un issue en GitHub

---

**¡Tu app está lista! 🎉**
