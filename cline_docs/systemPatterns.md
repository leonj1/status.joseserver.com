# System Patterns

## Architecture
- FastAPI-based REST service
- Modular design with separate routers and controllers
- Clean architecture principles

## Key Technical Decisions
- FastAPI for high performance and modern Python features
- Dependency injection for better testability
- Pydantic models for request/response validation
- Async/await for efficient I/O operations

## Design Patterns
- Repository pattern for data access (if needed)
- Dependency injection for service composition
- Strategy pattern for different health check implementations
- Factory pattern for creating health check instances

## Code Organization
```
src/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── health.py
│   └── core/
│       └── __init__.py
└── tests/
    └── __init__.py