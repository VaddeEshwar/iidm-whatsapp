# sms/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate, login, logout
from .models import Campaign, MessageLog
from .tasks import send_bulk_whatsapp
from .utils import save_uploaded_file_to_media
from django.db.models import Sum
import re
import os
import tempfile
import pandas as pd
from django.conf import settings
import time
from django.contrib.auth.decorators import login_required
import json




# def upload_view(request):
#     if request.method == 'POST':
#         campaign_name = request.POST.get('campaign_name')
#         message_template = request.POST.get('message_template')
#         phone_number = request.POST.get('phone_number', '').strip()
#         excel_file = request.FILES.get('excel_file')
#         delay_input = request.POST.get('delay', '1')  # Default to 1 second

#         # Validate and sanitize delay
#         try:
#             delay_seconds = int(delay_input)
#             if delay_seconds < 0:
#                 delay_seconds = 1
#             elif delay_seconds > 60:
#                 delay_seconds = 60  # Max 60 sec for safety
#         except (ValueError, TypeError):
#             delay_seconds = 1

#         # Validate input
#         if not campaign_name or not message_template:
#             messages.error(request, "Campaign name and message template are required.")
#             return render(request, 'upload.html')

#         if not phone_number and not excel_file:
#             messages.error(request, "Either a phone number or an Excel file is required.")
#             return render(request, 'upload.html')

#         # Handle single phone number → create Excel in memory
#         if phone_number:
#             df = pd.DataFrame([{'phone': phone_number}])
#             with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
#                 df.to_excel(tmp, index=False)
#                 excel_path = tmp.name
#         else:
#             # Handle uploaded Excel file
#             with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
#                 for chunk in excel_file.chunks():
#                     tmp.write(chunk)
#                 excel_path = tmp.name

#         # Estimate total numbers
#         total = 1 if phone_number else pd.read_excel(excel_path).shape[0]

#         # Save campaign
#         campaign = Campaign.objects.create(
#             name=campaign_name,
#             template=message_template,
#             total_numbers=total,
#         )

#         # Launch Celery task with delay
#         send_bulk_whatsapp.delay(campaign.id, excel_path, message_template, delay_seconds)

#         messages.success(request, "Campaign started!")
#         return redirect('dashboard')

#     return render(request, 'upload.html')




 # Make sure this is imported


# views.py
import os
import pandas as pd
import tempfile
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.sites.models import Site
from urllib.parse import urljoin

from .models import Campaign
from .tasks import send_bulk_whatsapp
from .utils import save_uploaded_file_to_media  # Make sure it's imported

# @login_required
# def upload_view(request):
#     if request.method == 'POST':
#         campaign_name = request.POST.get('campaign_name')
#         message_template = request.POST.get('message_template')
#         phone_number = request.POST.get('phone_number', '').strip()
#         excel_file = request.FILES.get('excel_file')
#         delay_input = request.POST.get('delay', '1')

#         # Validate delay
#         try:
#             delay_seconds = int(delay_input)
#             delay_seconds = max(0, min(delay_seconds, 60))
#         except (ValueError, TypeError):
#             delay_seconds = 1

#         # Validate main fields
#         if not campaign_name or not message_template:
#             messages.error(request, "Campaign name and message template are required.")
            
#             return render(request, 'upload.html')
#         if not phone_number and not excel_file:
#             messages.error(request, "Either phone number or Excel file is required.")
#             return render(request, 'upload.html')

#         # ✅ Handle media uploads — THIS IS WHERE YOU PUT THE URL GENERATION
#         img_url = None
#         pdf_url = None
#         try:
#             img1 = request.FILES.get('img1')
#             pdf = request.FILES.get('pdf')

#             if img1 or pdf:
#                 # Get absolute base URL of your site
#                 # current_site = Site.objects.get_current()
#                 # protocol = 'https' if request.is_secure() else 'http'
#                 # base_url = f"{protocol}://{current_site.domain}"

#                 current_site = Site.objects.get_current()
#                 domain = current_site.domain

#                 # Force HTTPS for ngrok domains
#                 if domain.endswith('.ngrok-free.app') or domain.endswith('.ngrok.io'):
#                     base_url = f"https://{domain}"
#                 else:
#                     protocol = 'https' if request.is_secure() else 'http'
#                     base_url = f"{protocol}://{domain}"

#                 if img1:
#                     relative_path = save_uploaded_file_to_media(img1, "whatsapp/images")
#                     img_url = urljoin(base_url, relative_path)

#                 if pdf:
#                     relative_path = save_uploaded_file_to_media(pdf, "whatsapp/pdfs")
#                     pdf_url = urljoin(base_url, relative_path)
#                 print("✅ Final img_url:", img_url)
#                 print("✅ Final pdf_url:", pdf_url)

#         except ValueError as e:
#             messages.error(request, str(e))
#             return render(request, 'upload.html')
#         except Exception as e:
#             messages.error(request, f"Failed to process media: {str(e)}")
#             return render(request, 'upload.html')

#         # Handle Excel or single number
#         if phone_number:
#             df = pd.DataFrame([{'phone': phone_number}])
#             with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
#                 df.to_excel(tmp, index=False)
#                 excel_path = tmp.name
#         else:
#             with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
#                 for chunk in excel_file.chunks():
#                     tmp.write(chunk)
#                 excel_path = tmp.name

#         total = 1 if phone_number else pd.read_excel(excel_path).shape[0]
#         campaign = Campaign.objects.create(
#             user=request.user, 
#             name=campaign_name,
#             template=message_template,
#             total_numbers=total,
#         )

#         # Launch task with absolute media URLs
#         send_bulk_whatsapp.delay(
#             campaign.id,
#             excel_path,
#             message_template,
#             delay_seconds,
#             img_url=img_url,
#             pdf_url=pdf_url
#         )

#         messages.success(request, "Campaign started!")
#         return redirect('dashboard')

#     return render(request, 'upload.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
import os
import tempfile
import pandas as pd
from urllib.parse import urljoin
from django.contrib.sites.models import Site

from .models import Campaign
from .tasks import send_bulk_whatsapp
from .utils import save_uploaded_file_to_media


@login_required
def upload_view(request):
    if request.method == 'POST':
        campaign_name = request.POST.get('campaign_name', '').strip()
        message_template = request.POST.get('message_template', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        excel_file = request.FILES.get('excel_file')
        img1 = request.FILES.get('img1')
        pdf = request.FILES.get('pdf')
        delay_input = request.POST.get('delay', '1')

        # ====== 1. Validate core fields ======
        if not campaign_name:
            messages.error(request, "Campaign name is required.")
            return render(request, 'upload.html')
        if not message_template:
            messages.error(request, "Message template is required.")
            return render(request, 'upload.html')

        # ====== 2. Validate phone vs Excel mutual exclusion ======
        if phone_number and excel_file:
            messages.error(request, "Please provide either a phone number or an Excel file, not both.")
            return render(request, 'upload.html')
        if not phone_number and not excel_file:
            messages.error(request, "Either a phone number or an Excel file is required.")
            return render(request, 'upload.html')

        # ====== 3. Validate phone number (if provided) ======
        if phone_number:
            if not phone_number.isdigit():
                messages.error(request, "Phone number must contain digits only (no spaces, dashes, or symbols).")
                return render(request, 'upload.html')
            if len(phone_number) != 10:
                messages.error(request, "Phone number must be exactly 10 digits long.")
                return render(request, 'upload.html')
            # Note: Only one number allowed — input is single field, so this is enforced by UI/backend

        # ====== 4. Validate image and PDF mutual exclusion ======
        if img1 and pdf:
            messages.error(request, "You cannot upload both an image and a PDF. Please choose one.")
            return render(request, 'upload.html')

        # ====== 5. Validate file types and sizes (defense in depth) ======
        if img1:
            if not isinstance(img1, UploadedFile):
                messages.error(request, "Invalid image file.")
                return render(request, 'upload.html')
            valid_image_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif']
            if img1.content_type not in valid_image_types:
                messages.error(request, "Please upload a valid image (JPEG, PNG, JPG, or GIF).")
                return render(request, 'upload.html')
            if img1.size > 5 * 1024 * 1024:  # 5 MB
                messages.error(request, "Image file must be under 5 MB.")
                return render(request, 'upload.html')

        if pdf:
            if not isinstance(pdf, UploadedFile):
                messages.error(request, "Invalid PDF file.")
                return render(request, 'upload.html')
            if pdf.content_type != 'application/pdf':
                messages.error(request, "Please upload a valid PDF file.")
                return render(request, 'upload.html')
            if pdf.size > 1 * 1024 * 1024:  # 1 MB
                messages.error(request, "PDF file must be under 1 MB.")
                return render(request, 'upload.html')

        if excel_file:
            if not isinstance(excel_file, UploadedFile):
                messages.error(request, "Invalid Excel file.")
                return render(request, 'upload.html')
            valid_excel_ext = ('.xlsx', '.xls')
            if not excel_file.name.lower().endswith(valid_excel_ext):
                messages.error(request, "Please upload a valid Excel file (.xlsx or .xls).")
                return render(request, 'upload.html')
            if excel_file.size > 10 * 1024 * 1024:  # 10 MB
                messages.error(request, "Excel file must be under 10 MB.")
                return render(request, 'upload.html')

        # ====== 6. Validate delay ======
        try:
            delay_seconds = int(delay_input)
            delay_seconds = max(0, min(delay_seconds, 60))
        except (ValueError, TypeError):
            delay_seconds = 1

        # ====== 7. Process media URLs (if any) ======
        img_url = None
        pdf_url = None
        try:
            if img1 or pdf:
                current_site = Site.objects.get_current()
                domain = current_site.domain

                if domain.endswith('.ngrok-free.app') or domain.endswith('.ngrok.io'):
                    base_url = f"https://{domain}"
                else:
                    protocol = 'https' if request.is_secure() else 'http'
                    base_url = f"{protocol}://{domain}"

                if img1:
                    relative_path = save_uploaded_file_to_media(img1, "whatsapp/images")
                    img_url = urljoin(base_url, relative_path)

                if pdf:
                    relative_path = save_uploaded_file_to_media(pdf, "whatsapp/pdfs")
                    pdf_url = urljoin(base_url, relative_path)

        except Exception as e:
            messages.error(request, f"Failed to process media files: {str(e)}")
            return render(request, 'upload.html')

        # ====== 8. Prepare Excel file ======
        try:
            if phone_number:
                df = pd.DataFrame([{'phone': phone_number}])
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                    df.to_excel(tmp, index=False)
                    excel_path = tmp.name
                total = 1
            else:
                # Validate Excel content (at least one phone number)
                df = pd.read_excel(excel_file)
                if df.empty:
                    messages.error(request, "Uploaded Excel file is empty.")
                    return render(request, 'upload.html')
                if 'phone' not in df.columns:
                    messages.error(request, "Excel file must contain a 'phone' column.")
                    return render(request, 'upload.html')
                # Optional: validate phone numbers in Excel
                phone_col = df['phone'].astype(str).str.replace(r'\D', '', regex=True)
                if phone_col.str.len().ne(10).any():
                    messages.error(request, "All phone numbers in Excel must be exactly 10 digits.")
                    return render(request, 'upload.html')
                if phone_col.str.contains(r'[^0-9]').any():
                    messages.error(request, "Phone numbers in Excel must contain only digits.")
                    return render(request, 'upload.html')

                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                    df.to_excel(tmp, index=False)
                    excel_path = tmp.name
                total = len(df)
        except Exception as e:
            messages.error(request, f"Error processing Excel file: {str(e)}")
            return render(request, 'upload.html')

        # ====== 9. Save campaign ======
        campaign = Campaign.objects.create(
            user=request.user,
            name=campaign_name,
            template=message_template,
            total_numbers=total,
        )

        # ====== 10. Launch task ======
        # send_bulk_whatsapp.delay(
        #     campaign.id,
        #     excel_path,
        #     message_template,
        #     delay_seconds,
        #     request.user.id,
        #     img_url=img_url,
        #     pdf_url=pdf_url
        # )
        send_bulk_whatsapp.delay(
                campaign_id=campaign.id,
                user_id=request.user.id,
                excel_path=excel_path,
                template=message_template,
                delay_seconds=delay_seconds,
                img_url=img_url,
                pdf_url=pdf_url
            )

        messages.success(request, "Campaign started successfully!")
        return redirect('dashboard')

    return render(request, 'upload.html')



# @login_required
# def campaign_detail_view(request, campaign_id):
#     campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
#     logs = MessageLog.objects.filter(campaign=campaign)
#     print("🔍 Logs count:", logs.count())
#     total = campaign.total_numbers or 0
#     sent = campaign.sent_count or 0
#     failed = campaign.failed_count or 0
#     success_rate = round((sent / total) * 100, 2) if total > 0 else 0.0

#     context = {
#         'campaign': campaign,
#         'logs': logs,
#         'total': total,
#         'sent': sent,
#         'failed': failed,
#         'success_rate': success_rate,
#     }
#     return render(request, 'campaign_detail.html', context)



@login_required
def campaign_detail_view(request, campaign_id):
    # Ensure the campaign belongs to the current user
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    
    # Fetch logs: filter by BOTH campaign AND user (extra security)
    logs = MessageLog.objects.filter(
        campaign=campaign,
        user=request.user
    ).order_by('-timestamp')  # Most recent first

    # Prepare logs for JSON serialization
    logs_data = []
    for log in logs:
        logs_data.append({
            "phone": log.phone_number,
            "status": log.status,
            "error": log.error_code or "-",
            "key": log.api_key_used or "-",
        })

    # Campaign stats
    total = campaign.total_numbers or 0
    sent = campaign.sent_count or 0
    failed = campaign.failed_count or 0
    success_rate = round((sent / total) * 100, 2) if total > 0 else 0.0

    context = {
        'campaign': campaign,
        'logs_json': json.dumps(logs_data),  # ✅ Safe for JS
        'total': total,
        'sent': sent,
        'failed': failed,
        'success_rate': success_rate,
    }
    return render(request, 'campaign_detail.html', context)

@login_required
def dashboard_view(request):
    campaigns = Campaign.objects.filter(user=request.user).order_by('-created_at') # Replace with your model

    # Aggregate totals
    agg = campaigns.aggregate(
        total_sent=Sum('sent_count'),
        total_failed=Sum('failed_count')
    )
    total_sent = agg['total_sent'] or 0
    total_failed = agg['total_failed'] or 0
    total_processed = total_sent + total_failed

    # Calculate rates
    if total_processed > 0:
        success_rate = (total_sent / total_processed) * 100
        failure_rate = (total_failed / total_processed) * 100
    else:
        success_rate = 0.0
        failure_rate = 0.0

    context = {
        'campaigns': campaigns,
        'total_sent': total_sent,
        'success_rate': success_rate,
        'failure_rate': failure_rate,
    }
    return render(request, 'dashboard.html', context)

def Test(request):
    return render (request, 'test.html')

