# Code Explanation Guide

## Explanation Structure

### 1. Overview (What)
- Purpose of the code
- Input/output
- Where it fits in the system

### 2. How It Works
- Step-by-step walkthrough
- Key algorithms
- Data flow

### 3. Why (Design Decisions)
- Why this approach?
- Trade-offs made
- Alternatives considered

### 4. Dependencies
- What it imports/uses
- What depends on it
- External services

## Common Patterns to Identify

### Creational Patterns
| Pattern | Indicators | Purpose |
|---------|------------|---------|
| Factory | `create_*`, `make_*` methods | Create objects without specifying class |
| Builder | Chained methods, `build()` | Construct complex objects step-by-step |
| Singleton | `_instance`, `get_instance()` | Single global instance |

### Structural Patterns
| Pattern | Indicators | Purpose |
|---------|------------|---------|
| Adapter | Wraps another class | Convert interface |
| Decorator | `@decorator`, wraps function | Add behavior |
| Facade | Simplified API over complex system | Hide complexity |

### Behavioral Patterns
| Pattern | Indicators | Purpose |
|---------|------------|---------|
| Observer | `subscribe`, `notify`, callbacks | Event handling |
| Strategy | Interchangeable algorithms | Select algorithm at runtime |
| Command | `execute()`, action objects | Encapsulate operations |

## Python Specifics

### Magic Methods
```python
__init__    # Constructor
__str__     # String representation (user-friendly)
__repr__    # String representation (debug)
__eq__      # Equality comparison
__hash__    # Hashability (for sets/dicts)
__enter__   # Context manager entry
__exit__    # Context manager exit
__call__    # Make instance callable
__getattr__ # Dynamic attribute access
__iter__    # Make iterable
__next__    # Iterator protocol
```

### Decorators
```python
@property           # Getter
@x.setter          # Setter
@classmethod       # Class method (cls)
@staticmethod      # Static method
@abstractmethod    # Abstract (must override)
@dataclass         # Auto-generate __init__, etc.
@lru_cache         # Memoization
```

### Type Hints
```python
def func(x: int) -> str:           # Basic types
def func(items: list[str]):        # Generic types
def func(x: int | None):           # Union (3.10+)
def func(x: Optional[int]):        # Optional
def func(**kwargs: Unpack[Config]): # TypedDict unpacking
```

## JavaScript/TypeScript Specifics

### Async Patterns
```typescript
// Promise
fetch(url).then(res => res.json()).then(data => ...)

// Async/await
const data = await fetch(url).then(r => r.json())

// Observable (RxJS)
observable.pipe(map(...), filter(...)).subscribe(...)
```

### React Patterns
```typescript
// Custom Hook
function useData() { const [data, setData] = useState() ... }

// HOC
const withAuth = (Component) => (props) => ...

// Render Props
<DataProvider render={(data) => <Child data={data} />} />

// Compound Components
<Select>
  <Select.Option value="a">A</Select.Option>
</Select>
```

## Questions to Answer

1. **Entry Point**: Where does execution start?
2. **Data Flow**: How does data move through the system?
3. **State Management**: Where is state stored? How is it modified?
4. **Error Handling**: What can go wrong? How is it handled?
5. **Side Effects**: What external systems does it interact with?
6. **Performance**: Are there any performance considerations?
7. **Security**: Are there any security implications?
8. **Testing**: How would you test this code?
