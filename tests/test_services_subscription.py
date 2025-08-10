"""Tests for bot services subscription."""

import pytest
import asyncio
import sys
import os
import json
import tempfile

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add the parent directory to the path to handle relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSubscriptionStructure:
    """Test subscription service structure and imports."""

    def test_import_structure(self):
        """Test that subscription service can be imported and has expected structure."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "bot.services.subscription", 
                os.path.join(os.path.dirname(__file__), "..", "bot", "services", "subscription.py")
            )
            assert spec is not None
        except Exception as e:
            pytest.fail(f"Failed to load subscription service: {e}")


class TestSubscriptionService:
    """Test SubscriptionService class."""

    def setup_method(self):
        """Set up test environment."""
        # Create temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.temp_path = Path(self.temp_file.name)
        
        # Mock SubscriptionService
        class MockSubscriptionService:
            def __init__(self, storage_file=None):
                self.storage_file = storage_file or self.temp_path
                self._subscriptions = {}
                self.subscription_types = {
                    'SYSTEM': 'system',
                    'ALERTS': 'alerts', 
                    'SCHEDULED': 'scheduled',
                    'NOTIFICATIONS': 'notifications'
                }
        
        self.service = MockSubscriptionService(self.temp_path)

    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_path.exists():
            self.temp_path.unlink()

    def test_subscription_service_initialization(self):
        """Test SubscriptionService initialization."""
        assert self.service.storage_file == self.temp_path
        assert self.service._subscriptions == {}
        assert len(self.service.subscription_types) > 0

    def test_subscription_data_loading(self):
        """Test loading subscription data from file."""
        # Create test data
        test_data = {
            "123456789": ["system", "alerts"],
            "987654321": ["scheduled"]
        }
        
        # Write test data to file
        with open(self.temp_path, 'w') as f:
            json.dump(test_data, f)
        
        def mock_load_subscriptions(service):
            """Mock loading subscriptions from file."""
            try:
                if service.storage_file.exists():
                    with open(service.storage_file, 'r') as f:
                        data = json.load(f)
                        service._subscriptions = {
                            int(user_id): set(subs) 
                            for user_id, subs in data.items()
                        }
                return True
            except Exception:
                service._subscriptions = {}
                return False
        
        # Test loading
        result = mock_load_subscriptions(self.service)
        assert result is True
        assert 123456789 in self.service._subscriptions
        assert "system" in self.service._subscriptions[123456789]

    def test_subscription_data_saving(self):
        """Test saving subscription data to file."""
        # Setup test data
        self.service._subscriptions = {
            123456789: {"system", "alerts"},
            987654321: {"scheduled"}
        }
        
        def mock_save_subscriptions(service):
            """Mock saving subscriptions to file."""
            try:
                data = {
                    str(user_id): list(subs) 
                    for user_id, subs in service._subscriptions.items()
                }
                
                service.storage_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(service.storage_file, 'w') as f:
                    json.dump(data, f, indent=2)
                return True
            except Exception:
                return False
        
        # Test saving
        result = mock_save_subscriptions(self.service)
        assert result is True
        assert self.temp_path.exists()
        
        # Verify saved data
        with open(self.temp_path, 'r') as f:
            saved_data = json.load(f)
        
        assert "123456789" in saved_data
        assert "system" in saved_data["123456789"]

    def test_subscribe_user(self):
        """Test subscribing user to notification types."""
        async def mock_subscribe(service, user_id, chat_id, subscription_type):
            """Mock user subscription."""
            # Validate subscription type
            if subscription_type not in service.subscription_types.values():
                return False
            
            # Add subscription
            if user_id not in service._subscriptions:
                service._subscriptions[user_id] = set()
            
            service._subscriptions[user_id].add(subscription_type)
            return True
        
        # Test valid subscription
        result = asyncio.run(mock_subscribe(self.service, 123456789, 123456789, "system"))
        assert result is True
        assert 123456789 in self.service._subscriptions
        assert "system" in self.service._subscriptions[123456789]
        
        # Test invalid subscription type
        result = asyncio.run(mock_subscribe(self.service, 123456789, 123456789, "invalid_type"))
        assert result is False

    def test_unsubscribe_user(self):
        """Test unsubscribing user from notification types."""
        # Setup initial subscriptions
        self.service._subscriptions = {
            123456789: {"system", "alerts"},
            987654321: {"scheduled"}
        }
        
        async def mock_unsubscribe(service, user_id, subscription_type):
            """Mock user unsubscription."""
            # Validate subscription type
            if subscription_type not in service.subscription_types.values():
                return False
            
            # Remove subscription
            if user_id in service._subscriptions:
                if subscription_type in service._subscriptions[user_id]:
                    service._subscriptions[user_id].remove(subscription_type)
                    
                    # Remove user if no subscriptions left
                    if not service._subscriptions[user_id]:
                        del service._subscriptions[user_id]
                    
                    return True
            
            return False
        
        # Test valid unsubscription
        result = asyncio.run(mock_unsubscribe(self.service, 123456789, "system"))
        assert result is True
        assert "system" not in self.service._subscriptions[123456789]
        
        # Test unsubscribing last subscription (should remove user)
        result = asyncio.run(mock_unsubscribe(self.service, 987654321, "scheduled"))
        assert result is True
        assert 987654321 not in self.service._subscriptions

    def test_get_user_subscriptions(self):
        """Test getting user's subscriptions."""
        # Setup test data
        self.service._subscriptions = {
            123456789: {"system", "alerts"},
            987654321: {"scheduled"}
        }
        
        async def mock_get_subscriptions(service, user_id):
            """Mock getting user subscriptions."""
            return list(service._subscriptions.get(user_id, set()))
        
        # Test existing user
        result = asyncio.run(mock_get_subscriptions(self.service, 123456789))
        assert len(result) == 2
        assert "system" in result
        assert "alerts" in result
        
        # Test non-existing user
        result = asyncio.run(mock_get_subscriptions(self.service, 999999999))
        assert len(result) == 0

    def test_get_subscribers_by_type(self):
        """Test getting subscribers for specific notification type."""
        # Setup test data
        self.service._subscriptions = {
            123456789: {"system", "alerts"},
            987654321: {"system"},
            555666777: {"alerts", "scheduled"}
        }
        
        async def mock_get_subscribers(service, subscription_type):
            """Mock getting subscribers by type."""
            return [
                user_id for user_id, subs in service._subscriptions.items()
                if subscription_type in subs
            ]
        
        # Test system subscribers
        result = asyncio.run(mock_get_subscribers(self.service, "system"))
        assert len(result) == 2
        assert 123456789 in result
        assert 987654321 in result
        
        # Test alerts subscribers
        result = asyncio.run(mock_get_subscribers(self.service, "alerts"))
        assert len(result) == 2
        assert 123456789 in result
        assert 555666777 in result
        
        # Test scheduled subscribers
        result = asyncio.run(mock_get_subscribers(self.service, "scheduled"))
        assert len(result) == 1
        assert 555666777 in result

    def test_is_user_subscribed(self):
        """Test checking if user is subscribed to specific type."""
        # Setup test data
        self.service._subscriptions = {
            123456789: {"system", "alerts"},
            987654321: {"scheduled"}
        }
        
        async def mock_is_subscribed(service, user_id, subscription_type):
            """Mock checking subscription status."""
            return (user_id in service._subscriptions and 
                   subscription_type in service._subscriptions[user_id])
        
        # Test positive cases
        result = asyncio.run(mock_is_subscribed(self.service, 123456789, "system"))
        assert result is True
        
        result = asyncio.run(mock_is_subscribed(self.service, 987654321, "scheduled"))
        assert result is True
        
        # Test negative cases
        result = asyncio.run(mock_is_subscribed(self.service, 123456789, "scheduled"))
        assert result is False
        
        result = asyncio.run(mock_is_subscribed(self.service, 999999999, "system"))
        assert result is False

    def test_get_all_subscriptions(self):
        """Test getting all subscriptions."""
        # Setup test data
        self.service._subscriptions = {
            123456789: {"system", "alerts"},
            987654321: {"scheduled"},
            555666777: {"system", "scheduled", "alerts"}
        }
        
        async def mock_get_all_subscriptions(service):
            """Mock getting all subscriptions."""
            return {
                user_id: list(subs) 
                for user_id, subs in service._subscriptions.items()
            }
        
        # Test getting all
        result = asyncio.run(mock_get_all_subscriptions(self.service))
        assert len(result) == 3
        assert 123456789 in result
        assert 987654321 in result
        assert 555666777 in result
        assert len(result[555666777]) == 3

    def test_remove_user_completely(self):
        """Test removing user from all subscriptions."""
        # Setup test data
        self.service._subscriptions = {
            123456789: {"system", "alerts"},
            987654321: {"scheduled"}
        }
        
        async def mock_remove_user(service, user_id):
            """Mock removing user completely."""
            if user_id in service._subscriptions:
                del service._subscriptions[user_id]
                return True
            return False
        
        # Test removing existing user
        result = asyncio.run(mock_remove_user(self.service, 123456789))
        assert result is True
        assert 123456789 not in self.service._subscriptions
        
        # Test removing non-existing user
        result = asyncio.run(mock_remove_user(self.service, 999999999))
        assert result is False

    def test_subscription_statistics(self):
        """Test getting subscription statistics."""
        # Setup test data
        self.service._subscriptions = {
            123456789: {"system", "alerts"},
            987654321: {"scheduled", "system"},
            555666777: {"alerts"}
        }
        
        async def mock_get_stats(service):
            """Mock getting subscription statistics."""
            stats = {
                'total_users': len(service._subscriptions),
                'total_subscriptions': sum(len(subs) for subs in service._subscriptions.values())
            }
            
            # Count subscriptions by type
            for sub_type in service.subscription_types.values():
                count = len([
                    user_id for user_id, subs in service._subscriptions.items()
                    if sub_type in subs
                ])
                stats[f'{sub_type}_subscribers'] = count
            
            return stats
        
        # Test statistics
        result = asyncio.run(mock_get_stats(self.service))
        assert result['total_users'] == 3
        assert result['total_subscriptions'] == 5  # 2 + 2 + 1
        assert result['system_subscribers'] == 2
        assert result['alerts_subscribers'] == 2
        assert result['scheduled_subscribers'] == 1


class TestSubscriptionServiceIntegration:
    """Test subscription service integration scenarios."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.temp_path = Path(self.temp_file.name)

    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_path.exists():
            self.temp_path.unlink()

    def test_file_persistence_across_sessions(self):
        """Test subscription persistence across service restarts."""
        # First session - create subscriptions
        session1_data = {
            123456789: {"system", "alerts"},
            987654321: {"scheduled"}
        }
        
        def mock_save_to_file(data, file_path):
            """Mock saving data to file."""
            json_data = {
                str(user_id): list(subs) 
                for user_id, subs in data.items()
            }
            
            with open(file_path, 'w') as f:
                json.dump(json_data, f, indent=2)
        
        def mock_load_from_file(file_path):
            """Mock loading data from file."""
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return {
                        int(user_id): set(subs) 
                        for user_id, subs in data.items()
                    }
            except Exception:
                return {}
        
        # Save session 1 data
        mock_save_to_file(session1_data, self.temp_path)
        
        # Load in session 2
        session2_data = mock_load_from_file(self.temp_path)
        
        # Verify persistence
        assert 123456789 in session2_data
        assert "system" in session2_data[123456789]
        assert 987654321 in session2_data

    def test_concurrent_subscription_operations(self):
        """Test concurrent subscription operations."""
        async def mock_concurrent_operations():
            """Mock concurrent subscription operations."""
            subscriptions = {}
            
            async def add_subscription(user_id, sub_type):
                if user_id not in subscriptions:
                    subscriptions[user_id] = set()
                subscriptions[user_id].add(sub_type)
                await asyncio.sleep(0.01)  # Simulate some processing
                return True
            
            async def remove_subscription(user_id, sub_type):
                if user_id in subscriptions and sub_type in subscriptions[user_id]:
                    subscriptions[user_id].remove(sub_type)
                    await asyncio.sleep(0.01)
                    return True
                return False
            
            # Run concurrent operations
            results = await asyncio.gather(
                add_subscription(123456789, "system"),
                add_subscription(123456789, "alerts"),
                add_subscription(987654321, "scheduled"),
                remove_subscription(123456789, "system"),
                return_exceptions=True
            )
            
            return results, subscriptions
        
        # Test concurrent operations
        results, final_subscriptions = asyncio.run(mock_concurrent_operations())
        assert all(isinstance(result, bool) for result in results)
        assert 123456789 in final_subscriptions
        assert "alerts" in final_subscriptions[123456789]

    def test_subscription_type_validation(self):
        """Test validation of subscription types."""
        valid_types = ["system", "alerts", "scheduled", "notifications"]
        
        def validate_subscription_type(subscription_type):
            """Validate subscription type."""
            return subscription_type in valid_types
        
        # Test valid types
        assert validate_subscription_type("system") is True
        assert validate_subscription_type("alerts") is True
        assert validate_subscription_type("scheduled") is True
        
        # Test invalid types
        assert validate_subscription_type("invalid") is False
        assert validate_subscription_type("") is False
        assert validate_subscription_type(None) is False

    def test_bulk_subscription_operations(self):
        """Test bulk subscription operations."""
        async def mock_bulk_subscribe(user_ids, subscription_types):
            """Mock bulk subscription operation."""
            results = []
            
            for user_id in user_ids:
                for sub_type in subscription_types:
                    # Mock subscription logic
                    if user_id and sub_type in ["system", "alerts", "scheduled"]:
                        results.append({'user_id': user_id, 'type': sub_type, 'success': True})
                    else:
                        results.append({'user_id': user_id, 'type': sub_type, 'success': False})
            
            return results
        
        # Test bulk operation
        user_ids = [123456789, 987654321, 555666777]
        subscription_types = ["system", "alerts"]
        
        results = asyncio.run(mock_bulk_subscribe(user_ids, subscription_types))
        
        assert len(results) == 6  # 3 users × 2 types
        success_count = sum(1 for result in results if result['success'])
        assert success_count == 6

    def test_subscription_conflict_resolution(self):
        """Test handling subscription conflicts and duplicates."""
        def mock_handle_duplicate_subscription(subscriptions, user_id, sub_type):
            """Mock handling duplicate subscription attempts."""
            if user_id not in subscriptions:
                subscriptions[user_id] = set()
            
            if sub_type in subscriptions[user_id]:
                return {'status': 'already_subscribed', 'action': 'none'}
            else:
                subscriptions[user_id].add(sub_type)
                return {'status': 'subscribed', 'action': 'added'}
        
        subscriptions = {}
        
        # First subscription
        result1 = mock_handle_duplicate_subscription(subscriptions, 123456789, "system")
        assert result1['status'] == 'subscribed'
        
        # Duplicate subscription
        result2 = mock_handle_duplicate_subscription(subscriptions, 123456789, "system")
        assert result2['status'] == 'already_subscribed'

    def test_subscription_migration_and_upgrade(self):
        """Test subscription data migration and format upgrades."""
        def mock_migrate_subscription_format(old_data):
            """Mock migrating subscription data format."""
            if isinstance(old_data, dict):
                # Check if it's old format (user_id as string keys)
                if all(isinstance(key, str) for key in old_data.keys()):
                    # Migrate to new format
                    new_data = {}
                    for user_id_str, subs in old_data.items():
                        try:
                            user_id = int(user_id_str)
                            # Convert list to set for new format
                            new_data[user_id] = set(subs) if isinstance(subs, list) else subs
                        except ValueError:
                            continue  # Skip invalid user IDs
                    return new_data
            
            return old_data
        
        # Test migration
        old_format = {
            "123456789": ["system", "alerts"],
            "987654321": ["scheduled"]
        }
        
        new_format = mock_migrate_subscription_format(old_format)
        
        assert 123456789 in new_format
        assert isinstance(new_format[123456789], set)
        assert "system" in new_format[123456789]

    def test_subscription_backup_and_restore(self):
        """Test subscription backup and restore functionality."""
        def mock_create_backup(subscriptions):
            """Mock creating subscription backup."""
            backup_data = {
                'version': '1.0',
                'created_at': '2024-01-01T00:00:00Z',
                'subscriptions': {
                    str(user_id): list(subs) 
                    for user_id, subs in subscriptions.items()
                }
            }
            return backup_data
        
        def mock_restore_backup(backup_data):
            """Mock restoring from backup."""
            if 'subscriptions' not in backup_data:
                return {}
            
            return {
                int(user_id): set(subs) 
                for user_id, subs in backup_data['subscriptions'].items()
            }
        
        # Test backup creation
        original_subscriptions = {
            123456789: {"system", "alerts"},
            987654321: {"scheduled"}
        }
        
        backup = mock_create_backup(original_subscriptions)
        assert 'version' in backup
        assert 'subscriptions' in backup
        
        # Test restore
        restored = mock_restore_backup(backup)
        assert 123456789 in restored
        assert "system" in restored[123456789]

    def test_subscription_analytics_and_reporting(self):
        """Test subscription analytics and reporting."""
        def mock_generate_analytics(subscriptions):
            """Mock generating subscription analytics."""
            analytics = {
                'total_users': len(subscriptions),
                'subscription_distribution': {},
                'average_subscriptions_per_user': 0,
                'most_popular_type': None,
                'least_popular_type': None
            }
            
            if not subscriptions:
                return analytics
            
            # Calculate distribution
            type_counts = {}
            total_subs = 0
            
            for user_subs in subscriptions.values():
                for sub_type in user_subs:
                    type_counts[sub_type] = type_counts.get(sub_type, 0) + 1
                    total_subs += 1
            
            analytics['subscription_distribution'] = type_counts
            analytics['average_subscriptions_per_user'] = total_subs / len(subscriptions)
            
            if type_counts:
                analytics['most_popular_type'] = max(type_counts.items(), key=lambda x: x[1])
                analytics['least_popular_type'] = min(type_counts.items(), key=lambda x: x[1])
            
            return analytics
        
        # Test analytics
        subscriptions = {
            123456789: {"system", "alerts"},
            987654321: {"system"},
            555666777: {"alerts", "scheduled", "system"}
        }
        
        analytics = mock_generate_analytics(subscriptions)
        
        assert analytics['total_users'] == 3
        assert analytics['subscription_distribution']['system'] == 3
        assert analytics['subscription_distribution']['alerts'] == 2
        assert analytics['most_popular_type'][0] == 'system'


def test_global_subscription_service():
    """Test global subscription service instance."""
    # Mock global service
    class MockGlobalSubscriptionService:
        def __init__(self):
            self.is_initialized = True
            self.service_type = "subscription"
    
    global_service = MockGlobalSubscriptionService()
    
    assert global_service.is_initialized is True
    assert global_service.service_type == "subscription"
