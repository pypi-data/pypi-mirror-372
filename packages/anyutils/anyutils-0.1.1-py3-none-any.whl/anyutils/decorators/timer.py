import time
from functools import wraps
from typing import Callable, Any

def timeit(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator to measure the execution time of a function.
    
    Prints the time taken by the decorated function to execute.
    
    Example:
        @timeit
        def sample_function():
            time.sleep(1)
            
        sample_function()
        # Expected output: [timeit] sample_function took 1.00...s
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"[timeit] {func.__name__} took {(end_time - start_time)*1000:.4f}s")
        return result
    return wrapper