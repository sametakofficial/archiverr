"""MongoDB Connection Manager - Motor async client"""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class Database:
    """
    Professional MongoDB connection manager.
    
    Features:
    - Async Motor client
    - Connection pooling
    - Singleton pattern
    - Graceful cleanup
    """
    
    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect(cls, uri: str, database_name: str, **kwargs):
        """
        Connect to MongoDB.
        
        Args:
            uri: MongoDB connection URI
            database_name: Database name
            **kwargs: Additional Motor client options
        """
        if cls._client is None:
            # Default options for production
            options = {
                'maxPoolSize': 10,
                'minPoolSize': 2,
                'maxIdleTimeMS': 30000,
                'serverSelectionTimeoutMS': 5000,
                **kwargs
            }
            
            cls._client = AsyncIOMotorClient(uri, **options)
            cls._database = cls._client[database_name]
            
            # Verify connection
            await cls._client.admin.command('ping')
    
    @classmethod
    async def disconnect(cls):
        """Close MongoDB connection"""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._database = None
    
    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if cls._database is None:
            raise RuntimeError("Database not connected. Call Database.connect() first.")
        return cls._database
    
    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        """Get client instance"""
        if cls._client is None:
            raise RuntimeError("Database not connected. Call Database.connect() first.")
        return cls._client
