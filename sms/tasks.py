import os
import logging
import pandas as pd
from celery import shared_task
from django.conf import settings
from django.db.models import F
from .models import Campaign, MessageLog
from django.contrib.auth.models import User


logger = logging.getLogger(__name__)


@shared_task(bind=True)
def send_bulk_whatsapp(self, campaign_id, user_id, excel_path, template, img_url=None, pdf_url=None):
    """
    Parent task:
    Reads Excel and queues independent message tasks
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        user = User.objects.get(id=user_id)

        api_key = getattr(user.userprofile, "api_key", None)
        if not api_key:
            raise ValueError(f"User {user.username} does not have an API key!")

        df = pd.read_excel(excel_path)
        total = len(df)
        logger.warning(f"BULK TASK STARTED — rows: {len(df)}")


        # Store total count
        campaign.total_numbers = total
        campaign.save()

        for _, row in df.iterrows():
            send_single_whatsapp.apply_async(
                kwargs={
                    "campaign_id": campaign_id,
                    "user_id": user_id,
                    "row": row.to_dict(),
                    "template": template,
                    "api_key": api_key,
                    "img_url": img_url,
                    "pdf_url": pdf_url,
                },
                queue="whatsapp"  # send to WhatsApp only worker
            )

        logger.info(f"[BULK QUEUED] Campaign {campaign_id} → {total} messages")
        return {"status": "queued", "total": total}

    except Exception as e:
        logger.exception(f"[PARENT TASK FAILED] Campaign {campaign_id}: {e}")
        raise

    finally:
        # Delete temp Excel file
        try:
            if excel_path and os.path.exists(excel_path):
                os.remove(excel_path)
        except Exception as exc:
            logger.warning(f"Could not delete uploaded Excel file: {exc}")


@shared_task(
    bind=True,
    autoretry_for=(Exception,),      # retry only on real errors
    retry_backoff=True,             # exponential delay: 1s → 2s → 4s ...
    retry_kwargs={"max_retries": 3},
    rate_limit="10/m"               # ≈ 50 messages per 5 mins (SAFE)
)
def send_single_whatsapp(self, campaign_id, user_id, row, template, api_key, img_url=None, pdf_url=None):
    """
    Child task:
    Sends WhatsApp message + Log + Update counts
    """

    from .utils import send_via_cloudwhatsapp  # Local import avoids circular issue

    try:
        campaign = Campaign.objects.get(id=campaign_id)
        user = User.objects.get(id=user_id)

        phone = str(row.get("phone", "")).strip()

        if not phone.isdigit() or len(phone) < 10:
            # Invalid number logging
            MessageLog.objects.create(
                campaign=campaign,
                user=user,
                phone_number=phone,
                message_text="",
                status="failed",
                error_code="INVALID_PHONE",
            )
            Campaign.objects.filter(id=campaign_id).update(failed_count=F("failed_count") + 1)
            logger.warning(f"[INVALID PHONE] {phone}")
            return {"phone": phone, "status": "failed"}

        # Replace {{column_name}} placeholders
        message = template
        for col, value in row.items():
            if col != "phone":
                message = message.replace(f"{{{{{col}}}}}", str(value))

        message = message.strip()

        # Send API request
        success, error = send_via_cloudwhatsapp(
            phone=phone,
            message=message,
            api_key=api_key,
            img_url=img_url,
            pdf_url=pdf_url,
        )

        # Log the message
        MessageLog.objects.create(
            campaign=campaign,
            user=user,
            phone_number=phone,
            message_text=message,
            status="sent" if success else "failed",
            error_code=None if success else str(error),
        )

        if success:
            Campaign.objects.filter(id=campaign_id).update(sent_count=F("sent_count") + 1)
            logger.info(f"[SENT] {phone}")
        else:
            Campaign.objects.filter(id=campaign_id).update(failed_count=F("failed_count") + 1)
            logger.error(f"[FAILED] {phone} → {error}")

        return {"phone": phone, "status": "sent" if success else "failed"}

    except Exception as e:
        logger.exception(f"[RETRY] Phone {row.get('phone')} → {e}")
        raise  # triggers Celery retry
