#!/usr/bin/env python3
"""
Micro Coding Patterns Collection - Maximum Idea Generation
Every possible coding pattern in minimal form for comprehensive testing
"""

# ========== BASIC PATTERNS ==========

# 1. Null Object Pattern
class NullLogger:
    def log(self, msg): pass

# 2. Singleton (Simple)
class Config:
    _instance = None
    def __new__(cls): 
        if not cls._instance: cls._instance = super().__new__(cls)
        return cls._instance

# 3. Factory Method
def create_handler(type_): 
    return {"json": JsonHandler, "xml": XmlHandler}[type_]()

# 4. Builder Pattern (Fluent)
class Query:
    def __init__(self): self.parts = []
    def select(self, field): self.parts.append(f"SELECT {field}"); return self
    def where(self, cond): self.parts.append(f"WHERE {cond}"); return self

# 5. Command Pattern
class Command:
    def execute(self): raise NotImplementedError

# 6. Observer Pattern (Minimal)
class Subject:
    def __init__(self): self.observers = []
    def notify(self, event): [obs.update(event) for obs in self.observers]

# 7. Strategy Pattern
class Sorter:
    def __init__(self, strategy): self.strategy = strategy
    def sort(self, data): return self.strategy(data)

# 8. Decorator Pattern
def timer(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__}: {time.time() - start:.4f}s")
        return result
    return wrapper

# 9. Adapter Pattern
class LegacyAPI:
    def old_method(self): return "legacy"

class ModernAdapter:
    def __init__(self, legacy): self.legacy = legacy
    def new_method(self): return self.legacy.old_method()

# 10. Template Method
class Algorithm:
    def run(self): self.step1(); self.step2(); self.step3()
    def step1(self): pass  # Override in subclass
    def step2(self): pass  # Override in subclass  
    def step3(self): pass  # Override in subclass

# ========== FUNCTIONAL PATTERNS ==========

# 11. Currying
curry = lambda f: lambda a: lambda b: f(a, b)
add = curry(lambda x, y: x + y)

# 12. Partial Application
from functools import partial
multiply_by_two = partial(lambda x, y: x * y, 2)

# 13. Pipe Operator (Functional Chain)
def pipe(value, *funcs):
    for func in funcs: value = func(value)
    return value

# 14. Memoization
def memoize(func):
    cache = {}
    def wrapper(*args):
        if args not in cache: cache[args] = func(*args)
        return cache[args]
    return wrapper

# 15. Map-Reduce Pattern
from functools import reduce
pipeline = lambda data: reduce(lambda acc, x: acc + x, map(lambda x: x**2, data), 0)

# 16. Monoid Pattern
class Sum:
    def __init__(self, value=0): self.value = value
    def __add__(self, other): return Sum(self.value + other.value)
    @classmethod
    def empty(cls): return cls(0)

# 17. Maybe/Optional Pattern
class Maybe:
    def __init__(self, value): self.value = value
    def map(self, func): return Maybe(func(self.value) if self.value else None)
    def flat_map(self, func): return func(self.value) if self.value else Maybe(None)

# ========== ASYNC PATTERNS ==========

# 18. Async Context Manager
class AsyncResource:
    async def __aenter__(self): return self
    async def __aexit__(self, *args): pass

# 19. Producer-Consumer
import asyncio
async def producer(queue):
    for i in range(5): await queue.put(i)

async def consumer(queue):
    while True: 
        item = await queue.get()
        if item is None: break

# 20. Circuit Breaker
class CircuitBreaker:
    def __init__(self, threshold=3): self.failures = 0; self.threshold = threshold
    def call(self, func, *args):
        if self.failures >= self.threshold: raise Exception("Circuit open")
        try: return func(*args)
        except: self.failures += 1; raise

# ========== DATA PATTERNS ==========

# 21. Repository Pattern
class Repository:
    def __init__(self): self.data = {}
    def save(self, id_, obj): self.data[id_] = obj
    def find(self, id_): return self.data.get(id_)

# 22. Unit of Work
class UnitOfWork:
    def __init__(self): self.changes = []
    def register(self, obj): self.changes.append(obj)
    def commit(self): [change.save() for change in self.changes]

# 23. Active Record Pattern
class Model:
    def save(self): pass  # Save to database
    def delete(self): pass  # Delete from database
    @classmethod
    def find(cls, id_): return cls()

# 24. Data Mapper
class UserMapper:
    def to_dict(self, user): return {"id": user.id, "name": user.name}
    def from_dict(self, data): return User(data["id"], data["name"])

# 25. Specification Pattern
class Specification:
    def is_satisfied_by(self, obj): raise NotImplementedError
    def __and__(self, other): return AndSpec(self, other)
    def __or__(self, other): return OrSpec(self, other)

# ========== EXAMPLE CLASSES FOR PATTERNS ==========
class JsonHandler: pass
class XmlHandler: pass
class User: 
    def __init__(self, id_=None, name=None): self.id = id_; self.name = name

class AndSpec:
    def __init__(self, left, right): self.left = left; self.right = right
    def is_satisfied_by(self, obj): return self.left.is_satisfied_by(obj) and self.right.is_satisfied_by(obj)

class OrSpec:
    def __init__(self, left, right): self.left = left; self.right = right  
    def is_satisfied_by(self, obj): return self.left.is_satisfied_by(obj) or self.right.is_satisfied_by(obj)


if __name__ == "__main__":
    print("TARGET: 25+ Core Micro Coding Patterns Generated!")
    print("Categories covered:")
    print("- Basic Patterns (10): Null Object, Singleton, Factory, Builder, Command...")
    print("- Functional Patterns (7): Currying, Partial, Pipe, Memoize, Map-Reduce...")  
    print("- Async Patterns (3): Context Manager, Producer-Consumer, Circuit Breaker")
    print("- Data Patterns (5): Repository, Unit of Work, Active Record, Mapper...")
    print("+ Helper classes and utilities")
    
    # Demo a few patterns
    print("\nQUICK DEMO:")
    
    # Strategy Pattern Demo
    sorter = Sorter(lambda data: sorted(data, reverse=True))
    print(f"Strategy: {sorter.sort([3,1,2])}")
    
    # Memoization Demo  
    @memoize
    def fib(n): return n if n <= 1 else fib(n-1) + fib(n-2)
    print(f"Memoized Fibonacci: {fib(10)}")
    
    # Maybe Pattern Demo
    result = Maybe(5).map(lambda x: x * 2).map(lambda x: x + 1)
    print(f"Maybe chaining: {result.value}")
    
    print("\nSUCCESS: Ready for comprehensive testing!")