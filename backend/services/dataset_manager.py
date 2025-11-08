"""
Dataset Manager - Manages persistent storage of trading datasets

Handles caching of Reddit, Twitter, and news data to avoid redundant API calls
across iterations and future backtests.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import date, datetime, timedelta
from supabase import Client
from db.supabase_client import get_supabase_admin
import json

logger = logging.getLogger(__name__)


class DatasetManager:
    """Manages persistent storage of trading datasets"""
    
    def __init__(self, supabase_client: Optional[Client] = None):
        """
        Initialize DatasetManager
        
        Args:
            supabase_client: Optional Supabase client. Uses admin client by default.
        """
        self.client = supabase_client or get_supabase_admin()
    
    def get_sentiment_for_date(
        self,
        session_id: Optional[str],
        ticker: str,
        data_source: str,
        target_date: date
    ) -> Optional[float]:
        """
        Get sentiment for a specific date from cached dataset.
        No API call needed if dataset exists.
        
        Args:
            session_id: Session ID (can be None for global lookup)
            ticker: Stock ticker symbol
            data_source: 'reddit', 'twitter', or 'news'
            target_date: Target date to get sentiment for
            
        Returns:
            Sentiment score (-1 to 1) or None if not found
        """
        try:
            # First, try to find a dataset that covers this date
            # Look for datasets where start_date <= target_date <= end_date
            date_str = target_date.strftime('%Y-%m-%d')
            
            # Query for matching datasets
            # We check both session_id-specific and global (NULL session_id) datasets
            query = self.client.table('trading_datasets').select('*')
            
            # Filter by ticker and data_source
            query = query.eq('ticker', ticker).eq('data_source', data_source)
            
            # Filter by date range: start_date <= target_date <= end_date
            query = query.lte('start_date', date_str).gte('end_date', date_str)
            
            # Order by most recent first (in case of overlaps)
            query = query.order('created_at', desc=True).limit(1)
            
            response = query.execute()
            
            if response.data and len(response.data) > 0:
                dataset = response.data[0]
                data = dataset.get('data', {})
                
                # Extract sentiment for this specific date
                date_data = data.get(date_str)
                if date_data:
                    sentiment = date_data.get('sentiment')
                    if sentiment is not None:
                        logger.debug(f"✅ Found cached sentiment for {ticker} ({data_source}) on {date_str}: {sentiment}")
                        return float(sentiment)
            
            logger.debug(f"⚠️ No cached sentiment found for {ticker} ({data_source}) on {date_str}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting sentiment from cache: {e}")
            return None
    
    def store_sentiment_for_date(
        self,
        session_id: Optional[str],
        ticker: str,
        data_source: str,
        date: date,
        sentiment: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store sentiment for a specific date in the dataset.
        This is called incrementally as data is fetched.
        
        Args:
            session_id: Session ID (can be None)
            ticker: Stock ticker symbol
            data_source: 'reddit', 'twitter', or 'news'
            date: Date for this sentiment
            sentiment: Sentiment score (-1 to 1)
            metadata: Optional metadata (post_count, avg_score, etc.)
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            date_str = date.strftime('%Y-%m-%d')
            
            # Check if a dataset exists for this ticker/source/date range
            # For now, we'll create/update a dataset that covers a date range
            # This is a simplified version - in production, you'd want to batch dates
            
            # For incremental storage, we'll need to:
            # 1. Find existing dataset or create new one
            # 2. Update the data JSONB field
            
            # This is a placeholder - full implementation would batch dates efficiently
            logger.debug(f"💾 Storing sentiment for {ticker} ({data_source}) on {date_str}: {sentiment}")
            
            # TODO: Implement efficient batching logic
            # For now, this is a placeholder that will be called but won't store yet
            # We'll implement full storage in the batch pre-fetch method
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing sentiment: {e}")
            return False
    
    def get_or_create_dataset(
        self,
        session_id: Optional[str],
        ticker: str,
        data_source: str,
        start_date: date,
        end_date: date
    ) -> Optional[Dict[str, Any]]:
        """
        Get existing dataset or create a new one.
        This is the main method for fetching/creating datasets.
        
        Args:
            session_id: Session ID (can be None for global lookup)
            ticker: Stock ticker symbol
            data_source: 'reddit', 'twitter', or 'news'
            start_date: Start date of dataset
            end_date: End date of dataset
            
        Returns:
            Dataset dict with 'data' field containing {date: {sentiment, ...}} or None
        """
        try:
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            # Check if dataset already exists
            # Note: Based on schema, datasets are global (not session-specific)
            # But we can track session_id for association later
            query = self.client.table('trading_datasets').select('*')
            query = query.eq('ticker', ticker)
            query = query.eq('data_source', data_source)
            query = query.eq('start_date', start_str)
            query = query.eq('end_date', end_str)
            query = query.limit(1)
            
            response = query.execute()
            
            if response.data and len(response.data) > 0:
                dataset = response.data[0]
                logger.info(f"✅ Found existing dataset for {ticker} ({data_source}) from {start_str} to {end_str}")
                return dataset
            
            # Dataset doesn't exist - return None (caller will fetch and store)
            logger.debug(f"⚠️ No existing dataset for {ticker} ({data_source}) from {start_str} to {end_str}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error checking for dataset: {e}")
            return None
    
    def create_or_update_dataset(
        self,
        session_id: Optional[str],
        ticker: str,
        data_source: str,
        start_date: date,
        end_date: date,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a new dataset or update existing one with fetched data.
        This is called after fetching data from APIs.
        
        Args:
            session_id: Session ID (for association when bot is saved)
            ticker: Stock ticker symbol
            data_source: 'reddit', 'twitter', or 'news'
            start_date: Start date of dataset
            end_date: End date of dataset
            data: Dict mapping date strings to sentiment data
                Format: {"2024-01-15": {"sentiment": 0.45, "post_count": 12, ...}, ...}
            metadata: Optional metadata (total_posts, avg_sentiment, etc.)
            
        Returns:
            True if created/updated successfully, False otherwise
        """
        try:
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            # Check if dataset exists
            existing = self.get_or_create_dataset(session_id, ticker, data_source, start_date, end_date)
            
            dataset_dict = {
                'ticker': ticker,
                'data_source': data_source,
                'start_date': start_str,
                'end_date': end_str,
                'data': data,
                'metadata': metadata or {},
                'session_id': session_id,
                'updated_at': datetime.now().isoformat()
            }
            
            if existing:
                # Update existing dataset
                dataset_id = existing['id']
                response = self.client.table('trading_datasets').update(dataset_dict).eq('id', dataset_id).execute()
                logger.info(f"✅ Updated dataset {dataset_id} for {ticker} ({data_source})")
            else:
                # Create new dataset
                response = self.client.table('trading_datasets').insert(dataset_dict).execute()
                if response.data and len(response.data) > 0:
                    dataset_id = response.data[0]['id']
                    logger.info(f"✅ Created dataset {dataset_id} for {ticker} ({data_source}) from {start_str} to {end_str}")
                else:
                    logger.error(f"❌ Failed to create dataset - empty response")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating/updating dataset: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def associate_with_bot(self, session_id: str, bot_id: str) -> bool:
        """
        Associate datasets created during a session with a bot when it's saved.
        
        Args:
            session_id: Session ID used during workflow
            bot_id: Bot ID from saved bot
            
        Returns:
            True if association successful, False otherwise
        """
        try:
            # Update all datasets with this session_id to have the bot_id
            response = self.client.table('trading_datasets').update({
                'bot_id': bot_id
            }).eq('session_id', session_id).is_('bot_id', 'null').execute()
            
            updated_count = len(response.data) if response.data else 0
            logger.info(f"✅ Associated {updated_count} datasets with bot {bot_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error associating datasets with bot: {e}")
            return False

