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
    Add email to SendGrid contact list
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

        return {
            "success": True,
            "message": "Email successfully subscribed",
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
