"""
Database connection and query utilities
"""
import mysql.connector
from mysql.connector import Error, pooling
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
from utils.config import DB_CONFIG
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Singleton database manager with connection pooling"""

    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._pool is None:
            try:
                self._pool = pooling.MySQLConnectionPool(
                    pool_name="coffee_shop_pool",
                    pool_size=5,
                    pool_reset_session=True,
                    **DB_CONFIG
                )
                logger.info("Database connection pool created successfully")
            except Error as e:
                logger.error(f"Error creating connection pool: {e}")
                raise

    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool"""
        connection = None
        try:
            connection = self._pool.get_connection()
            yield connection
        except Error as e:
            logger.error(f"Error getting connection: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()

    @contextmanager
    def get_cursor(self, dictionary=True):
        """Get a cursor from a pooled connection"""
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=dictionary)
            try:
                yield cursor
                connection.commit()
            except Error as e:
                connection.rollback()
                logger.error(f"Error in cursor operation: {e}")
                raise
            finally:
                cursor.close()

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> bool:
        """Execute a query that doesn't return results (INSERT, UPDATE, DELETE)"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return True
        except Error as e:
            logger.error(f"Error executing query: {e}")
            return False

    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
        """Fetch a single row"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchone()
        except Error as e:
            logger.error(f"Error fetching one: {e}")
            return None

    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """Fetch all rows"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except Error as e:
            logger.error(f"Error fetching all: {e}")
            return []

    def insert(self, query: str, params: Optional[Tuple] = None) -> Optional[int]:
        """Execute INSERT and return last inserted ID"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.lastrowid
        except Error as e:
            logger.error(f"Error inserting: {e}")
            return None

    def execute_many(self, query: str, params_list: List[Tuple]) -> bool:
        """Execute many queries with different parameters"""
        try:
            with self.get_cursor() as cursor:
                cursor.executemany(query, params_list)
                return True
        except Error as e:
            logger.error(f"Error executing many: {e}")
            return False

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as connection:
                if connection.is_connected():
                    db_info = connection.get_server_info()
                    logger.info(f"Successfully connected to MySQL Server version {db_info}")
                    return True
        except Error as e:
            logger.error(f"Error testing connection: {e}")
            return False


# Global database instance
db = DatabaseManager()


# Helper functions for common operations
def create_tables_from_schema(schema_file: str) -> bool:
    """Execute SQL schema file to create tables"""
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]

        with db.get_connection() as connection:
            cursor = connection.cursor()
            for statement in statements:
                if statement:
                    try:
                        cursor.execute(statement)
                    except Error as e:
                        logger.warning(f"Statement execution warning: {e}")
            connection.commit()
            cursor.close()

        logger.info("Database schema created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False


if __name__ == "__main__":
    # Test connection
    if db.test_connection():
        print("✓ Database connection successful!")
    else:
        print("✗ Database connection failed!")
