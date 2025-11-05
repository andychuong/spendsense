"""Example usage of persona assignment service."""

import uuid
from sqlalchemy.orm import Session

from app.features.persona_assignment import PersonaAssignmentService

# Example: Assign persona to a user
def example_assign_persona(db_session: Session, user_id: uuid.UUID):
    """
    Example usage of persona assignment.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID to assign persona to
    """
    # Initialize service
    service = PersonaAssignmentService(db_session)

    # Assign persona (signals will be generated automatically)
    result = service.assign_persona(user_id)

    print(f"Persona Assignment for User {user_id}:")
    print(f"  Persona ID: {result['persona_id']}")
    print(f"  Persona Name: {result['persona_name']}")
    print(f"  Rationale: {result['rationale']}")
    print(f"  Persona Changed: {result['persona_changed']}")
    print(f"  Assigned At: {result['assigned_at']}")

    return result


# Example: Assign persona with pre-computed signals
def example_assign_persona_with_signals(
    db_session: Session,
    user_id: uuid.UUID,
    signals_30d: dict,
    signals_180d: dict,
):
    """
    Example with pre-computed signals.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID to assign persona to
        signals_30d: Pre-computed signals for 30-day window
        signals_180d: Pre-computed signals for 180-day window
    """
    service = PersonaAssignmentService(db_session)

    # Assign persona with pre-computed signals
    result = service.assign_persona(
        user_id,
        signals_30d=signals_30d,
        signals_180d=signals_180d,
    )

    print(f"Persona Assignment for User {user_id}:")
    print(f"  Persona: {result['persona_name']} (ID: {result['persona_id']})")
    print(f"  Rationale: {result['rationale']}")

    return result



