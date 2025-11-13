# sms/utils.py
import requests
import logging
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)


# def send_via_cloudwhatsapp(phone, message, api_key):
#     """
#     Send WhatsApp message via CloudWhatsApp (text-only, no media).
#     """
#     url = "http://web.cloudwhatsapp.com/wapp/api/send"  # Use HTTP if your test works with it

#     params = {
#         'apikey': api_key,
#         'mobile': phone,
#         'msg': message[:1000].strip(),
#     }

#     try:
#         response = requests.get(url, params=params, timeout=15)
#         logger.info(f"Sent to {phone} | Status: {response.status_code} | Response: {response.text[:200]}")

#         if response.status_code == 200:
#             try:
#                 data = response.json()
#                 if data.get('status') == 'success':
#                     return True, None
#                 else:
#                     return False, f"API: {data.get('message', str(data))}"
#             except ValueError:
#                 if 'success' in response.text.lower():
#                     return True, None
#                 else:
#                     return False, f"Text: {response.text[:100]}"
#         else:
#             return False, f"HTTP {response.status_code}: {response.text[:100]}"

#     except Exception as e:
#         error_msg = f"Exception: {str(e)}"
#         logger.error(error_msg)
#         return False, error_msg





# # sms/utils.py
# import os
# import requests
# import logging
# from django.conf import settings

# logger = logging.getLogger(__name__)

# def send_via_cloudwhatsapp(phone, message, api_key, media_path=None):
#     """
#     Send WhatsApp message via CloudWhatsApp.
#     Supports:
#       - Text-only (if media_path is None)
#       - Image or PDF with caption (if media_path is provided)
#     """
#     url = "http://web.cloudwhatsapp.com/wapp/api/send"

#     # Trim and cap message (as before)
#     caption = message[:2000].strip() if message else ""

#     try:
#         if media_path and os.path.isfile(media_path):
#             # 📎 Media mode: POST with file upload
#             with open(media_path, 'rb') as f:
#                 files = {'file': (os.path.basename(media_path), f)}
#                 data = {
#                     'apikey': api_key,
#                     'mobile': phone,
#                 }
#                 # Only add caption if not empty
#                 if caption:
#                     data['msg'] = caption

#                 response = requests.post(url, data=data, files=files, timeout=30)
#         else:
#             # 📝 Text-only mode: GET (as before)
#             params = {
#                 'apikey': api_key,
#                 'mobile': phone,
#                 'msg': caption or " ",  # Avoid empty msg if needed
#             }
#             response = requests.get(url, params=params, timeout=15)

#         # Log response
#         logger.info(
#             f"Sent to {phone} | Media: {bool(media_path)} | "
#             f"Status: {response.status_code} | Response: {response.text[:200]}"
#         )

#         # Parse success
#         if response.status_code == 200:
#             try:
#                 data = response.json()
#                 if data.get('status') == 'success':
#                     return True, None
#                 else:
#                     return False, f"API: {data.get('message', str(data))}"
#             except ValueError:
#                 # Fallback: check text response
#                 if 'success' in response.text.lower():
#                     return True, None
#                 else:
#                     return False, f"Text: {response.text[:100]}"
#         else:
#             return False, f"HTTP {response.status_code}: {response.text[:100]}"

#     except Exception as e:
#         error_msg = f"Exception during send to {phone}: {str(e)}"
#         logger.error(error_msg)
#         return False, error_msg


# sms/utils.py

# sms/utils.py
import os
import time
import requests
import logging
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)
# sms/utils.py
import requests
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

# def send_via_cloudwhatsapp(phone, message, api_key, img_url=None, pdf_url=None):
#     """
#     Send WhatsApp via CloudWhatsApp API.
#     Uses:
#       - img1=URL for images
#       - pdf=URL for PDFs
#     """
#     url = "http://web.cloudwhatsapp.com/wapp/api/send"
#     caption = message[:2000].strip() if message else ""

#     # 🔍 Debug inputs
#     logger.debug(f"[WhatsApp] Preparing send to {phone}")
#     logger.debug(f"[WhatsApp] Caption: {repr(caption)}")
#     logger.debug(f"[WhatsApp] img_url: {img_url}")
#     logger.debug(f"[WhatsApp] pdf_url: {pdf_url}")

#     try:
#         params = {
#             'apikey': api_key,
#             'mobile': phone,
#         }
#         if caption:
#             params['msg'] = caption

#         # Add media parameters based on what's provided
#         if img_url:
#             params['img1'] = img_url
#             params['type'] = 'image'  # 👈 Recommended by many gateways
#         elif pdf_url:
#             params['pdf'] = pdf_url   # 👈 You confirmed it's 'pdf', not 'pdf1'
#             params['type'] = 'pdf'

#         # 🔍 Log full request (safe for debugging)
#         full_url = f"{url}?{urlencode(params)}"
#         logger.info(f"[WhatsApp Request] Sending to {phone}")
#         logger.info(f"[WhatsApp Request] URL: {full_url}")

#         # Send GET request
#         response = requests.get(url, params=params, timeout=15)

#         # 🔍 Log response
#         logger.info(
#             f"[WhatsApp Response] To: {phone} | Status: {response.status_code} "
#             f"| Body: {response.text[:300]}"
#         )

#         # Parse result
#         if response.status_code == 200:
#             try:
#                 data = response.json()
#                 if data.get('status') == 'success':
#                     logger.info(f"[WhatsApp] ✅ Success for {phone}")
#                     return True, None
#                 else:
#                     error_msg = data.get('message', str(data))
#                     logger.warning(f"[WhatsApp] ❌ API Error for {phone}: {error_msg}")
#                     return False, f"API: {error_msg}"
#             except ValueError:
#                 # Handle non-JSON responses
#                 if 'success' in response.text.lower():
#                     logger.info(f"[WhatsApp] ✅ Text-based success for {phone}")
#                     return True, None
#                 else:
#                     logger.warning(f"[WhatsApp] ❌ Non-JSON error: {response.text[:200]}")
#                     return False, f"Text: {response.text[:200]}"
#         else:
#             logger.error(f"[WhatsApp] ❌ HTTP {response.status_code} for {phone}: {response.text[:200]}")
#             return False, f"HTTP {response.status_code}: {response.text[:200]}"

#     except requests.exceptions.Timeout:
#         logger.exception(f"[WhatsApp] ⏱️ Timeout sending to {phone}")
#         return False, "Request timed out"
#     except requests.exceptions.ConnectionError:
#         logger.exception(f"[WhatsApp] 🌐 Connection failed to gateway for {phone}")
#         return False, "Could not reach WhatsApp gateway"
#     except Exception as e:
#         logger.exception(f"[WhatsApp] 💥 Unexpected error for {phone}: {e}")
#         return False, f"Exception: {str(e)}"

from urllib.parse import urlencode, quote_plus
import requests
import logging

logger = logging.getLogger(__name__)

# def send_via_cloudwhatsapp(phone, message, api_key, img_url=None, pdf_url=None):
#     """
#     Send WhatsApp via CloudWhatsApp API.
#     Uses POST (not GET) because gateway requires it for media.
#     """
#     url = "http://web.cloudwhatsapp.com/wapp/api/send"
#     caption = message[:2000].strip() if message else ""

#     logger.debug(f"[WhatsApp] Preparing send to {phone}")
#     logger.debug(f"[WhatsApp] Caption: {repr(caption)}")
#     logger.debug(f"[WhatsApp] img_url: {img_url}")
#     logger.debug(f"[WhatsApp] pdf_url: {pdf_url}")

#     try:
#         # Build payload as form data (query params in POST body)
#         payload = {
#             'apikey': api_key,
#             'mobile': phone,
#         }
#         if caption:
#             payload['msg'] = caption

#         if img_url:
#             payload['img1'] = img_url
#         elif pdf_url:
#             payload['pdf'] = pdf_url

#         # Add User-Agent header
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
#         }

#         logger.info(f"[WhatsApp Request] Sending to {phone} via POST")
#         logger.info(f"[WhatsApp Payload] {payload}")

#         # ✅ SEND AS POST (not GET)
#         response = requests.post(url, data=payload, headers=headers, timeout=15)

#         logger.info(
#             f"[WhatsApp Response] To: {phone} | Status: {response.status_code} "
#             f"| Body: {response.text[:300]}"
#         )

#         if response.status_code == 200:
#             try:
#                 data = response.json()
#                 if data.get('status') == 'success':
#                     logger.info(f"[WhatsApp] ✅ Success for {phone}")
#                     return True, None
#                 else:
#                     error_msg = data.get('message', str(data))
#                     logger.warning(f"[WhatsApp] ❌ API Error for {phone}: {error_msg}")
#                     return False, f"API: {error_msg}"
#             except ValueError:
#                 if 'success' in response.text.lower():
#                     logger.info(f"[WhatsApp] ✅ Text-based success for {phone}")
#                     return True, None
#                 else:
#                     logger.warning(f"[WhatsApp] ❌ Non-JSON error: {response.text[:200]}")
#                     return False, f"Text: {response.text[:200]}"
#         else:
#             logger.error(f"[WhatsApp] ❌ HTTP {response.status_code} for {phone}: {response.text[:200]}")
#             return False, f"HTTP {response.status_code}: {response.text[:200]}"

#     except requests.exceptions.Timeout:
#         logger.exception(f"[WhatsApp] ⏱️ Timeout sending to {phone}")
#         return False, "Request timed out"
#     except requests.exceptions.ConnectionError:
#         logger.exception(f"[WhatsApp] 🌐 Connection failed to gateway for {phone}")
#         return False, "Could not reach WhatsApp gateway"
#     except Exception as e:
#         logger.exception(f"[WhatsApp] 💥 Unexpected error for {phone}: {e}")
#         return False, f"Exception: {str(e)}"

# sms/utils.py
import requests
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

def send_via_cloudwhatsapp(phone, message, api_key, img_url=None, pdf_url=None):
    """
    Send WhatsApp message via CloudWhatsApp API.
    Works exactly like your successful test.
    """
    # ✅ Use HTTPS (your test used https)
    base_url = "https://web.cloudwhatsapp.com/wapp/api/send"
    
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