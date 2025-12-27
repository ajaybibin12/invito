from app.core.config import settings
from email.message import EmailMessage
import smtplib


def send_invite_email(to_email: str, token: str, event_name: str):
    invite_link = f"{settings.FRONTEND_URL}/invite?token={token}"

    msg = EmailMessage()
    msg["Subject"] = f"You're invited to {event_name} 🎉"
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email

    msg.set_content(f"""
You are invited to {event_name}

Accept your invite:
{invite_link}

This link expires in 24 hours.
""")

    msg.add_alternative(f"""
    <html>
      <body style="font-family:Arial; background:#f4f4f4; padding:20px">
        <div style="max-width:600px; background:white; padding:30px; border-radius:10px">
          <h2>🎟️ You're Invited!</h2>
          <p>You’ve been invited to <strong>{event_name}</strong>.</p>
          <a href="{invite_link}"
             style="display:inline-block;
                    padding:12px 24px;
                    background:#4f46e5;
                    color:white;
                    text-decoration:none;
                    border-radius:6px;
                    font-weight:bold">
            Accept Invitation
          </a>
          <p style="margin-top:20px;color:#666">
            This link expires in 24 hours.
          </p>
        </div>
      </body>
    </html>
    """, subtype="html")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
    print(f"📧 Invite email sent to {to_email}")