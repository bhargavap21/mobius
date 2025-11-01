"""
Orchestrator module - provides singleton access to IntelligentOrchestrator
"""
from agents.intelligent_orchestrator import IntelligentOrchestrator

_orchestrator_instance = None

def get_orchestrator() -> IntelligentOrchestrator:
    """
    Get the singleton orchestrator instance

    Returns:
        IntelligentOrchestrator: The orchestrator instance
    """
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = IntelligentOrchestrator()
    return _orchestrator_instance
