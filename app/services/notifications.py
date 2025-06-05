import requests
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from app.core.config import GOTIFY_URL, GOTIFY_APP_TOKEN, logger


class PushNotificationService:
    @staticmethod
    def is_initialized() -> bool:
        """Check if Gotify is configured"""
        return GOTIFY_URL is not None and GOTIFY_APP_TOKEN is not None

    @staticmethod
    def send_notification(client_token: str, title: str, body: str, data: Optional[Dict[str, Any]] = None) -> Dict:
        """Send a push notification to a client using Gotify"""
        if not PushNotificationService.is_initialized():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Push notification service is not configured"
            )
        
        # Prepare the notification payload
        payload = {
            "title": title,
            "message": body,
            "priority": 5,  # Medium priority
            "extras": data or {}
        }
        
        # Add client token to extras to identify the target client
        if "extras" not in payload:
            payload["extras"] = {}
        payload["extras"]["client_token"] = client_token
        
        try:
            # Send message to Gotify server
            headers = {"X-Gotify-Key": GOTIFY_APP_TOKEN}
            response = requests.post(
                f"{GOTIFY_URL}/message",
                json=payload,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to send push notification: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to send push notification: {response.text}"
                )
                
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send push notification: {str(e)}"
            )

    @staticmethod
    def send_multicast(client_tokens: List[str], title: str, body: str, data: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Send a push notification to multiple clients"""
        if not PushNotificationService.is_initialized():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Push notification service is not configured"
            )
        
        responses = []
        for token in client_tokens:
            try:
                response = PushNotificationService.send_notification(token, title, body, data)
                responses.append(response)
            except Exception as e:
                logger.error(f"Failed to send notification to {token}: {e}")
                # Continue with other tokens even if one fails
        
        return responses 