"""Execution Repository - Time-series data management"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from ..database import Database


class ExecutionRepository:
    """
    Professional repository for execution documents.
    
    Responsibilities:
    - Save execution records
    - Query executions (time-series)
    - Aggregation statistics
    - Cleanup (TTL handled by MongoDB)
    """
    
    def __init__(self):
        self.db = Database.get_database()
        self.collection = self.db.executions
    
    async def save_execution(self, api_response: Dict[str, Any]) -> str:
        """
        Save execution to MongoDB.
        
        Args:
            api_response: Complete API response dict
            
        Returns:
            Execution ID (string)
        """
        # Convert ISO strings to datetime for proper indexing
        execution = api_response.copy()
        execution['started_at'] = datetime.fromisoformat(
            execution['execution']['started_at'].replace('Z', '+00:00')
        )
        execution['finished_at'] = datetime.fromisoformat(
            execution['execution']['finished_at'].replace('Z', '+00:00')
        )
        
        # Extract top-level fields for indexing
        execution['duration_ms'] = execution['execution']['duration_ms']
        execution['success'] = execution['execution']['success']
        
        # Remove nested execution (flattened)
        del execution['execution']
        
        # Insert
        result = await self.collection.insert_one(execution)
        return str(result.inserted_id)
    
    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution by ID"""
        return await self.collection.find_one({'_id': ObjectId(execution_id)})
    
    async def get_latest_executions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest executions (most recent first)"""
        cursor = self.collection.find().sort('started_at', -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_executions_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get executions within date range"""
        cursor = self.collection.find({
            'started_at': {'$gte': start_date, '$lte': end_date}
        }).sort('started_at', -1)
        return await cursor.to_list(length=None)
    
    async def get_failed_executions(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get failed executions in last N days"""
        since = datetime.now() - timedelta(days=days)
        cursor = self.collection.find({
            'success': False,
            'started_at': {'$gte': since}
        }).sort('started_at', -1)
        return await cursor.to_list(length=None)
    
    async def search_by_file_path(self, path_pattern: str) -> List[Dict[str, Any]]:
        """Search executions by file path (regex)"""
        cursor = self.collection.find({
            'matches.input_path': {'$regex': path_pattern, '$options': 'i'}
        }).sort('started_at', -1)
        return await cursor.to_list(length=None)
    
    async def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get execution statistics for last N days"""
        since = datetime.now() - timedelta(days=days)
        
        pipeline = [
            {'$match': {'started_at': {'$gte': since}}},
            {'$group': {
                '_id': None,
                'total_executions': {'$sum': 1},
                'successful_executions': {
                    '$sum': {'$cond': ['$success', 1, 0]}
                },
                'failed_executions': {
                    '$sum': {'$cond': ['$success', 0, 1]}
                },
                'total_matches_processed': {'$sum': '$total_matches'},
                'avg_duration_ms': {'$avg': '$duration_ms'},
                'total_size_bytes': {'$sum': '$total_size_bytes'}
            }}
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        return result[0] if result else {}
    
    async def get_daily_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily execution statistics"""
        since = datetime.now() - timedelta(days=days)
        
        pipeline = [
            {'$match': {'started_at': {'$gte': since}}},
            {'$group': {
                '_id': {
                    '$dateToString': {'format': '%Y-%m-%d', 'date': '$started_at'}
                },
                'count': {'$sum': 1},
                'avg_duration': {'$avg': '$duration_ms'},
                'total_matches': {'$sum': '$total_matches'},
                'success_rate': {
                    '$avg': {'$cond': ['$success', 1.0, 0.0]}
                }
            }},
            {'$sort': {'_id': 1}}
        ]
        
        return await self.collection.aggregate(pipeline).to_list(length=None)
    
    async def update_config_snapshot(self, config_hash: str, config: Dict[str, Any]):
        """Update config_snapshots collection (optional deduplication)"""
        snapshots = self.db.config_snapshots
        
        await snapshots.update_one(
            {'config_hash': config_hash},
            {
                '$setOnInsert': {
                    'config': config,
                    'first_used': datetime.now(),
                    'created_at': datetime.now()
                },
                '$set': {'last_used': datetime.now()},
                '$inc': {'execution_count': 1}
            },
            upsert=True
        )
    
    async def ensure_indexes(self):
        """Create indexes for optimal query performance"""
        # Time-series index (most common)
        await self.collection.create_index([('started_at', -1)])
        
        # Status filtering
        await self.collection.create_index([
            ('success', 1),
            ('started_at', -1)
        ])
        
        # Plugin filtering
        await self.collection.create_index([
            ('enabled_plugins', 1),
            ('started_at', -1)
        ])
        
        # File path search
        await self.collection.create_index([('matches.input_path', 1)])
        
        # TTL index (automatic cleanup after 90 days)
        await self.collection.create_index(
            [('started_at', 1)],
            expireAfterSeconds=7776000  # 90 days
        )
