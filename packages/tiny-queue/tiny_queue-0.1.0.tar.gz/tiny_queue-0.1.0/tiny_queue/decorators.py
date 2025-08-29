def queue_task(queue):
    def decorator(func):
        def wrapper(*args, **kwargs):
            queue.enqueue((func.__name__, args, kwargs))
        return wrapper
    return decorator
