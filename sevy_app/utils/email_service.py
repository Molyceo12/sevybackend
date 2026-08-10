import os
import base64
import resend
from django.conf import settings
from django.template.loader import render_to_string

# Initialize Resend
if hasattr(settings, 'RESEND_API_KEY') and settings.RESEND_API_KEY:
    resend.api_key = settings.RESEND_API_KEY

def get_logo_base64():
    """Returns the base64 string of the logo for embedding directly in HTML."""
    frontend_assets_dir = os.path.join(settings.BASE_DIR.parent, 'sevy', 'assets', 'images')
    logo_path = os.path.join(frontend_assets_dir, 'logo.jpeg')
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    return ""

def send_customer_email(to_email, subject, template_name, context):
    """
    Hands off the email to a Celery background task so it doesn't block the API response.
    """
    from sevy_app.tasks import send_email_task
    try:
        send_email_task.delay(to_email, subject, template_name, context)
        print(f"\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::email notification:::::::::::::::::::::::::::::::")
        print(f":::::email shedulered successfully to celery::::::::::::::::")
        print(f" head : {subject}, to: {to_email},")
        print(f":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
        return True
    except Exception as e:
        print(f"Failed to queue Email task: {str(e)}")
        return False

def _execute_send_customer_email(to_email, subject, template_name, context):
    """
    Actually executes the email sending via Resend (runs in Celery background worker).
    """
    if not hasattr(settings, 'RESEND_API_KEY') or not settings.RESEND_API_KEY:
        print(f"Warning: RESEND_API_KEY not set. Cannot send email to {to_email}")
        return False
        
    try:
        html_content = render_to_string(f'emails/{template_name}', context)
        
        params = {
            "from": "Sevy Mobility <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }
        
        # Attach the logo as CID for inline rendering
        frontend_assets_dir = os.path.join(settings.BASE_DIR.parent, 'sevy', 'assets', 'images')
        logo_path = os.path.join(frontend_assets_dir, 'logo.jpeg')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_data = f.read()
                # Ensure the Resend python SDK passes this payload correctly
                params["attachments"] = [
                    {
                        "filename": "logo.jpeg",
                        "content": list(logo_data),
                        "content_id": "sevy_logo"
                    }
                ]
        
        email_response = resend.Emails.send(params)
        print(f"Email sent successfully to {to_email}. Response: {email_response}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")
        return False

def send_notification_email(to_email, subject, name, message, details=None, action_url=None, action_text=None, table_title=None, total_amount=None, total_label=None, closing_message=None):
    """
    Sends a generic notification email using the universal template.
    """
    context = {
        'title': subject,
        'name': name,
        'message': message,
        'details': details,
        'action_url': action_url,
        'action_text': action_text,
        'table_title': table_title,
        'total_amount': total_amount,
        'total_label': total_label,
        'closing_message': closing_message,
    }
    return send_customer_email(to_email, subject, 'universal_email.html', context)

def send_admin_email_notification(to_email, subject, message, notification_type, details=None):
    """
    Sends an admin email using the universal template.
    """
    # Create an appropriate table title based on the notification type
    table_title = "NOTIFICATION DETAILS"
    if 'transaction' in notification_type or 'withdrawal' in notification_type or 'withdrawal' in subject.lower():
        table_title = "TRANSACTION DETAILS"
    elif 'system' in notification_type:
        table_title = "SYSTEM DETAILS"
    elif 'cancelled' in notification_type:
        table_title = "CANCELLATION DETAILS"
        
    context = {
        'title': subject,
        'name': "Admin",
        'message': message,
        'details': details,
        'table_title': table_title
    }
    return send_customer_email(to_email, subject, 'universal_email.html', context)
