"""
Email service for sending notifications
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema


class EmailService:
    """Email service for sending notifications"""

    def __init__(self, mail_config: ConnectionConfig):
        self.fastmail = FastMail(mail_config)

    async def send_registration_notification(
        self, user_email: str, username: str, admin_email: str
    ):
        """Send registration notification to admin"""
        registration_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        message = MessageSchema(
            subject="New User Registration - LinkLink Server",
            recipients=[admin_email],
            body=f"""
            <html>
                <body>
                    <h2>New User Registration</h2>
                    <p>A new user has registered for an account:</p>
                    <ul>
                        <li><strong>Username:</strong> {username}</li>
                        <li><strong>Email:</strong> {user_email}</li>
                        <li><strong>Registration Date:</strong> {registration_time}</li>
                    </ul>
                    <p>Please review and approve/reject this registration.</p>
                    <p>You can approve or reject this user through the admin interface.</p>
                </body>
            </html>
            """,
            subtype="html",
        )
        await self.fastmail.send_message(message)

    async def send_approval_notification(
        self,
        user_email: str,
        username: str,
        approved: bool,
        reason: Optional[str] = None,
    ):
        """Send approval/rejection notification to user"""
        status = "approved" if approved else "rejected"
        subject = f"Account {status.title()} - LinkLink Server"

        body_content = f"""
        <html>
            <body>
                <h2>Account {status.title()}</h2>
                <p>Dear {username},</p>
                <p>Your account registration has been <strong>{status}</strong>.</p>
        """

        if approved:
            body_content += """
                <p>You can now log in to your account and start using our services.</p>
                <p>Thank you for choosing LinkLink Server!</p>
            """
        else:
            reason_text = reason or "No specific reason provided"
            body_content += f"""
                <p>Reason: {reason_text}</p>
                <p>If you believe this was an error, please contact support.</p>
            """

        body_content += """
            </body>
        </html>
        """

        message = MessageSchema(
            subject=subject, recipients=[user_email], body=body_content, subtype="html"
        )
        await self.fastmail.send_message(message)


class MockEmailService(EmailService):
    """Mock email service that does nothing - used when email is not configured"""

    def __init__(self):
        # Create a dummy config for the parent class
        dummy_config = ConnectionConfig(
            MAIL_USERNAME="dummy",
            MAIL_PASSWORD="dummy",
            MAIL_FROM="dummy@example.com",
            MAIL_PORT=587,
            MAIL_SERVER="smtp.example.com",
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
        )
        super().__init__(dummy_config)

    async def send_registration_notification(
        self, user_email: str, username: str, admin_email: str
    ):
        """Mock registration notification - does nothing"""
        pass

    async def send_approval_notification(
        self,
        user_email: str,
        username: str,
        approved: bool,
        reason: Optional[str] = None,
    ):
        """Mock approval notification - does nothing"""
        pass
