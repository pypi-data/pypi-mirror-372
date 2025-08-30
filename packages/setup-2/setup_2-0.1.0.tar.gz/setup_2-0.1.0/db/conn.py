# # db/conn.py
# import json
# from typing import Dict, Any, List
# from sqlalchemy import create_engine, text
# from pymongo import MongoClient

# class UnifiedDB:
#     def __init__(self, conn_str: str):
#         self.conn_str = conn_str
#         if conn_str.startswith("mysql"):
#             self.db_type = "mysql"
#             self.engine = create_engine(conn_str)
#         elif conn_str.startswith("mongodb"):
#             self.db_type = "mongodb"
#             self.client = MongoClient(conn_str)
#             # extract db name from URI
#             self.db_name = conn_str.rsplit("/", 1)[-1]
#             self.db = self.client[self.db_name]
#         else:
#             raise ValueError(f"Unsupported connection string: {conn_str}")

#     @classmethod
#     def from_config(cls, name: str, path: str = "db_config.json"):
#         with open(path, "r") as f:
#             cfg = json.load(f)
#         conn_str = cfg.get(name)
#         if not conn_str:
#             raise ValueError(f"No connection string for {name}")
#         return cls(conn_str)

#     def query(self, query: str, params: Dict[str, Any] = None, collection: str = None) -> List[Dict[str, Any]]:
#         """
#         Run query on MySQL or MongoDB.
#         For MySQL -> SQL string
#         For Mongo -> query is ignored, pass filter in params + collection
#         """
#         if self.db_type == "mysql":
#             with self.engine.connect() as conn:
#                 result = conn.execute(text(query), params or {})
#                 rows = result.mappings().all()
#                 return [dict(r) for r in rows]

#         elif self.db_type == "mongodb":
#             if not collection:
#                 raise ValueError("Collection name is required for MongoDB")
#             filter_query = params or {}
#             docs = list(self.db[collection].find(filter_query))
#             for d in docs:
#                 d["_id"] = str(d["_id"])  # convert ObjectId to string
#             return docs


# db/conn.py
# from sqlalchemy import create_engine, text
# from pymongo import MongoClient

# def mysql(user: str, password: str, host: str, port: int, database: str = None):
#     """
#     Simple MySQL connection using SQLAlchemy.
#     Returns (engine, connection)
#     """
#     try:
#         conn_str = f"mysql+pymysql://{user}:{password}@{host}:{port}"
#         if database:
#             conn_str += f"/{database}"
        
#         engine = create_engine(conn_str)
#         conn = engine.connect()
        
#         print("✅ MySQL connection established.")
#         return engine, conn
#     except Exception as e:
#         print("❌ MySQL connection failed:", e)
#         return None, None

# # Example usage (for testing)
# if __name__ == "__main__":
#     engine, conn = mysql(user="root", password="root", host="127.0.0.1", port=3306, database="client1_db")
#     if conn:
#         result = conn.execute(text("SELECT DATABASE();"))
#         print("📌 Current DB:", result.fetchone())
#         conn.close()



# db/conn.py
# from sqlalchemy import create_engine, text
# from pymongo import MongoClient
# import sqlite3


# def mysql(user: str, password: str, host: str, port: int, database: str = None):
#     """
#     Simple MySQL connection using SQLAlchemy.
#     Returns (engine, connection)
#     """
#     try:
#         conn_str = f"mysql+pymysql://{user}:{password}@{host}:{port}"
#         if database:
#             conn_str += f"/{database}"

#         engine = create_engine(conn_str)
#         conn = engine.connect()

#         print("✅ MySQL connection established.")
#         return engine, conn
#     except Exception as e:
#         print("❌ MySQL connection failed:", e)
#         return None, None


# def mongodb(uri: str, db_name: str):
#     """
#     Simple MongoDB connection.
#     Returns (client, db)
#     """
#     try:
#         client = MongoClient(uri)
#         db = client[db_name]
#         print("✅ MongoDB connection established.")
#         return client, db
#     except Exception as e:
#         print("❌ MongoDB connection failed:", e)
#         return None, None


# def sqlite(db_path: str):
#     """
#     Simple SQLite connection.
#     Returns (conn, cursor)
#     """
#     try:
#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()
#         print("✅ SQLite connection established.")
#         return conn, cursor
#     except Exception as e:
#         print("❌ SQLite connection failed:", e)
#         return None, None
      
    #   //////////////////////////////////////////////////////////////////////////////////////////////////////
    
    
    # db/conn.py
from sqlalchemy import create_engine
from pymongo import MongoClient
import sqlite3


def mysql(user: str, password: str, host: str, port: int, database: str = None):
    """
    Connect to a MySQL database using SQLAlchemy.
    Returns (engine, connection).
    """
    try:
        conn_str = f"mysql+pymysql://{user}:{password}@{host}:{port}"
        if database:
            conn_str += f"/{database}"

        engine = create_engine(conn_str)
        conn = engine.connect()

        print("✅ MySQL connection established.")
        return engine, conn
    except Exception as e:
        print("❌ MySQL connection failed:", e)
        return None, None


def mongodb(uri: str, db_name: str):
    """
    Connect to a MongoDB database using pymongo.
    Returns (client, db).
    """
    try:
        client = MongoClient(uri)
        db = client[db_name]
        print("✅ MongoDB connection established.")
        return client, db
    except Exception as e:
        print("❌ MongoDB connection failed:", e)
        return None, None


def sqlite(db_path: str):
    """
    Connect to a SQLite database.
    Returns (conn, cursor).
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✅ SQLite connection established.")
        return conn, cursor
    except Exception as e:
        print("❌ SQLite connection failed:", e)
        return None, None
