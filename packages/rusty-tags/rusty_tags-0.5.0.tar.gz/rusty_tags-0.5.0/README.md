# RustyTags

⚠️ **Early Beta** - This library is in active development and APIs may change.

A high-performance HTML generation library that provides a Rust-based Python extension for building HTML/SVG tags. RustyTags offers significant speed improvements over pure Python HTML generation libraries through memory optimization and Rust-powered performance, now featuring FastHTML-style callable syntax, automatic mapping expansion, comprehensive Datastar integration, and full-stack web development utilities.

## What RustyTags Does

RustyTags generates HTML and SVG content programmatically with:
- **Speed**: Rust-powered performance with memory optimization and caching
- **Modern Syntax**: FastHTML-style callable chaining with minimal performance overhead
- **Automatic Mapping Expansion**: Dictionaries automatically expand as tag attributes
- **Datastar Integration**: Complete reactive web development with shorthand attributes and server-sent events
- **Full-Stack Utilities**: Page templates, decorators, async backends, and event handling
- **Type Safety**: Smart type conversion for Python objects (booleans, numbers, strings)
- **Framework Integration**: Supports `__html__`, `_repr_html_`, and `render()` methods
- **Advanced Features**: Custom tags, attribute mapping, complete HTML5/SVG support

## Quick Start

### Installation (Development)

```bash
# Clone and build from source
git clone <repository>
cd rustyTags
maturin develop

# Or build for release
maturin build --release
```

### Basic Usage

```python
from rusty_tags import Div, P, A, Html, Head, Body, Script, CustomTag, Svg, Circle, Text, Button, Input
from rusty_tags.datastar import signals, reactive_class, DS
from rusty_tags.utils import Page, create_template, show

# Simple HTML generation
content = Div(
    P("Hello World", cls="greeting"),
    A("Click here", href="https://example.com", target="_blank")
)
print(content)
# Output: <div><p class="greeting">Hello World</p><a href="https://example.com" target="_blank">Click here</a></div>

# NEW! Automatic Mapping Expansion - dictionaries auto-expand as attributes
content = Div("Content", dict(id="main", class_="container", hidden=False))
print(content)
# Output: <div id="main" class="container">Content</div>

# FastHTML-style callable chaining
content = Div(cls="container")(
    P("Hello World", cls="greeting"),
    A("Click here", href="https://example.com")
)
print(content)
# Output: <div class="container"><p class="greeting">Hello World</p><a href="https://example.com">Click here</a></div>

# Complete HTML document with Page utility
page = Page(
    Div("Main content", cls="container"),
    title="My App",
    datastar=True  # Automatically includes Datastar script
)
print(page)
# Output: <!doctype html><html><head><title>My App</title><script src="..." type="module"></script></head><body><div class="container">Main content</div></body></html>

# Custom tags
custom = CustomTag("my-component", "Content", data_value="123")
print(custom)
# Output: <my-component data-value="123">Content</my-component>

# SVG graphics
svg_graphic = Svg(
    Circle(cx="50", cy="50", r="40", fill="blue"),
    Text("Hello SVG!", x="10", y="30", fill="white"),
    width="100", height="100"
)
print(svg_graphic)
# Output: <svg width="100" height="100"><circle cx="50" cy="50" r="40" fill="blue"></circle><text x="10" y="30" fill="white">Hello SVG!</text></svg>

# Datastar reactive components with shorthand syntax
reactive_counter = Div(
    P(text="$count", cls="counter-display"),
    Button("+", on_click="$count++"),
    Button("-", on_click="$count--"),
    signals={"count": 0},
    cls="counter-app"
)
print(reactive_counter)
# Output: <div class="counter-app" data-signals='{"count":0}'><p class="counter-display" data-text="$count"></p><button data-on-click="$count++">+</button><button data-on-click="$count--">-</button></div>

# Advanced Datastar with action generators
form = Div(
    Input(type="email", bind="$user.email", placeholder="Email"),
    Input(type="password", bind="$user.password", placeholder="Password"),
    Button("Login", on_click=DS.post("/auth/login", data="$user")),
    signals=signals(user={"email": "", "password": ""}),
    cls="login-form"
)
```

## Features

### 🆕 Automatic Mapping Expansion
RustyTags now automatically expands Python dictionaries passed as positional arguments into tag attributes:

```python
# Before: Manual unpacking required
Div("Content", **{"id": "main", "class": "container", "hidden": False})

# Now: Automatic expansion!
Div("Content", dict(id="main", class_="container", hidden=False))
# Output: <div id="main" class="container">Content</div>

# Works with any mapping type and combines with regular kwargs
attrs = {"data-value": 123, "title": "Tooltip"}
Div("Text", attrs, id="element", cls="active")
# Output: <div data-value="123" title="Tooltip" id="element" class="active">Text</div>
```

**Key Features:**
- **Automatic Detection**: Any dict in positional args is expanded as attributes
- **Type Preservation**: Booleans, numbers, strings handled correctly
- **Datastar Compatible**: `ds_` attributes and reactive `cls` dicts preserved
- **Performance Optimized**: Zero overhead expansion at the Rust level

### 🌟 Full-Stack Web Development Utilities

**Page Templates & Decorators:**
```python
from rusty_tags.utils import Page, create_template, page_template

# Ready-to-use page template with Datastar
page = Page(
    Div("Content"),
    title="My App",
    hdrs=(Meta(charset="utf-8"),),
    datastar=True
)

# Decorator for view functions
template = create_template("My Site", datastar=True)

@template.page("Home")
def home():
    return Div("Welcome to my site!")
```

**Async Backend Integration:**
```python
from rusty_tags.backend import on_event, send_stream, process_queue
import asyncio

# Event-driven backend with Blinker integration
@on_event("user_action")
async def handle_user_action(sender, **data):
    # Process user action and yield HTML updates
    yield Div(f"Action processed: {data}")

# Async SSE streaming
async def stream_updates():
    queue = asyncio.Queue()
    async for update in process_queue(queue):
        yield str(update)
```

### Datastar Reactive Integration
- **Shorthand Attributes**: Clean syntax with `signals`, `bind`, `show`, `text`, `on_click`, etc.
- **Action Generators**: Built-in `DS` class for common patterns (`DS.post()`, `DS.get()`, etc.)
- **Backward Compatible**: Full support for `ds_*` prefixed attributes
- **Event Handling**: Comprehensive `on_*` event attribute support
- **State Management**: Built-in signals, computed values, and effects
- **Server-Sent Events**: Full SSE support with `datastar-py` integration
- **Performance Optimized**: Zero overhead for Datastar attribute processing

### FastHTML-Style Callable API
- **Chainable Syntax**: Support for `Div(cls="container")(children...)` patterns
- **Flexible Composition**: Mix traditional and callable styles seamlessly
- **Performance Optimized**: Minimal overhead (6-8%) for callable functionality
- **Smart Returns**: Empty tags return callable builders, populated tags return HTML

### Performance Optimizations
- **Memory Pooling**: Thread-local string pools for efficient memory reuse
- **Lock-free Caching**: Global caches for attribute and tag name transformations
- **String Interning**: Pre-allocated common HTML strings
- **SIMD Ready**: Optimized for modern CPU instruction sets
- **Stack Allocation**: SmallVec for small collections to avoid heap allocation

### Smart Type Conversion
- **Automatic Type Handling**: Booleans, integers, floats, strings
- **Framework Integration**: `__html__()`, `_repr_html_()`, `render()` method support
- **Attribute Mapping**: `cls` → `class`, `_for` → `for`, etc.
- **Error Handling**: Clear error messages for unsupported types

### HTML Features
- **All Standard Tags**: Complete HTML5 tag set with optimized generation
- **Automatic DOCTYPE**: Html tag includes `<!doctype html>` 
- **Custom Tags**: Dynamic tag creation with any tag name
- **Attribute Processing**: Smart attribute key transformation and value conversion

## API Features & Architecture

RustyTags provides clean, intuitive APIs with multiple styles and full-stack capabilities:

```python
# Traditional style with mapping expansion
from rusty_tags import Div, P, Input, Button
content = Div(
    P("Text", dict(class_="highlight", data_id="p1")),
    cls="container"
)

# FastHTML-style callable chaining
content = Div(cls="container")(P("Text", _class="highlight"))

# Full-stack reactive application
from rusty_tags.datastar import signals, reactive_class, DS
from rusty_tags.backend import on_event
from rusty_tags.utils import Page, create_template

# Backend event handler
@on_event("todo_updated")
async def handle_todo_update(sender, **data):
    # Return HTML update
    yield Div(f"Todo {data['id']} updated!", cls="notification")

# Interactive todo application
def todo_app():
    return Page(
        Div(
            Input(
                type="text", 
                bind="$newTodo", 
                placeholder="Add todo...",
                on_keyup="event.key === 'Enter' && $addTodo()"
            ),
            Button("Add", on_click="$addTodo()"),
            Div(
                # Dynamic todo list
                show="$todos.length > 0",
                effect="console.log('Todos updated:', $todos)"
            ),
            signals=signals(
                newTodo="",
                todos=[]
            ),
            cls="todo-app"
        ),
        title="Todo App",
        datastar=True
    )

# Page template decorator
template = create_template("My App", datastar=True)

@template.page("Dashboard")  
def dashboard():
    return Div("Welcome to dashboard!", dict(role="main", cls="dashboard"))
```

### 📦 **Module Structure**

**Core Engine (`rusty_tags.*`):**
- High-performance Rust-based HTML/SVG tag generation
- Automatic mapping expansion and type conversion
- FastHTML-style callable syntax support

**Datastar Integration (`rusty_tags.datastar`):**
- Shorthand attribute support and action generators
- Server-sent events with `datastar-py` integration
- Reactive state management utilities

**Full-Stack Utilities (`rusty_tags.utils`):**
- Page templates and layout management  
- Function decorators for view composition
- IPython/Jupyter integration with `show()`

**Async Backend (`rusty_tags.backend`):**
- Event-driven architecture with Blinker signals
- Async SSE streaming and queue processing
- Concurrent event handler execution

## Datastar Integration

RustyTags provides comprehensive Datastar support for building reactive web applications:

### Shorthand Attributes

All Datastar attributes support clean shorthand syntax:

```python
# Before (still supported)
Div(ds_signals={"count": 0}, ds_show="$visible", ds_on_click="$increment()")

# After (new shorthand)
Div(signals={"count": 0}, show="$visible", on_click="$increment()")
```

### Supported Datastar Attributes

**Core Attributes:**
- `signals` → `data-signals` - Component state management
- `bind` → `data-bind` - Two-way data binding
- `show` → `data-show` - Conditional visibility
- `text` → `data-text` - Dynamic text content
- `attrs` → `data-attrs` - Dynamic attributes
- `style` → `data-style` - Dynamic styling

**Event Attributes:**
- `on_click`, `on_hover`, `on_submit`, `on_focus`, `on_blur`
- `on_keydown`, `on_change`, `on_input`, `on_load`
- `on_intersect`, `on_interval`, `on_raf`, `on_resize`

**Advanced Attributes:**
- `effect` → `data-effect` - Side effects
- `computed` → `data-computed` - Computed values
- `ref` → `data-ref` - Element references
- `indicator` → `data-indicator` - Loading states
- `persist` → `data-persist` - State persistence
- `ignore` → `data-ignore` - Skip processing

### Complete Example

```python
from rusty_tags import Div, Button, Input, Span
from rusty_tags.datastar import signals, reactive_class, DS

# Interactive counter with Datastar
counter_app = Div(
    Span(text="$count", cls="display"),
    Div(
        Button("-", on_click="$count--"),
        Button("+", on_click="$count++"),
        Button("Reset", on_click=DS.set("count", 0)),
        cls="controls"
    ),
    Input(
        type="range",
        bind="$count",
        attrs={"min": "0", "max": "100"}
    ),
    signals={"count": 50},
    effect="console.log('Count changed:', $count)",
    cls="counter-app"
)
```

## Performance

RustyTags significantly outperforms pure Python HTML generation:
- 3-10x faster than equivalent Python code
- Optimized memory usage with pooling and interning
- Aggressive compiler optimizations in release builds

## Development Status

🚧 **Early Beta**: While the core functionality is stable and tested, this library is still in early development. Breaking changes may occur in future versions. Production use is not recommended yet.

### Current Features ✅
- **Core Engine**: All HTML5 and SVG tags with Rust performance
- **Mapping Expansion**: Automatic dict-to-attributes expansion
- **Callable API**: FastHTML-style chainable syntax
- **Datastar Integration**: Complete reactive web development stack
- **Full-Stack Utilities**: Page templates, decorators, async backends
- **Event System**: Blinker-based event handling with async support
- **Server-Sent Events**: Real-time updates with datastar-py integration
- **Type Safety**: Smart type conversion and attribute mapping
- **Performance**: Memory optimization, caching, and Rust-powered speed
- **Custom Tags**: Dynamic tag creation and framework integration

### Planned Features 🔄
- **Template Engine**: Jinja2/Mako integration for server-side rendering  
- **Streaming HTML**: Chunked response generation for large documents
- **PyPI Distribution**: Official package releases and versioning
- **Developer Tools**: Hot reload, debugging utilities, and performance profilers

### Dependencies & Integration

**Core Dependencies:**
- `datastar-py`: Official Datastar Python SDK for SSE and attributes
- `blinker`: Signal/event system for backend event handling
- `maturin`: Rust-Python build system for performance-critical code

**Framework Integration:**
- **FastAPI**: Native async support with SSE streaming
- **Flask**: Compatible with Jinja2 templates and request contexts
- **Django**: Template integration and ORM query rendering
- **IPython/Jupyter**: Built-in `show()` function for notebook display
- **Starlette**: ASGI compatibility with streaming responses

## Build from Source

```bash
# Development build
maturin develop

# Release build with optimizations
maturin build --release

# Run tests
python test_complex.py
python stress_test.py
```

## Requirements

**Runtime:**
- Python 3.8+
- `datastar-py` (official Datastar Python SDK)
- `blinker` (signal/event system)

**Development/Building:**
- Rust 1.70+
- Maturin for building Rust extensions
- Optional: IPython/Jupyter for `show()` functionality

## License

[Add your license here]