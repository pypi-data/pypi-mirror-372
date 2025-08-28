import time
from functools import wraps

#  A decorator that measures and prints the execution time of a function.
def time_it(func):
    @wraps(func) 
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds.")
        return result
    return wrapper

#how to use
if __name__== "__main__":
    @time_it
    def say_hello():
        print("Hello world!")  
    say_hello()