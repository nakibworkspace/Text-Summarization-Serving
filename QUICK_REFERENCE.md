# Quick Reference Guide

## 📁 File-by-File Explanation

### **Root Level Files**

#### `README.md`
**Purpose**: Main documentation and quick start guide
**What it contains**:
- Project overview and learning objectives
- Architecture diagram
- Quick start instructions
- Complete learning path
- Troubleshooting guide

#### `docker-compose.yml`
**Purpose**: Orchestrates all Docker services
**What it defines**:
- `web` service: FastAPI application
- `web-db` service: PostgreSQL database
- Network configuration
- Volume mounts
- Environment variables

**Key concept**: This is your development environment in one file

#### `release.sh`
**Purpose**: Deploys to Heroku via API
**What it does**:
- Gets Docker image ID
- Calls Heroku API to release new version
- Automates deployment process

---

### **GitHub Actions**

#### `.github/workflows/main.yml`
**Purpose**: CI/CD pipeline configuration
**What it contains**:
- **build** job: Builds Docker images
- **test** job: Runs tests and linters
- **deploy** job: Deploys to Heroku

**Triggers**: Runs on every push to repository

**Key concept**: Automates testing and deployment

---

### **Project Directory**

#### `project/requirements.txt`
**Purpose**: Production dependencies
**What it lists**:
- FastAPI framework
- Uvicorn server
- Tortoise ORM
- Database drivers
- Text summarization libraries

#### `project/requirements-dev.txt`
**Purpose**: Development dependencies
**What it adds**:
- Pytest (testing)
- Black (formatting)
- Flake8 (linting)
- isort (import sorting)
- Coverage (code coverage)

**Key concept**: Separates prod and dev dependencies for smaller production images

#### `project/Dockerfile`
**Purpose**: Development Docker image
**What it does**:
- Starts from Python base image
- Installs system dependencies (PostgreSQL, netcat)
- Installs Python packages
- Sets up entrypoint script

**When used**: `docker compose up` uses this

#### `project/Dockerfile.prod`
**Purpose**: Production Docker image
**What it does**:
- **Stage 1 (builder)**: Builds wheels, runs linters
- **Stage 2 (final)**: Creates minimal production image
- Adds non-root user for security
- Runs Gunicorn with Uvicorn workers

**Key concept**: Multi-stage builds reduce image size

**When used**: GitHub Actions and Heroku deployment

#### `project/entrypoint.sh`
**Purpose**: Container startup script
**What it does**:
```bash
1. Wait for PostgreSQL to be ready
2. Execute the main command (uvicorn)
```

**Why needed**: Docker Compose `depends_on` doesn't wait for services to be ready

#### `project/.dockerignore`
**Purpose**: Excludes files from Docker images
**What it excludes**:
- Virtual environments
- Dockerfiles
- Local configurations

**Benefit**: Smaller, faster builds

#### `project/.coveragerc`
**Purpose**: Code coverage configuration
**What it sets**:
- Exclude tests from coverage
- Enable branch coverage

#### `project/setup.cfg`
**Purpose**: Flake8 configuration
**What it sets**:
- Maximum line length (119 characters)

---

### **Database Files**

#### `project/db/Dockerfile`
**Purpose**: PostgreSQL Docker image
**What it does**:
- Extends official PostgreSQL image
- Runs create.sql on initialization

#### `project/db/create.sql`
**Purpose**: Database initialization
**What it creates**:
- `web_dev` database (development/production)
- `web_test` database (testing)

---

### **Application Code**

#### `project/app/main.py`
**Purpose**: Application entry point
**What it does**:
```python
1. Creates FastAPI application
2. Registers routers
3. Initializes database
```

**Key functions**:
- `create_application()`: Factory pattern for creating app instances

#### `project/app/config.py`
**Purpose**: Configuration management
**What it does**:
```python
1. Defines Settings class with Pydantic
2. Reads from environment variables
3. Caches settings with lru_cache
```

**Key concept**: Type-safe configuration with automatic validation

#### `project/app/db.py`
**Purpose**: Database setup and utilities
**What it contains**:
- `TORTOISE_ORM`: Tortoise configuration dict
- `init_db()`: Registers Tortoise with FastAPI
- `generate_schema()`: Creates tables programmatically

**When used**: 
- `init_db()`: Called at startup
- `generate_schema()`: Run manually to skip migrations

#### `project/app/summarizer.py`
**Purpose**: Text summarization logic
**What it does**:
```python
1. Downloads article from URL
2. Parses content with Newspaper3k
3. Generates summary with NLP
4. Updates database
```

**Key concept**: Background task for long-running operations

---

### **API Layer**

#### `project/app/api/ping.py`
**Purpose**: Health check endpoint
**What it provides**:
- `GET /ping`: Returns environment info

**Use case**: Monitoring, testing setup

#### `project/app/api/crud.py`
**Purpose**: Database operations (Data Access Layer)
**What it contains**:
- `post()`: Create summary
- `get()`: Read single summary
- `get_all()`: Read all summaries
- `put()`: Update summary
- `delete()`: Delete summary

**Key concept**: Separates database logic from HTTP handlers

#### `project/app/api/summaries.py`
**Purpose**: Summary CRUD endpoints
**What it provides**:
- `POST /summaries`: Create summary
- `GET /summaries`: List all summaries
- `GET /summaries/{id}`: Get single summary
- `PUT /summaries/{id}`: Update summary
- `DELETE /summaries/{id}`: Delete summary

**Key concept**: RESTful API design

---

### **Models**

#### `project/app/models/pydantic.py`
**Purpose**: Request/response schemas
**What it defines**:
- `SummaryPayloadSchema`: Create summary request
- `SummaryResponseSchema`: Summary response
- `SummaryUpdatePayloadSchema`: Update summary request

**Key concept**: Data validation and serialization

**Example flow**:
```
Client JSON → Pydantic validates → Python object → Handler
Handler → Python object → Pydantic serializes → JSON response
```

#### `project/app/models/tortoise.py`
**Purpose**: Database models
**What it defines**:
- `TextSummary`: Database table model
- `SummarySchema`: Generated Pydantic model

**Key concept**: ORM maps Python classes to database tables

**Example**:
```python
# Python code
summary = TextSummary(url="https://example.com", summary="Text")
await summary.save()

# SQL executed
INSERT INTO textsummary (url, summary, created_at) 
VALUES ('https://example.com', 'Text', NOW())
```

---

### **Tests**

#### `project/tests/conftest.py`
**Purpose**: Shared test fixtures
**What it provides**:
- `test_app`: FastAPI test client without database
- `test_app_with_db`: Test client with test database
- `get_settings_override()`: Test configuration

**Key concept**: Fixtures reduce code duplication

#### `project/tests/test_ping.py`
**Purpose**: Health check tests
**What it tests**:
- Endpoint returns correct status code
- Response has expected structure
- Testing flag is set correctly

#### `project/tests/test_summaries.py`
**Purpose**: Integration tests
**What it tests**:
- Full CRUD operations with database
- Error handling
- Validation logic
- Background tasks (mocked)

**Key concept**: Tests complete workflows

#### `project/tests/test_summaries_unit.py`
**Purpose**: Unit tests
**What it tests**:
- Individual functions in isolation
- Uses monkeypatching to mock database
- Faster than integration tests

**Key concept**: Tests logic without external dependencies

---

### **Migrations**

#### `project/migrations/models/0_*.sql`
**Purpose**: Database migration
**What it contains**:
- `upgrade()`: SQL to create tables
- `downgrade()`: SQL to revert changes

**How to use**:
```bash
# Create migration
docker compose exec web aerich init-db

# Apply migration
docker compose exec web aerich upgrade

# Rollback
docker compose exec web aerich downgrade
```

---

## 🎯 Quick Command Reference

### Docker Commands

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# View logs
docker compose logs -f web

# Stop services
docker compose down

# Remove volumes (fresh start)
docker compose down -v

# Rebuild everything
docker compose up -d --build
```

### Database Commands

```bash
# Access PostgreSQL
docker compose exec web-db psql -U postgres

# Apply migrations
docker compose exec web aerich upgrade

# Create new migration
docker compose exec web aerich migrate

# Migration history
docker compose exec web aerich history
```

### Testing Commands

```bash
# Run all tests
docker compose exec web python -m pytest

# Run with coverage
docker compose exec web python -m pytest --cov="."

# Run specific test
docker compose exec web python -m pytest tests/test_ping.py

# Run in parallel
docker compose exec web python -m pytest -n auto
```

### Code Quality Commands

```bash
# Lint with Flake8
docker compose exec web flake8 .

# Format with Black
docker compose exec web black .

# Check formatting (don't modify)
docker compose exec web black . --check

# Sort imports
docker compose exec web isort .

# Check imports (don't modify)
docker compose exec web isort . --check-only
```

### API Testing Commands

```bash
# Health check
http GET http://localhost:8004/ping

# Create summary
http --json POST http://localhost:8004/summaries/ url=https://testdriven.io

# Get all summaries
http GET http://localhost:8004/summaries/

# Get specific summary
http GET http://localhost:8004/summaries/1/

# Update summary
http PUT http://localhost:8004/summaries/1/ url=https://testdriven.io summary="Updated"

# Delete summary
http DELETE http://localhost:8004/summaries/1/
```

---

## 🔍 What Each Service Does

### `web` Service (FastAPI App)
**Image**: Built from `project/Dockerfile`
**Port**: 8004 (host) → 8000 (container)
**What it runs**: `uvicorn app.main:app --reload`
**Purpose**: Serves API endpoints

### `web-db` Service (PostgreSQL)
**Image**: Built from `project/db/Dockerfile`
**Port**: 5432 (internal only)
**What it runs**: PostgreSQL server
**Purpose**: Stores summary data

---

## 📊 Data Flow

### Creating a Summary

```
1. Client Request
   POST /summaries/ {"url": "https://example.com"}
   ↓

2. FastAPI Route Handler
   @router.post("/")
   async def create_summary(payload: SummaryPayloadSchema)
   ↓

3. Pydantic Validation
   Validates URL format
   ↓

4. CRUD Layer
   await crud.post(payload)
   ↓

5. Tortoise ORM
   TextSummary(url=..., summary="")
   await summary.save()
   ↓

6. PostgreSQL
   INSERT INTO textsummary...
   ↓

7. Background Task
   background_tasks.add_task(generate_summary, ...)
   ↓

8. Response
   {"id": 1, "url": "https://example.com"}
   ↓

9. Background Processing
   - Download article
   - Parse content
   - Generate summary
   - Update database
```

---

## 🧪 Testing Strategy

### Test Pyramid

```
        /\
       /  \
      / UI \
     /------\
    /  API   \    ← test_summaries.py (Integration)
   /----------\
  /   Unit     \  ← test_summaries_unit.py
 /--------------\
```

### When to Use Each Type

**Unit Tests** (`test_summaries_unit.py`):
- ✅ Fast execution
- ✅ Test logic in isolation
- ✅ No database required
- Use for: Business logic, validators, transformers

**Integration Tests** (`test_summaries.py`):
- ✅ Test complete workflows
- ✅ Includes database
- ❌ Slower execution
- Use for: API endpoints, database operations

**E2E Tests** (Manual):
- ✅ Test entire system
- ✅ Includes external services
- ❌ Slowest, fragile
- Use for: Critical user flows

---

## 🚀 Deployment Flow

### Local → GitHub → Production

```
1. Local Development
   Write code → Run tests → Commit
   ↓

2. Push to GitHub
   git push origin main
   ↓

3. GitHub Actions Triggered
   ├── Build Docker image
   ├── Run tests
   ├── Run linters
   └── (if all pass)
   ↓

4. Deploy to Heroku
   ├── Push image to Heroku registry
   └── Release new version
   ↓

5. Production Live
   https://your-app.herokuapp.com
```

---

## 💡 Best Practices Demonstrated

1. **Test-Driven Development**
   - Write tests first
   - Implement features
   - Refactor with confidence

2. **Separation of Concerns**
   - Routes (API layer)
   - Business logic (CRUD)
   - Data models (ORM)

3. **Configuration Management**
   - Environment variables
   - Type-safe settings
   - Separate dev/prod configs

4. **Docker Best Practices**
   - Multi-stage builds
   - Layer caching
   - Non-root user
   - .dockerignore

5. **Code Quality**
   - Linting (Flake8)
   - Formatting (Black)
   - Import sorting (isort)
   - Type hints

6. **Database Management**
   - Migrations (Aerich)
   - Separate test database
   - Async operations

7. **API Design**
   - RESTful routes
   - Proper status codes
   - Request validation
   - Response models

---

This reference guide covers the structure and purpose of every file in the project! 🎯
