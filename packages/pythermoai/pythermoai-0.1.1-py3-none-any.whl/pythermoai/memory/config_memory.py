# import libs
import uuid


def generate_thread_id():
    return str(uuid.uuid4())


def generate_thread():
    """Generate a thread"""
    thread_id = generate_thread_id()
    thread = {
        'configurable': {
            'thread_id': thread_id
        }
    }
    return thread, thread_id
