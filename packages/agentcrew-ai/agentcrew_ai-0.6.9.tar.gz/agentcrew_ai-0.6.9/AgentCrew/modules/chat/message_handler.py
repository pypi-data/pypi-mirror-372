# Backward compatibility import - the main functionality has been moved to the message/ package
from .message.base import Observable, Observer
from .message.handler import MessageHandler

# For backward compatibility, we still export the main classes
__all__ = ["Observable", "Observer", "MessageHandler"]
