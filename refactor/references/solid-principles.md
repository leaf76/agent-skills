# Refactoring Reference

## SOLID Principles

### S - Single Responsibility Principle
A class should have only one reason to change.

```python
# ❌ Bad: Multiple responsibilities
class User:
    def save_to_db(self): ...
    def send_email(self): ...
    def generate_report(self): ...

# ✅ Good: Single responsibility
class User: ...
class UserRepository: ...
class EmailService: ...
class ReportGenerator: ...
```

### O - Open/Closed Principle
Open for extension, closed for modification.

```python
# ❌ Bad: Modifying existing code
def calculate_area(shape):
    if shape.type == "circle":
        return math.pi * shape.radius ** 2
    elif shape.type == "rectangle":
        return shape.width * shape.height
    # Need to modify for each new shape

# ✅ Good: Extend without modifying
class Shape(ABC):
    @abstractmethod
    def area(self): pass

class Circle(Shape):
    def area(self): return math.pi * self.radius ** 2
```

### L - Liskov Substitution Principle
Subtypes must be substitutable for their base types.

```python
# ❌ Bad: Square breaks Rectangle contract
class Rectangle:
    def set_width(self, w): self.width = w
    def set_height(self, h): self.height = h

class Square(Rectangle):
    def set_width(self, w): 
        self.width = self.height = w  # Breaks LSP

# ✅ Good: Separate hierarchies
class Shape(ABC):
    @abstractmethod
    def area(self): pass
```

### I - Interface Segregation Principle
Clients shouldn't depend on interfaces they don't use.

```python
# ❌ Bad: Fat interface
class Worker(ABC):
    @abstractmethod
    def work(self): pass
    @abstractmethod
    def eat(self): pass  # Robots don't eat

# ✅ Good: Segregated interfaces
class Workable(ABC):
    @abstractmethod
    def work(self): pass

class Eatable(ABC):
    @abstractmethod
    def eat(self): pass
```

### D - Dependency Inversion Principle
Depend on abstractions, not concretions.

```python
# ❌ Bad: Direct dependency
class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # Concrete dependency

# ✅ Good: Depend on abstraction
class UserService:
    def __init__(self, db: Database):
        self.db = db  # Injected abstraction
```

## Common Refactoring Patterns

### Extract Method
```python
# Before
def process():
    # validation
    if not name: raise Error()
    if not email: raise Error()
    # processing
    result = compute(data)
    return result

# After
def process():
    validate_input(name, email)
    return compute(data)

def validate_input(name, email):
    if not name: raise Error()
    if not email: raise Error()
```

### Extract Class
Move related fields and methods to a new class.

### Replace Conditional with Polymorphism
```python
# Before
def get_speed(vehicle_type):
    if vehicle_type == "car": return 100
    if vehicle_type == "bike": return 30

# After
class Vehicle(ABC):
    @abstractmethod
    def speed(self): pass

class Car(Vehicle):
    def speed(self): return 100
```

### Introduce Parameter Object
```python
# Before
def search(name, min_age, max_age, city, country):
    ...

# After
@dataclass
class SearchCriteria:
    name: str
    min_age: int
    max_age: int
    city: str
    country: str

def search(criteria: SearchCriteria):
    ...
```

## Code Smells

| Smell | Solution |
|-------|----------|
| Long Method | Extract Method |
| Large Class | Extract Class |
| Long Parameter List | Parameter Object |
| Duplicated Code | Extract Method/Class |
| Feature Envy | Move Method |
| Data Clumps | Extract Class |
| Primitive Obsession | Value Objects |
| Switch Statements | Polymorphism |
| Parallel Inheritance | Merge hierarchies |
| Lazy Class | Inline Class |
| Speculative Generality | Remove unused abstractions |
| Message Chains | Hide Delegate |
| Middle Man | Remove Middle Man |
| Comments | Rename, Extract Method |
