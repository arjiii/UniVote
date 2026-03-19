from typing import Optional
from database import supabase


def log_action(
    actor_id: str,
    actor_role: str,
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    details: Optional[dict] = None,
) -> None:
    """
    Insert a row into the audit_log table.
    Call this at the end of every mutating service operation.
    Failures are silently swallowed so audit errors never break the main flow.
    """
    try:
        supabase.table("audit_log").insert({
            "actor_id": actor_id,
            "actor_role": actor_role,
            "action": action,
            "target_type": target_type,
            "target_id": target_id,
            "details": details,
        }).execute()
    except Exception as exc:
        # Never let audit failures surface to the caller
        print(f"[audit_service] Failed to log action '{action}': {exc}")


def get_audit_log(limit: int = 100) -> list:
    """Retrieve the most recent audit log entries, newest first."""
    result = (
        supabase.table("audit_log")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data
