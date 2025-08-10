"""Subscription management service."""

from typing import List, Dict, Set, Optional
import json
from pathlib import Path
from ..constants import SUBSCRIPTION_TYPES
import structlog

logger = structlog.get_logger(__name__)


class SubscriptionService:
    """Manages user subscriptions to different notification types."""
    
    def __init__(self, storage_file: Optional[Path] = None):
        """Initialize subscription service.
        
        Args:
            storage_file: Path to subscription storage file
        """
        self.storage_file = storage_file or Path("subscriptions.json")
        self._subscriptions: Dict[int, Set[str]] = {}
        self._load_subscriptions()
    
    def _load_subscriptions(self):
        """Load subscriptions from storage file."""
        try:
            if self.storage_file.exists():
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    # Convert string keys back to int and lists to sets
                    self._subscriptions = {
                        int(user_id): set(subs) 
                        for user_id, subs in data.items()
                    }
                logger.info("Subscriptions loaded", 
                           file=str(self.storage_file),
                           users=len(self._subscriptions))
            else:
                logger.info("No existing subscription file found")
        except Exception as e:
            logger.error("Error loading subscriptions", error=str(e))
            self._subscriptions = {}
    
    def _save_subscriptions(self):
        """Save subscriptions to storage file."""
        try:
            # Convert sets to lists for JSON serialization
            data = {
                str(user_id): list(subs) 
                for user_id, subs in self._subscriptions.items()
            }
            
            # Ensure directory exists
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug("Subscriptions saved", file=str(self.storage_file))
        except Exception as e:
            logger.error("Error saving subscriptions", error=str(e))
    
    async def subscribe(
        self, 
        user_id: int, 
        chat_id: int, 
        subscription_type: str
    ) -> bool:
        """Subscribe user to a notification type.
        
        Args:
            user_id: Telegram user ID
            chat_id: Telegram chat ID
            subscription_type: Type of subscription
            
        Returns:
            True if successful, False if invalid type
        """
        # Validate subscription type
        if subscription_type not in SUBSCRIPTION_TYPES.values():
            logger.warning("Invalid subscription type", 
                          user_id=user_id,
                          subscription_type=subscription_type)
            return False
        
        # Add subscription
        if user_id not in self._subscriptions:
            self._subscriptions[user_id] = set()
        
        self._subscriptions[user_id].add(subscription_type)
        self._save_subscriptions()
        
        logger.info("User subscribed",
                   user_id=user_id,
                   chat_id=chat_id,
                   subscription_type=subscription_type)
        
        return True
    
    async def unsubscribe(
        self, 
        user_id: int, 
        subscription_type: str
    ) -> bool:
        """Unsubscribe user from a notification type.
        
        Args:
            user_id: Telegram user ID
            subscription_type: Type of subscription
            
        Returns:
            True if successful, False if invalid type or not subscribed
        """
        # Validate subscription type
        if subscription_type not in SUBSCRIPTION_TYPES.values():
            logger.warning("Invalid subscription type", 
                          user_id=user_id,
                          subscription_type=subscription_type)
            return False
        
        # Remove subscription
        if user_id in self._subscriptions:
            if subscription_type in self._subscriptions[user_id]:
                self._subscriptions[user_id].remove(subscription_type)
                
                # Remove user if no subscriptions left
                if not self._subscriptions[user_id]:
                    del self._subscriptions[user_id]
                
                self._save_subscriptions()
                
                logger.info("User unsubscribed",
                           user_id=user_id,
                           subscription_type=subscription_type)
                
                return True
        
        logger.warning("User not subscribed to type",
                      user_id=user_id,
                      subscription_type=subscription_type)
        return False
    
    async def get_subscriptions(self, user_id: int) -> List[str]:
        """Get user's subscriptions.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            List of subscription types
        """
        subscriptions = list(self._subscriptions.get(user_id, set()))
        logger.debug("Retrieved subscriptions",
                    user_id=user_id,
                    subscriptions=subscriptions)
        return subscriptions
    
    async def get_subscribers(self, subscription_type: str) -> List[int]:
        """Get users subscribed to a specific type.
        
        Args:
            subscription_type: Type of subscription
            
        Returns:
            List of user IDs
        """
        subscribers = [
            user_id for user_id, subs in self._subscriptions.items()
            if subscription_type in subs
        ]
        
        logger.debug("Retrieved subscribers",
                    subscription_type=subscription_type,
                    count=len(subscribers))
        
        return subscribers
    
    async def is_subscribed(self, user_id: int, subscription_type: str) -> bool:
        """Check if user is subscribed to a type.
        
        Args:
            user_id: Telegram user ID
            subscription_type: Type of subscription
            
        Returns:
            True if subscribed, False otherwise
        """
        is_sub = (user_id in self._subscriptions and 
                 subscription_type in self._subscriptions[user_id])
        
        logger.debug("Checked subscription status",
                    user_id=user_id,
                    subscription_type=subscription_type,
                    is_subscribed=is_sub)
        
        return is_sub
    
    async def get_all_subscriptions(self) -> Dict[int, List[str]]:
        """Get all subscriptions.
        
        Returns:
            Dictionary mapping user IDs to their subscriptions
        """
        return {
            user_id: list(subs) 
            for user_id, subs in self._subscriptions.items()
        }
    
    async def remove_user(self, user_id: int) -> bool:
        """Remove all subscriptions for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user was removed, False if not found
        """
        if user_id in self._subscriptions:
            del self._subscriptions[user_id]
            self._save_subscriptions()
            
            logger.info("User removed from all subscriptions", user_id=user_id)
            return True
        
        return False
    
    async def get_stats(self) -> Dict[str, int]:
        """Get subscription statistics.
        
        Returns:
            Dictionary with subscription statistics
        """
        stats = {
            'total_users': len(self._subscriptions),
            'total_subscriptions': sum(len(subs) for subs in self._subscriptions.values())
        }
        
        # Count subscriptions by type
        for sub_type in SUBSCRIPTION_TYPES.values():
            stats[f'{sub_type}_subscribers'] = len(await self.get_subscribers(sub_type))
        
        logger.debug("Generated subscription stats", stats=stats)
        return stats


# Global subscription service instance
subscription_service = SubscriptionService()
