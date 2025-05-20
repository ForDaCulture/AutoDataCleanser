from db.supabase_client import supabase, get_supabase_client
from datetime import datetime
from typing import Dict, Any, Optional
import json

class AuditLogError(Exception):
    """Custom exception for audit logging errors"""
    pass

def validate_audit_data(user_id: str, action: str, details: Dict[str, Any]) -> None:
    """
    Validate audit log data before insertion.
    Raises AuditLogError if validation fails.
    """
    if not user_id or not isinstance(user_id, str):
        raise AuditLogError("Invalid user_id")
    
    if not action or not isinstance(action, str):
        raise AuditLogError("Invalid action")
    
    if not isinstance(details, dict):
        raise AuditLogError("Details must be a dictionary")
    
    # Ensure details can be serialized to JSON
    try:
        json.dumps(details)
    except (TypeError, ValueError) as e:
        raise AuditLogError(f"Details cannot be serialized to JSON: {str(e)}")

def log_action(
    user_id: str,
    action: str,
    details: Dict[str, Any],
    session_id: Optional[str] = None
) -> None:
    """
    Log an action to the audit_logs table.
    
    Args:
        user_id: The ID of the user performing the action
        action: The type of action being performed
        details: Additional details about the action
        session_id: Optional session ID if the action is related to a cleaning session
    
    Raises:
        AuditLogError: If logging fails
    """
    try:
        # Validate input data
        validate_audit_data(user_id, action, details)
        
        # Prepare audit log entry
        audit_entry = {
            "user_id": user_id,
            "action": action,
            "details": details,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Add session_id if provided
        if session_id:
            audit_entry["session_id"] = session_id
        
        # Get Supabase client and insert log
        client = get_supabase_client()
        result = client.table("audit_logs").insert(audit_entry).execute()
        
        if not result.data:
            raise AuditLogError("Failed to insert audit log")
            
    except Exception as e:
        # Log the error but don't expose internal details
        print(f"Audit logging failed: {str(e)}")
        raise AuditLogError("Failed to log action")

def get_user_audit_logs(
    user_id: str,
    limit: int = 100,
    offset: int = 0
) -> list:
    """
    Retrieve audit logs for a specific user.
    
    Args:
        user_id: The ID of the user
        limit: Maximum number of logs to retrieve
        offset: Number of logs to skip
    
    Returns:
        List of audit log entries
    """
    try:
        client = get_supabase_client()
        result = client.table("audit_logs")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .offset(offset)\
            .execute()
        
        return result.data
    except Exception as e:
        print(f"Failed to retrieve audit logs: {str(e)}")
        return []

def get_session_audit_logs(
    session_id: str,
    limit: int = 100,
    offset: int = 0
) -> list:
    """
    Retrieve audit logs for a specific cleaning session.
    
    Args:
        session_id: The ID of the cleaning session
        limit: Maximum number of logs to retrieve
        offset: Number of logs to skip
    
    Returns:
        List of audit log entries
    """
    try:
        client = get_supabase_client()
        result = client.table("audit_logs")\
            .select("*")\
            .eq("session_id", session_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .offset(offset)\
            .execute()
        
        return result.data
    except Exception as e:
        print(f"Failed to retrieve session audit logs: {str(e)}")
        return [] 