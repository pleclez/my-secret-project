"""
Utility functions for database operations
"""
from typing import Dict, List, Any
import json


def serialize_metadata(metadata: Dict) -> str:
    """Convert metadata dict to JSON string"""
    return json.dumps(metadata) if metadata else None


def deserialize_metadata(metadata_str: str) -> Dict:
    """Convert JSON string to metadata dict"""
    return json.loads(metadata_str) if metadata_str else {}


def build_where_clause(filters: Dict[str, Any]) -> tuple:
    """
    Build WHERE clause from filters dictionary
    
    Args:
        filters: Dictionary of field: value pairs
        
    Returns:
        Tuple of (where_clause_string, params_tuple)
    """
    if not filters:
        return "", ()
    
    conditions = []
    params = []
    
    for field, value in filters.items():
        if value is not None:
            conditions.append(f"{field} = %s")
            params.append(value)
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    return where_clause, tuple(params)


def paginate_query(query: str, page: int = 1, per_page: int = 50) -> str:
    """
    Add pagination to a query
    
    Args:
        query: SQL query string
        page: Page number (1-indexed)
        per_page: Results per page
        
    Returns:
        Query with LIMIT and OFFSET added
    """
    offset = (page - 1) * per_page
    return f"{query} LIMIT {per_page} OFFSET {offset}"

