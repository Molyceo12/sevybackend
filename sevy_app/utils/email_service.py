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
    Sends an email using Resend with the provided template and context.
    The logo is attached as an inline image (CID).
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

def send_notification_email(to_email, subject, name, message, details=None, action_url=None, action_text=None):
    """
    Sends a generic notification email using the notification.html template.
    """
    context = {
        'title': subject,
        'name': name,
        'message': message,
        'details': details,
        'action_url': action_url,
        'action_text': action_text,
    }
    return send_customer_email(to_email, subject, 'notification.html', context)
