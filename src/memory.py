from langgraph.checkpoint.memory import MemorySaver

def get_memory_saver():
    """
    Returns an in-memory checkpointer for storing conversation history.
    """
    return MemorySaver()