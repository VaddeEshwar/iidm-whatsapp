# sms/utils.py
import requests
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
import os
import time
from urllib.parse import urlencode,urlencode, quote_plus, quote
import logging
logger = logging.getLogger(__name__)

def send_via_cloudwhatsapp(phone, message, api_key, img_url=None, pdf_url=None):
    """
    Send WhatsApp message via CloudWhatsApp API.
    Works exactly like your successful test.
    """
    # ✅ Use HTTPS (your test used https)
    base_url = "https://graph.facebook.com/v22.0/989568807562414/messages"
    logger.info("building api url...")
    # Encode only the message (safe for spaces, special chars)
    msg_part = f"&msg={quote(message)}" if message else ""
    
    # Build base URL
    full_url = f"{base_url}?apikey={api_key}&mobile={phone}{msg_part}"
    
    # Append media if provided
    if img_url:
        full_url += f"&img1={img_url}"
    elif pdf_url:
        full_url += f"&pdf={pdf_url}"

    try:
        logger.info(f"[WhatsApp] Sending: {full_url}")
        response = requests.get(full_url, timeout=15)
        
        logger.info(f"[WhatsApp] Status: {response.status_code}, Response: {response.text[:200]}")
        
        success = response.status_code == 200 and ('success' in response.text.lower())
        return success, response.text

    except Exception as e:
        logger.exception(f"[WhatsApp] Failed to send to {phone}: {e}")
        return False, str(e)


def save_uploaded_file_to_media(uploaded_file: UploadedFile, subfolder="whatsapp"):
    """
    Save uploaded file to MEDIA_ROOT/subfolder and return public URL.
    Returns None if no file.
    """
    if not uploaded_file:
        return None

    max_size = 1 * 1024 * 1024  # 1 MB
    if uploaded_file.size > max_size:
        raise ValueError(f"File {uploaded_file.name} exceeds 1 MB limit.")

    # Validate extension
    _, ext = os.path.splitext(uploaded_file.name.lower())
    allowed_ext = ('.jpg', '.jpeg', '.png', '.pdf')
    if ext not in allowed_ext:
        raise ValueError(f"Unsupported file type. Allowed: {', '.join(allowed_ext)}")

    # Create media path
    media_dir = os.path.join(settings.MEDIA_ROOT, subfolder)
    os.makedirs(media_dir, exist_ok=True)

    # Generate safe filename
    filename = f"{int(time.time())}_{uploaded_file.name}"
    filepath = os.path.join(media_dir, filename)

    # Save file
    with open(filepath, 'wb') as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    # Return public URL
    public_url = f"{settings.MEDIA_URL}{subfolder}/{filename}"
    return public_url
