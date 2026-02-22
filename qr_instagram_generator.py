from flask import Flask, render_template, request, send_file
import qrcode
from io import BytesIO
import re
import os

app = Flask(__name__)

def extract_instagram_username(url):
    """Extrage username-ul Instagram din URL"""
    url = url.strip()
    patterns = [
        r'instagram\.com/([a-zA-Z0-9_.]+)/?', 
        r'ig\.me/([a-zA-Z0-9_.]+)/?', 
        r'^@?([a-zA-Z0-9_.]+)$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            username = match.group(1)
            username = username.rstrip('/')
            return username
    
    return None

def validate_instagram_url(url):
    """Validează dacă URL-ul este valid pentru Instagram"""
    if not url:
        return False, "URL-ul nu poate fi gol"
    
    username = extract_instagram_username(url)
    if not username:
        return False, "URL-ul Instagram nu este valid. Folosiți: instagram.com/username sau @username"
    
    if not re.match(r'^[a-zA-Z0-9_.]+$', username):
        return False, "Username-ul Instagram conține caractere invalide"
    
    if len(username) > 30:
        return False, "Username-ul Instagram este prea lung"
    
    return True, username

def generate_qr_code(instagram_url):
    """Generează cod QR pentru URL-ul Instagram"""
    is_valid, result = validate_instagram_url(instagram_url)
    
    if not is_valid:
        return None, result
    
    username = result
    full_url = f"https://instagram.com/{username}"
    
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(full_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return img_io, f"https://instagram.com/{username}"
    except Exception as e:
        return None, f"Eroare la generarea codului QR: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    instagram_url = data.get('instagram_url', '').strip()
    
    qr_image, result = generate_qr_code(instagram_url)
    
    if qr_image is None:
        return {'success': False, 'error': result}, 400
    
    return send_file(qr_image, mimetype='image/png', as_attachment=True, download_name='instagram_qr.png')

@app.route('/validate', methods=['POST'])
def validate():
    """Endpoint pentru validare în timp real"""
    data = request.get_json()
    instagram_url = data.get('instagram_url', '').strip()
    
    is_valid, result = validate_instagram_url(instagram_url)
    
    if is_valid:
        return {
            'success': True,
            'username': result,
            'url': f"https://instagram.com/{result}"
        }
    else:
        return {
            'success': False,
            'error': result
        }

if __name__ == '__main__':
    app.run(debug=True, port=5000)
