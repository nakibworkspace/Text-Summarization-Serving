# Test-Driven Development with FastAPI and Docker - Hands-On Lab

![Continuous Integration and Delivery](https://github.com/YOUR_GITHUB_NAMESPACE/fastapi-tdd-docker/workflows/Continuous%20Integration%20and%20Delivery/badge.svg?branch=main)

## 🎯 Learning Objectives

By completing this hands-on lab, you will learn:

- **Test-Driven Development (TDD)**: Write tests before implementing features
- **FastAPI Framework**: Build modern, fast APIs with Python
- **Docker & Docker Compose**: Containerize applications for consistency
- **Database Management**: Use Tortoise ORM with PostgreSQL
- **CI/CD Pipelines**: Automate testing and deployment with GitHub Actions
- **Code Quality**: Implement linting, formatting, and code coverage
- **Background Tasks**: Handle async operations efficiently
- **API Design**: Follow RESTful best practices

## 📚 Lab Overview

This lab builds a **Text Summarization API** that:
- Accepts URLs and generates article summaries
- Uses asynchronous processing with background tasks
- Implements full CRUD operations
- Follows TDD principles throughout development
- Deploys to production with CI/CD automation

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │─────▶│  FastAPI App │─────▶│  PostgreSQL │
│  (HTTPie)   │      │   (Uvicorn)  │      │  Database   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ Newspaper3k  │
                     │ (Summarizer) │
                     └──────────────┘
```

## 🛠️ Prerequisites

- Docker (version 28.0+)
- Docker Compose (version 2.34+)
- Git
- A GitHub account
- A Heroku account (optional, for deployment)
- HTTPie or curl (for API testing)

## 📁 Project Structure

```
fastapi-tdd-docker/
├── .github/
│   └── workflows/
│       └── main.yml              # GitHub Actions CI/CD
├── project/
│   ├── app/
│   │   ├── api/
│   │   │   ├── crud.py          # Database operations
│   │   │   ├── ping.py          # Health check endpoint
│   │   │   └── summaries.py     # Summary CRUD endpoints
│   │   ├── models/
│   │   │   ├── pydantic.py      # Request/Response schemas
│   │   │   └── tortoise.py      # Database models
│   │   ├── config.py            # Application configuration
│   │   ├── db.py                # Database initialization
│   │   ├── main.py              # FastAPI app creation
│   │   └── summarizer.py        # Text summarization logic
│   ├── db/
│   │   ├── Dockerfile           # PostgreSQL Docker image
│   │   └── create.sql           # Database initialization
│   ├── tests/
│   │   ├── conftest.py          # Test fixtures
│   │   ├── test_ping.py         # Health check tests
│   │   ├── test_summaries.py   # Integration tests
│   │   └── test_summaries_unit.py # Unit tests
│   ├── migrations/              # Database migrations
│   ├── Dockerfile               # Development Docker image
│   ├── Dockerfile.prod          # Production Docker image
│   ├── entrypoint.sh            # Container startup script
│   ├── requirements.txt         # Python dependencies
│   └── requirements-dev.txt     # Development dependencies
├── docker-compose.yml           # Docker services configuration
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd fastapi-tdd-docker
```

### 2. Build and Start Services
```bash
docker compose up -d --build
```

### 3. Apply Database Migrations
```bash
docker compose exec web aerich upgrade
```

### 4. Test the API
```bash
# Health check
http GET http://localhost:8004/ping

# Create a summary
http --json POST http://localhost:8004/summaries/ url=https://testdriven.io

# Get all summaries
http GET http://localhost:8004/summaries/

# Get specific summary
http GET http://localhost:8004/summaries/1/
```

### 5. Run Tests
```bash
docker compose exec web python -m pytest
```

## 📖 Learning Path

Follow this path to understand the project step-by-step:

### **Phase 1: Foundation (Modules 1-3)**

#### Module 1: Getting Started with FastAPI
**Concepts Covered:**
- FastAPI basics and ASGI servers
- Dependency injection
- Configuration management with Pydantic
- Async/await in Python

**Key Files:**
- `project/app/main.py` - Entry point
- `project/app/config.py` - Settings management
- `project/app/api/ping.py` - Simple endpoint

**Code Explanation:**

```python
# app/main.py - Application Factory Pattern
def create_application() -> FastAPI:
    application = FastAPI()
    # Register database
    # Register routes
    return application
```
This pattern allows creating fresh app instances for testing.

```python
# app/config.py - Configuration with Pydantic
class Settings(BaseSettings):
    environment: str = "dev"
    testing: bool = 0
    database_url: AnyUrl = None
```
Pydantic automatically validates environment variables and provides type safety.

**Try It:**
```bash
# Start the server
docker compose up -d

# Test the endpoint
http GET http://localhost:8004/ping
```

---

#### Module 2: Docker Configuration
**Concepts Covered:**
- Dockerfile best practices
- Multi-container applications
- Volume mounting for development
- Environment variables

**Key Files:**
- `project/Dockerfile` - Development image
- `docker-compose.yml` - Service orchestration

**Code Explanation:**

```dockerfile
# Dockerfile - Layer optimization
ENV PYTHONDONTWRITEBYTECODE 1  # Prevents .pyc files
ENV PYTHONUNBUFFERED 1          # Ensures logs appear immediately
```

```yaml
# docker-compose.yml - Volume mounting
volumes:
  - ./project:/usr/src/app  # Live code reload
```
This allows changing code without rebuilding the image.

**Try It:**
```bash
# Rebuild after changes
docker compose up -d --build

# View logs
docker compose logs web
```

---

#### Module 3: PostgreSQL Setup
**Concepts Covered:**
- Database containerization
- ORM (Object-Relational Mapping) with Tortoise
- Database migrations with Aerich
- Async database operations

**Key Files:**
- `project/db/Dockerfile` - PostgreSQL image
- `project/app/models/tortoise.py` - Database models
- `project/app/db.py` - Database configuration

**Code Explanation:**

```python
# models/tortoise.py - ORM Model
class TextSummary(models.Model):
    url = fields.TextField()
    summary = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
```
Tortoise ORM maps Python classes to database tables.

```python
# db.py - Database registration
register_tortoise(
    app,
    db_url=os.environ.get("DATABASE_URL"),
    modules={"models": ["app.models.tortoise"]},
    generate_schemas=False,  # Use migrations instead
)
```

**Try It:**
```bash
# Access database
docker compose exec web-db psql -U postgres

# In psql:
\c web_dev
\dt
SELECT * FROM textsummary;
```

---

### **Phase 2: Testing (Modules 4-5)**

#### Module 4: Pytest Setup
**Concepts Covered:**
- Test fixtures and scopes
- Dependency overriding
- Given-When-Then pattern
- Test organization

**Key Files:**
- `project/tests/conftest.py` - Shared fixtures
- `project/tests/test_ping.py` - Example tests

**Code Explanation:**

```python
# conftest.py - Test fixture
@pytest.fixture(scope="module")
def test_app():
    # Setup: Override settings for testing
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    
    with TestClient(app) as test_client:
        yield test_client  # Test runs here
    
    # Teardown happens after yield
```

**Fixture Scopes:**
- `function` - Run before each test (default)
- `module` - Run once per test file
- `session` - Run once for entire test session

**Try It:**
```bash
# Run all tests
docker compose exec web python -m pytest

# Run with verbose output
docker compose exec web python -m pytest -v

# Run specific test
docker compose exec web python -m pytest tests/test_ping.py
```

---

#### Module 5: App Structure & Routing
**Concepts Covered:**
- API routing with APIRouter
- Request/response models
- Pydantic validation
- Code organization

**Key Files:**
- `project/app/api/summaries.py` - Route handlers
- `project/app/models/pydantic.py` - Schemas

**Code Explanation:**

```python
# api/summaries.py - Route handler
@router.post("/", response_model=SummaryResponseSchema, status_code=201)
async def create_summary(payload: SummaryPayloadSchema):
    # FastAPI automatically:
    # 1. Validates the request body against SummaryPayloadSchema
    # 2. Parses JSON to Python objects
    # 3. Returns errors if validation fails
    summary_id = await crud.post(payload)
    return {"id": summary_id, "url": payload.url}
```

```python
# models/pydantic.py - Schema validation
class SummaryPayloadSchema(BaseModel):
    url: AnyHttpUrl  # Validates URL format automatically
```

**Try It:**
```bash
# Test validation - this should fail
http --json POST http://localhost:8004/summaries/ url="not-a-valid-url"

# This should succeed
http --json POST http://localhost:8004/summaries/ url=https://testdriven.io
```

---

### **Phase 3: Full CRUD & TDD (Module 6)**

#### Module 6: RESTful Routes with TDD
**Concepts Covered:**
- RED-GREEN-REFACTOR cycle
- CRUD operations
- Path parameters and validation
- Error handling

**TDD Workflow:**

```
1. RED: Write a failing test
   └─> docker compose exec web python -m pytest
   
2. GREEN: Write minimal code to pass
   └─> Implement just enough functionality
   
3. REFACTOR: Improve code quality
   └─> Keep tests passing while improving
```

**Code Explanation:**

```python
# Path parameter validation
@router.get("/{id}/", response_model=SummarySchema)
async def read_summary(id: int = Path(..., gt=0)):
    # Path(..., gt=0) means:
    # - ... = required parameter
    # - gt=0 = must be greater than 0
    summary = await crud.get(id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary
```

**Try It - Follow TDD:**
```bash
# 1. Write test first (already in test_summaries.py)
# 2. Run test - it should FAIL
docker compose exec web python -m pytest tests/test_summaries.py::test_read_summary -v

# 3. Implement feature
# 4. Run test - it should PASS
docker compose exec web python -m pytest tests/test_summaries.py::test_read_summary -v
```

---

### **Phase 4: Deployment (Modules 7-10)**

#### Module 7: Production Deployment
**Concepts Covered:**
- Gunicorn + Uvicorn workers
- Production Dockerfile
- Environment-specific configuration
- Heroku deployment

**Code Explanation:**

```dockerfile
# Dockerfile.prod - Multi-stage build
FROM python:3.13.3-slim-bookworm as builder
# Build dependencies and wheels
# This stage is discarded after use

FROM python:3.13.3-slim-bookworm
# Final production image
# Only contains necessary runtime files
```

**Try It:**
```bash
# Build production image
docker build -f project/Dockerfile.prod -t summarizer:prod ./project

# Run locally
docker run -e PORT=8765 -e DATABASE_URL=sqlite://sqlite.db -p 5003:8765 summarizer:prod
```

---

#### Module 8: Code Quality Tools
**Concepts Covered:**
- Code coverage with Coverage.py
- Linting with Flake8
- Auto-formatting with Black
- Import sorting with isort

**Code Explanation:**

```python
# .coveragerc - Coverage configuration
[run]
omit = tests/*        # Don't measure test coverage
branch = True         # Measure branch coverage
```

**Quality Metrics:**
- **Coverage**: Measures which code is executed during tests
- **Flake8**: Checks PEP 8 style and common errors
- **Black**: Enforces consistent formatting
- **isort**: Organizes imports alphabetically

**Try It:**
```bash
# Check coverage
docker compose exec web python -m pytest --cov="." --cov-report html
open project/htmlcov/index.html

# Run quality checks
docker compose exec web flake8 .
docker compose exec web black . --check
docker compose exec web isort . --check-only

# Auto-fix formatting
docker compose exec web black .
docker compose exec web isort .
```

---

#### Module 9: Continuous Integration
**Concepts Covered:**
- GitHub Actions workflows
- Automated testing
- Container registry
- Workflow triggers

**Code Explanation:**

```yaml
# .github/workflows/main.yml
on: [push]  # Trigger on every push

jobs:
  build:
    # Build and push Docker images
  test:
    needs: build  # Run after build completes
    # Run tests in container
  deploy:
    needs: [build, test]  # Run after both complete
    # Deploy to Heroku
```

**Try It:**
```bash
# Commit and push to trigger CI
git add .
git commit -m "Test CI pipeline"
git push origin main

# View workflow on GitHub:
# https://github.com/YOUR_USERNAME/YOUR_REPO/actions
```

---

#### Module 10: Continuous Delivery
**Concepts Covered:**
- Automated deployments
- Heroku integration
- Environment secrets
- Release automation

**Code Explanation:**

```bash
# release.sh - Heroku deployment
IMAGE_ID=$(docker inspect ${HEROKU_REGISTRY_IMAGE} --format={{.Id}})
# Gets the Docker image ID

curl -X PATCH https://api.heroku.com/apps/$HEROKU_APP_NAME/formation \
  -H "Authorization: Bearer ${HEROKU_AUTH_TOKEN}"
# Triggers Heroku to deploy the new image
```

---

### **Phase 5: Advanced Features (Modules 11-13)**

#### Module 11: Complete CRUD Operations
**Concepts Covered:**
- UPDATE and DELETE operations
- Parametrized tests
- Advanced validation
- Error handling patterns

**Code Explanation:**

```python
# Parametrized test - test multiple scenarios
@pytest.mark.parametrize(
    "summary_id, payload, status_code, detail",
    [
        [999, {"url": "https://foo.bar", "summary": "updated!"}, 404, "Summary not found"],
        [0, {"url": "https://foo.bar", "summary": "updated!"}, 422, [...]],
    ],
)
def test_update_summary_invalid(test_app_with_db, summary_id, payload, status_code, detail):
    # This test runs twice with different inputs
    response = test_app_with_db.put(f"/summaries/{summary_id}/", data=json.dumps(payload))
    assert response.status_code == status_code
```

**Try It:**
```bash
# Test all CRUD operations
http POST http://localhost:8004/summaries/ url=https://testdriven.io
http GET http://localhost:8004/summaries/1/
http PUT http://localhost:8004/summaries/1/ url=https://testdriven.io summary="Updated summary"
http DELETE http://localhost:8004/summaries/1/
```

---

#### Module 12: Monkeypatching & Unit Tests
**Concepts Covered:**
- Mocking external dependencies
- Unit vs Integration tests
- Test isolation
- Parallel test execution

**Code Explanation:**

```python
# Monkeypatching example
def test_create_summary(test_app, monkeypatch):
    # Mock the database call
    async def mock_post(payload):
        return 1  # Return fake ID
    
    monkeypatch.setattr(crud, "post", mock_post)
    
    # Now the test doesn't hit the database
    response = test_app.post("/summaries/", ...)
```

**Why Monkeypatch?**
- **Speed**: Tests run faster without database
- **Isolation**: Tests don't affect each other
- **Predictability**: No external dependencies

**Try It:**
```bash
# Run unit tests only
docker compose exec web python -m pytest -k "unit" -v

# Run in parallel
docker compose exec web python -m pytest -k "unit" -n auto
```

---

#### Module 13: Text Summarization Feature
**Concepts Covered:**
- Background tasks in FastAPI
- Web scraping with Newspaper3k
- NLP basics
- Async operations

**Code Explanation:**

```python
# Background task execution
@router.post("/", response_model=SummaryResponseSchema, status_code=201)
async def create_summary(payload: SummaryPayloadSchema, background_tasks: BackgroundTasks):
    summary_id = await crud.post(payload)
    
    # This runs AFTER the response is sent
    background_tasks.add_task(generate_summary, summary_id, str(payload.url))
    
    return {"id": summary_id, "url": payload.url}
```

**Background Task Flow:**
```
Client Request → Create DB Entry → Return Response → Generate Summary → Update DB
     ↓               ↓                  ↓                  ↓              ↓
   Fast          Immediate          Immediate          Slow          Complete
```

**Try It:**
```bash
# Create summary
http POST http://localhost:8004/summaries/ url=https://testdriven.io

# Check immediately (summary will be empty)
http GET http://localhost:8004/summaries/1/

# Wait 5 seconds, check again (summary will be populated)
sleep 5
http GET http://localhost:8004/summaries/1/
```

---

### **Phase 6: Optimization (Modules 14-16)**

#### Module 14: Advanced CI/CD
**Concepts Covered:**
- Multi-stage Docker builds
- Docker layer caching
- Build optimization
- Dependency management

**Code Explanation:**

```dockerfile
# Multi-stage build
FROM python:3.13.3-slim-bookworm as builder
# Install and build dependencies
RUN pip wheel --no-deps --wheel-dir /wheels -r requirements.txt

FROM python:3.13.3-slim-bookworm
# Copy only the wheels, not the build tools
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*
```

**Benefits:**
- Smaller final image (builder stage discarded)
- Faster builds (cached layers)
- Linting in build process (fails early)

---

#### Module 15: Development Workflow
**Concepts Covered:**
- Command aliases
- Common operations
- Database management
- Debugging techniques

**Try It:**
```bash
# Create alias (add to ~/.bashrc)
alias dc='docker compose'

# Quick workflow
dc build
dc up -d
dc exec web aerich upgrade
dc exec web python -m pytest
dc logs -f web
```

---

## 🎓 Core Concepts Explained

### 1. Test-Driven Development (TDD)

**The TDD Cycle:**
```
┌─────────────┐
│  Write Test │ (RED - Test fails)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Write Code  │ (GREEN - Test passes)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Refactor   │ (Clean code while keeping tests green)
└──────┬──────┘
       │
       └────────────┐
                    │
       ┌────────────┘
       │
```

**Benefits:**
- Catches bugs early
- Provides documentation
- Encourages better design
- Enables confident refactoring

---

### 2. FastAPI Architecture

**Request Flow:**
```
HTTP Request
    │
    ▼
Routing (@router.get/post/put/delete)
    │
    ▼
Validation (Pydantic models)
    │
    ▼
Dependency Injection (get_settings, database)
    │
    ▼
Handler Function (async def)
    │
    ▼
CRUD Operations (database queries)
    │
    ▼
Response Model (Pydantic serialization)
    │
    ▼
HTTP Response
```

---

### 3. Async/Await

**Why Async?**
```python
# Synchronous - blocks while waiting
def get_data():
    result = slow_operation()  # Everything waits
    return result

# Asynchronous - other tasks can run
async def get_data():
    result = await slow_operation()  # Other tasks run during wait
    return result
```

**When to Use:**
- I/O operations (database, network)
- Multiple concurrent requests
- Background tasks

---

### 4. Docker Concepts

**Dockerfile Layers:**
```dockerfile
FROM python:3.13.3-slim-bookworm  # Layer 1 (cached)
WORKDIR /usr/src/app              # Layer 2 (cached)
COPY requirements.txt .            # Layer 3 (cached if unchanged)
RUN pip install -r requirements.txt # Layer 4 (cached if Layer 3 unchanged)
COPY . .                          # Layer 5 (changes most often)
```

**Layer Caching:**
- Each instruction creates a layer
- Layers are cached
- Change invalidates that layer + all after
- Order instructions from least to most frequently changed

---

## 🧪 Testing Strategy

### Test Types

**1. Unit Tests** (`test_summaries_unit.py`)
- Test individual functions
- Mock external dependencies
- Fast and isolated

**2. Integration Tests** (`test_summaries.py`)
- Test complete workflows
- Use real database (test DB)
- Slower but more realistic

**3. E2E Tests** (Manual testing)
- Test entire system
- Include external services
- Production-like environment

---

## 🐛 Common Issues & Solutions

### Issue 1: Port Already in Use
```bash
# Error: port 8004 is already allocated
# Solution: Change port in docker-compose.yml or stop conflicting service
docker compose down
lsof -i :8004  # Find process using port
```

### Issue 2: Database Connection Failed
```bash
# Error: connection to server failed
# Solution: Ensure database is ready
docker compose exec web nc -z web-db 5432  # Test connection
docker compose logs web-db  # Check database logs
```

### Issue 3: Tests Failing Randomly
```bash
# Possible causes:
# - Database state from previous tests
# - Async race conditions
# Solutions:
docker compose down -v  # Remove volumes
docker compose up -d --build
docker compose exec web aerich upgrade
```

### Issue 4: Import Errors
```bash
# Error: ModuleNotFoundError
# Solution: Rebuild container
docker compose build --no-cache
docker compose up -d
```

---

## 📊 Success Metrics

After completing this lab, you should be able to:

- [ ] Write tests before implementing features
- [ ] Build RESTful APIs with FastAPI
- [ ] Containerize applications with Docker
- [ ] Set up CI/CD pipelines
- [ ] Implement code quality tools
- [ ] Handle async operations
- [ ] Deploy to production
- [ ] Debug containerized applications

---

## 🎯 Practice Exercises

### Exercise 1: Add a New Endpoint
**Task:** Create a GET endpoint `/summaries/count` that returns the total number of summaries

**Steps:**
1. Write the test first
2. Run test (should fail)
3. Implement the feature
4. Run test (should pass)

### Exercise 2: Add Validation
**Task:** Ensure summary text is between 10 and 1000 characters

**Steps:**
1. Add validation to Pydantic model
2. Write tests for edge cases
3. Update PUT endpoint

### Exercise 3: Add Filtering
**Task:** Add query parameter to filter summaries by date

**Steps:**
1. Modify the GET all endpoint
2. Add tests
3. Implement filtering logic

---

## 📚 Additional Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Tortoise ORM Docs](https://tortoise.github.io/)
- [Pytest Docs](https://docs.pytest.org/)
- [Docker Docs](https://docs.docker.com/)

### Related Concepts
- REST API design principles
- Database normalization
- HTTP status codes
- OAuth authentication
- Rate limiting
- Caching strategies

---

## 🤝 Contributing

This is a learning lab. Feel free to:
- Add more test cases
- Improve documentation
- Fix bugs
- Add new features

---

## 📝 Notes

- Database is reset when you run `docker compose down -v`
- Use `docker compose logs -f web` to see live logs
- Tests run in isolation with a separate test database
- Production deployment uses Gunicorn with Uvicorn workers

---

## 🎊 Congratulations!

You've completed a comprehensive hands-on lab covering:
- Modern Python API development
- Test-driven development practices
- Container orchestration
- CI/CD automation
- Production deployment

Keep practicing and building! 🚀
