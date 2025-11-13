# sms/tasks.py
import os
import time
import logging
import pandas as pd
from celery import shared_task
from django.conf import settings
from .utils import send_via_cloudwhatsapp
from .models import Campaign, MessageLog

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def send_bulk_whatsapp(self, campaign_id, excel_path, template):
    campaign = None  # Define early for use in finally
    try:
        # Fetch campaign early (may raise Campaign.DoesNotExist)
        campaign = Campaign.objects.get(id=campaign_id)

        # Read the Excel file
        df = pd.read_excel(excel_path)
        total = len(df)
        campaign.total_numbers = total
        campaign.save()

        # Load API keys
        api_keys = [k.strip() for k in getattr(settings, 'SMS_API_KEYS', []) if k.strip()]
        if not api_keys:
            raise ValueError("No API keys configured in SMS_API_KEYS")

        current_key_index = 0
        sent, failed = 0, 0

        for idx, row in df.iterrows():
            raw_phone = str(row.get('phone', '')).strip()
            if not raw_phone or not raw_phone.isdigit():
                logger.warning(f"Skipping invalid phone: '{raw_phone}'")
                failed += 1
                continue

            # Use 10-digit phone (no '91' prefix) — matches your working URL
            phone = raw_phone

            # Replace placeholders like {{name}}
            message = template
            for col in df.columns:
                if col == 'phone':
                    continue
                placeholder = f"{{{{{col}}}}}"
                if placeholder in message:
                    value = str(row.get(col, '')).strip()
                    message = message.replace(placeholder, value)

            message = message.strip()
            if not message:
                logger.warning(f"Empty message for {phone}")
                failed += 1
                continue

            # Ensure message is UTF-8 encodable
            try:
                message.encode('utf-8')
            except UnicodeEncodeError:
                logger.error(f"Invalid encoding in message for {phone}")
                failed += 1
                continue

            # Send via WhatsApp
            api_key = api_keys[current_key_index]
            success, error = send_via_cloudwhatsapp(phone, message, api_key)

            # Rotate key if blocked/invalid
            if not success and ('invalid api key' in str(error).lower() or 'blocked' in str(error).lower()):
                current_key_index = (current_key_index + 1) % len(api_keys)
                api_key = api_keys[current_key_index]
                success, error = send_via_cloudwhatsapp(phone, message, api_key)

            # Log result
            MessageLog.objects.create(
                campaign=campaign,
                phone_number=phone,
                message_text=message,
                status='sent' if success else 'failed',
                error_code=str(error) if not success else None,
                api_key_used=api_key
            )

            if success:
                sent += 1
            else:
                failed += 1

            # Update progress every 100 messages or at the end
            if (idx + 1) % 100 == 0 or idx == total - 1:
                campaign.sent_count = sent
                campaign.failed_count = failed
                campaign.save()

            time.sleep(0.5)  # Respect rate limits

        # Final update
        campaign.sent_count = sent
        campaign.failed_count = failed
        campaign.save()

        logger.info(f"Campaign {campaign_id} finished: {sent} sent, {failed} failed")
        print(f"Campaign {campaign_id} finished: {sent} sent, {failed} failed")

    except Exception as e:
        logger.exception(f"Task failed for campaign {campaign_id}: {e}")
        raise  # Re-raise to allow Celery to handle retry/failure if configured
    finally:
        # Clean up the temporary Excel file
        try:
            if excel_path and os.path.exists(excel_path):
                os.unlink(excel_path)
                logger.info(f"Temporary file {excel_path} deleted.")
        except Exception as cleanup_error:
            logger.warning(f"Failed to delete temp file {excel_path}: {cleanup_error}")