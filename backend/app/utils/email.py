import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from ..config import settings

async def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send an email using SMTP with explicit TLS settings
    """
    print(f"Preparing to send email to: {to_email}")
    
    # For development, log the email instead of sending
    print("\n" + "="*50)
    print(f"TO: {to_email}")
    print(f"SUBJECT: {subject}")
    print("BODY:")
    print(body)
    print("="*50 + "\n")
    
    return True  # Return True to simulate successful send
    
    # Uncomment the following block to enable actual email sending
    """
    try:
        message = MIMEMultipart()
        message["From"] = settings.EMAIL_FROM
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))
        
        # For debugging
        print(f"Connecting to SMTP server: {settings.SMTP_SERVER}:{settings.SMTP_PORT}")
        
        # Connect with explicit TLS
        smtp = aiosmtplib.SMTP(
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            use_tls=False,  # We'll use starttls() explicitly
            timeout=10
        )
        
        print("Initiating SMTP connection...")
        await smtp.connect()
        print("Starting TLS...")
        await smtp.starttls(validate_certs=False)  # Disable cert validation for development
        print(f"Logging in as: {settings.SMTP_USERNAME}")
        await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        print("Sending email...")
        await smtp.send_message(message)
        await smtp.quit()
        print("Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"\n!!! ERROR SENDING EMAIL !!!")
        print(f"Type: {type(e).__name__}")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    """

async def send_otp_email(email: str, otp: str, username: Optional[str] = None) -> bool:
    """
    # For development, log the OTP to console instead of sending email
    print(f"\n{'='*50}")
    print(f"OTP for {email}: {otp}")
    if username:
        print(f"Username: {username}")
    print("(In production, this would be sent via email)")
    print(f"{'='*50}\n")
    
    # Uncomment the following to enable actual email sending in production
    """
    subject = "Your OTP for LiveMart"
    
    # Create a nice HTML email template
    username_display = f" {username}" if username else ""
    
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Hello{username_display},</h2>
        <p>Your OTP for LiveMart is:</p>
        <div style="background-color: #f0f0f0; padding: 20px; text-align: center; font-size: 24px; letter-spacing: 5px; margin: 20px 0;">
            <strong>{otp}</strong>
        </div>
        <p>This OTP is valid for {settings.OTP_EXPIRE_MINUTES} minutes.</p>
        <p>If you didn't request this OTP, please ignore this email.</p>
        <p>Best regards,<br/>The LiveMart Team</p>
    </div>
    """
    
    return await send_email(email, subject, body)
