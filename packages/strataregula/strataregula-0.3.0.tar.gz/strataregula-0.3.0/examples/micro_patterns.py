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

# ========== CONCURRENCY PATTERNS ==========

# 26. Thread Pool
from concurrent.futures import ThreadPoolExecutor
def process_parallel(items, func):
    with ThreadPoolExecutor() as executor:
        return list(executor.map(func, items))

# 27. Lock-Free Counter (Atomic)
import threading
class AtomicCounter:
    def __init__(self): self.value = 0; self.lock = threading.Lock()
    def increment(self): 
        with self.lock: self.value += 1

# 28. Event Bus
class EventBus:
    def __init__(self): self.handlers = {}
    def subscribe(self, event, handler): 
        self.handlers.setdefault(event, []).append(handler)
    def publish(self, event, data): 
        [h(data) for h in self.handlers.get(event, [])]

# ========== VALIDATION PATTERNS ==========

# 29. Chain of Responsibility
class Validator:
    def __init__(self, next_validator=None): self.next = next_validator
    def validate(self, data): 
        if self.check(data) and self.next: return self.next.validate(data)
        return not self.check(data)

# 30. Schema Validation
def validate_schema(schema):
    def decorator(func):
        def wrapper(data):
            for key, type_ in schema.items():
                if not isinstance(data.get(key), type_): 
                    raise ValueError(f"Invalid {key}")
            return func(data)
        return wrapper
    return decorator

# ========== ERROR HANDLING PATTERNS ==========

# 31. Result Type
class Result:
    def __init__(self, value=None, error=None): self.value = value; self.error = error
    def is_success(self): return self.error is None
    def map(self, func): return Result(func(self.value)) if self.is_success() else self

# 32. Retry Pattern
def retry(max_attempts=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try: return func(*args, **kwargs)
                except Exception as e: 
                    if attempt == max_attempts - 1: raise e
        return wrapper
    return decorator

# ========== CACHING PATTERNS ==========

# 33. LRU Cache
class LRUCache:
    def __init__(self, capacity): 
        self.capacity = capacity; self.cache = {}; self.order = []
    def get(self, key):
        if key in self.cache: 
            self.order.remove(key); self.order.append(key)
            return self.cache[key]
    def put(self, key, value):
        if len(self.cache) >= self.capacity: 
            oldest = self.order.pop(0); del self.cache[oldest]
        self.cache[key] = value; self.order.append(key)

# 34. Write-Through Cache
class WriteThruCache:
    def __init__(self, backend): self.cache = {}; self.backend = backend
    def get(self, key): 
        if key not in self.cache: self.cache[key] = self.backend.get(key)
        return self.cache[key]
    def put(self, key, value): self.cache[key] = value; self.backend.put(key, value)

# ========== STREAMING PATTERNS ==========

# 35. Generator Pipeline
def read_lines(): yield from ["line1", "line2", "line3"]
def process_lines(lines): yield from (line.upper() for line in lines)
def save_lines(lines): [print(line) for line in lines]

# 36. Backpressure Handler
class BackpressureBuffer:
    def __init__(self, max_size=100): self.buffer = []; self.max_size = max_size
    def add(self, item):
        if len(self.buffer) >= self.max_size: self.buffer.pop(0)
        self.buffer.append(item)

# ========== CONFIGURATION PATTERNS ==========

# 37. Configuration Builder
class ConfigBuilder:
    def __init__(self): self.config = {}
    def set(self, key, value): self.config[key] = value; return self
    def build(self): return self.config.copy()

# 38. Environment Adapter
import os
class EnvConfig:
    def get(self, key, default=None): return os.getenv(key, default)
    def get_int(self, key, default=0): return int(os.getenv(key, default))

# ========== PLUGIN PATTERNS ==========

# 39. Plugin Registry
class PluginRegistry:
    def __init__(self): self.plugins = {}
    def register(self, name, plugin): self.plugins[name] = plugin
    def get(self, name): return self.plugins.get(name)

# 40. Hook System
class HookSystem:
    def __init__(self): self.hooks = {}
    def add_hook(self, name, func): self.hooks.setdefault(name, []).append(func)
    def execute_hooks(self, name, *args): [hook(*args) for hook in self.hooks.get(name, [])]

# ========== TESTING PATTERNS ==========

# 41. Mock Object
class Mock:
    def __init__(self): self.calls = []
    def __getattr__(self, name): 
        def method(*args, **kwargs): self.calls.append((name, args, kwargs))
        return method

# 42. Spy Pattern
class Spy:
    def __init__(self, target): self.target = target; self.calls = []
    def __getattr__(self, name):
        def method(*args, **kwargs):
            result = getattr(self.target, name)(*args, **kwargs)
            self.calls.append((name, args, kwargs, result))
            return result
        return method

# ========== STATE PATTERNS ==========

# 43. State Machine
class StateMachine:
    def __init__(self, initial_state): self.state = initial_state; self.transitions = {}
    def add_transition(self, from_state, event, to_state): 
        self.transitions[(from_state, event)] = to_state
    def trigger(self, event): 
        self.state = self.transitions.get((self.state, event), self.state)

# 44. Memento Pattern
class Memento:
    def __init__(self, state): self.state = state

class Originator:
    def __init__(self): self.state = None
    def create_memento(self): return Memento(self.state)
    def restore_memento(self, memento): self.state = memento.state

# ========== COLLECTION PATTERNS ==========

# 45. Fluent Collection
class FluentList:
    def __init__(self, items): self.items = items
    def map(self, func): return FluentList([func(x) for x in self.items])
    def filter(self, pred): return FluentList([x for x in self.items if pred(x)])
    def to_list(self): return self.items

# 46. Lazy Collection
class LazyList:
    def __init__(self, generator): self.generator = generator; self._items = None
    def __iter__(self): 
        if self._items is None: self._items = list(self.generator)
        return iter(self._items)

# ========== SERIALIZATION PATTERNS ==========

# 47. Visitor Pattern (for serialization)
class JSONVisitor:
    def visit_dict(self, obj): return {k: self.visit(v) for k, v in obj.items()}
    def visit_list(self, obj): return [self.visit(x) for x in obj]
    def visit(self, obj): return getattr(self, f"visit_{type(obj).__name__.lower()}", lambda x: x)(obj)

# 48. Encoder/Decoder Pattern
class Base64Codec:
    @staticmethod
    def encode(data): import base64; return base64.b64encode(data.encode()).decode()
    @staticmethod  
    def decode(data): import base64; return base64.b64decode(data.encode()).decode()

# ========== DEPENDENCY INJECTION PATTERNS ==========

# 49. Service Locator
class ServiceLocator:
    services = {}
    @classmethod
    def register(cls, name, service): cls.services[name] = service
    @classmethod
    def get(cls, name): return cls.services[name]

# 50. Dependency Injection Container
class DIContainer:
    def __init__(self): self.services = {}; self.instances = {}
    def register(self, interface, implementation): self.services[interface] = implementation
    def resolve(self, interface):
        if interface not in self.instances:
            self.instances[interface] = self.services[interface]()
        return self.instances[interface]


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
    print("🎯 50 Micro Coding Patterns Generated!")
    print("Categories covered:")
    print("- Basic Patterns (10)")
    print("- Functional Patterns (7)")
    print("- Async Patterns (3)")
    print("- Data Patterns (5)")
    print("- Concurrency Patterns (3)")
    print("- Validation Patterns (2)")
    print("- Error Handling Patterns (2)")
    print("- Caching Patterns (2)")
    print("- Streaming Patterns (2)")
    print("- Configuration Patterns (2)")
    print("- Plugin Patterns (2)")
    print("- Testing Patterns (2)")
    print("- State Patterns (2)")
    print("- Collection Patterns (2)")
    print("- Serialization Patterns (2)")
    print("- Dependency Injection Patterns (2)")