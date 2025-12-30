"""
Email subscription routes for SendGrid integration
"""

import logging
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import HTTPError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/email", tags=["email"])

class EmailSubscription(BaseModel):
    email: EmailStr

@router.post("/subscribe")
async def subscribe_email(subscription: EmailSubscription):
    """
    Add email to SendGrid contact list and send confirmation email
    """
    try:
        # Get SendGrid API key from environment
        sg_api_key = os.getenv('SENDGRID_API_KEY')
        if not sg_api_key:
            logger.error("SENDGRID_API_KEY not found in environment variables")
            raise HTTPException(status_code=500, detail="SendGrid not configured")

        # Initialize SendGrid client
        sg = SendGridAPIClient(sg_api_key)

        # Add contact to SendGrid
        data = {
            "contacts": [
                {
                    "email": subscription.email
                }
            ]
        }

        response = sg.client.marketing.contacts.put(
            request_body=data
        )

        logger.info(f"✅ Email {subscription.email} added to SendGrid contact list")
        logger.info(f"SendGrid Response: {response.status_code}")

        # Send confirmation email
        message = Mail(
            from_email='team@joinmobius.com',
            to_emails=subscription.email,
            subject='Welcome to Mobius - You\'re on the Waitlist!',
            html_content=f"""
            <html>
                <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; background-color: #ffffff; color: #333333; padding: 40px; margin: 0; line-height: 1.6;">
                    <div style="max-width: 600px; margin: 0 auto;">
                        <h1 style="color: #333333; font-size: 24px; font-weight: 600; margin-bottom: 20px;">
                            Welcome to Mobius
                        </h1>

                        <p style="font-size: 16px; color: #333333; margin-bottom: 16px;">
                            Thank you for joining our waitlist! We're excited to have you on board.
                        </p>

                        <p style="font-size: 16px; color: #333333; margin-bottom: 24px;">
                            You're now part of an exclusive group getting early access to Mobius - your AI-powered trading desk that turns ideas into trades.
                        </p>

                        <p style="font-size: 16px; color: #333333; font-weight: 600; margin-bottom: 12px;">
                            What's Next?
                        </p>

                        <ul style="font-size: 16px; color: #333333; margin-bottom: 24px; padding-left: 20px;">
                            <li style="margin-bottom: 8px;">We'll keep you updated on our launch progress</li>
                            <li style="margin-bottom: 8px;">You'll get exclusive early access when we go live</li>
                            <li style="margin-bottom: 8px;">Be the first to know about new features and updates</li>
                        </ul>

                        <p style="font-size: 16px; color: #333333; margin-bottom: 24px;">
                            Stay tuned for updates!
                        </p>

                        <p style="font-size: 16px; color: #666666; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e5e5;">
                            Best regards,<br>
                            <strong>The Mobius Team</strong>
                        </p>
                    </div>
                </body>
            </html>
            """
        )

        # Send the email
        email_response = sg.send(message)
        logger.info(f"✅ Confirmation email sent to {subscription.email}")
        logger.info(f"Email Response: {email_response.status_code}")

        return {
            "success": True,
            "message": "Email successfully subscribed and confirmation sent",
            "email": subscription.email
        }

    except HTTPError as e:
        logger.error(f"SendGrid API error: {e.to_dict}")
        raise HTTPException(
            status_code=e.status_code,
            detail=f"Failed to add email: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error subscribing email: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
