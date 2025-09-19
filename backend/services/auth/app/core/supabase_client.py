"""
Supabase client configuration and utilities
"""

from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Supabase client wrapper"""

    def __init__(self):
        self._client: Client = None
        self._service_client: Client = None

    @property
    def client(self) -> Client:
        """Get Supabase client with anon key (for client-side operations)"""
        if not self._client:
            if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
                logger.warning("Supabase credentials not configured")
                return None

            self._client = create_client(
                settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY
            )
            logger.info("Supabase client initialized")

        return self._client

    @property
    def service_client(self) -> Client:
        """Get Supabase client with service role key (for server-side operations)"""
        if not self._service_client:
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
                logger.warning("Supabase service credentials not configured")
                return None

            self._service_client = create_client(
                settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY
            )
            logger.info("Supabase service client initialized")

        return self._service_client

    def test_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            if not self.client:
                return False

            # Try to access the auth service
            response = self.client.auth.get_session()
            logger.info("Supabase connection test successful")
            return True

        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False

    def create_user_profile(self, user_data: dict) -> dict:
        """Create user profile in Supabase"""
        try:
            if not self.service_client:
                raise Exception("Supabase service client not available")

            # Insert user profile into profiles table
            response = self.service_client.table("profiles").insert(user_data).execute()

            if response.data:
                logger.info(f"User profile created: {response.data[0]['id']}")
                return response.data[0]
            else:
                raise Exception("Failed to create user profile")

        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            raise

    def get_user_profile(self, user_id: str) -> dict:
        """Get user profile from Supabase"""
        try:
            if not self.service_client:
                raise Exception("Supabase service client not available")

            response = (
                self.service_client.table("profiles")
                .select("*")
                .eq("id", user_id)
                .execute()
            )

            if response.data:
                return response.data[0]
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            raise

    def update_user_profile(self, user_id: str, update_data: dict) -> dict:
        """Update user profile in Supabase"""
        try:
            if not self.service_client:
                raise Exception("Supabase service client not available")

            response = (
                self.service_client.table("profiles")
                .update(update_data)
                .eq("id", user_id)
                .execute()
            )

            if response.data:
                logger.info(f"User profile updated: {user_id}")
                return response.data[0]
            else:
                raise Exception("Failed to update user profile")

        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            raise


# Create global Supabase client instance
supabase_client = SupabaseClient()
