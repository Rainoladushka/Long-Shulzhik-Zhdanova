import functools
from collections import OrderedDict
from typing import Callable, Any, Tuple

# Decorator with caching functionality
def caching_designator(cache_depth: int = 128):
    def decorator(func: Callable):
        # Cache storage with limited size (FIFO)
        cache = OrderedDict()

        @functools.wraps(func)
        def wrapper(*args: Tuple[Any], **kwargs: dict) -> Any:
            # Create a key based on function arguments to identify unique calls
            key = (args, frozenset(kwargs.items()))

            # Check if the result is in the cache
            if key in cache:
                print(f"Cache hit for arguments: {args} {kwargs}")
                return cache[key]

            # Compute the result since it's not in cache
            result = func(*args, **kwargs)

            # Add the result to the cache
            cache[key] = result
            print(f"Cache miss for arguments: {args} {kwargs}. Caching result.")

            # Maintain cache depth limit
            if len(cache) > cache_depth:
                removed_key, _ = cache.popitem(last=False)  # Remove oldest item
                print(f"Cache depth exceeded. Removing oldest cached result for arguments: {removed_key}")

            return result

        return wrapper
    return decorator

# Example usage:
@caching_designator(cache_depth=3)
def compute_square(x):
    print(f"Computing square of {x}")
    return x * x

@caching_designator(cache_depth=2)
def compute_sum(x, y):
    print(f"Computing sum of {x} and {y}")
    return x + y

# Testing the functions
print(compute_square(4))  # Cache miss
print(compute_square(4))  # Cache hit

print(compute_sum(2, 3))  # Cache miss
print(compute_sum(2, 3))  # Cache hit
print(compute_sum(5, 7))  # Cache miss
print(compute_sum(2, 3))  # Cache miss (previous entry removed due to depth limit)
