# FastAPI TDD Docker Lab - Complete Learning Path

## 📖 How to Use This Lab

This hands-on lab is designed for **learning by doing**. Follow the modules in order, as each builds upon the previous one. The lab includes:

- ✅ Complete working code
- 📝 Detailed explanations of core concepts
- 🧪 Test-driven development examples
- 🔍 Real-world best practices
- 💡 Interactive exercises

---

## 🗺️ Learning Journey Overview

```
Phase 1: Foundation → Phase 2: Testing → Phase 3: Full CRUD
     ↓                     ↓                    ↓
Phase 4: Deployment → Phase 5: Advanced → Phase 6: Optimization
```

**Total Time**: ~8-12 hours
**Difficulty**: Intermediate
**Prerequisites**: Basic Python, understanding of APIs

---

## 📚 Detailed Module Breakdown

### **PHASE 1: FOUNDATION**

#### **Module 1: Getting Started with FastAPI** (45 min)

**Learning Objectives:**
- Understand ASGI vs WSGI
- Master FastAPI basics
- Implement dependency injection
- Use Pydantic for configuration

**Files to Study:**
```
project/app/main.py          # Application setup
project/app/config.py        # Configuration management
project/app/api/ping.py      # Simple endpoint
```

**Key Concepts Explained:**

**1. Application Factory Pattern**
```python
# project/app/main.py
def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(ping.router)
    return application

app = create_application()
```

**Why use this pattern?**
- ✅ Creates fresh instances for testing
- ✅ Separates configuration from app creation
- ✅ Makes testing easier (no global state)
- ✅ Enables multiple app configurations

**2. Dependency Injection**
```python
# project/app/api/ping.py
@router.get("/ping")
async def pong(settings: Settings = Depends(get_settings)):
    return {
        "ping": "pong",
        "environment": settings.environment,
        "testing": settings.testing,
    }
```

**How it works:**
1. FastAPI sees `Depends(get_settings)`
2. Calls `get_settings()` function
3. Injects result into `settings` parameter
4. Available in handler without manual calls

**Benefits:**
- 🔄 Easy to override in tests
- 📦 Reusable across endpoints
- 🎯 Explicit dependencies
- 🧪 Testable in isolation

**3. Pydantic Settings**
```python
# project/app/config.py
class Settings(BaseSettings):
    environment: str = "dev"
    testing: bool = 0
    database_url: AnyUrl = None
```

**What happens:**
- Reads from environment variables automatically
- `environment` → reads `ENVIRONMENT` env var
- Validates types (AnyUrl ensures valid URL)
- Provides defaults if env var missing

**4. LRU Cache**
```python
@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()
```

**Why cache?**
- Settings are read once, not on every request
- Improves performance significantly
- Safe because settings don't change during runtime

**Hands-On Exercise:**
```bash
# 1. Start the service
docker compose up -d

# 2. Test the endpoint
http GET http://localhost:8004/ping

# 3. Try changing environment variables
docker compose down
# Edit docker-compose.yml: ENVIRONMENT=prod
docker compose up -d
http GET http://localhost:8004/ping

# Notice the "environment" field changed!
```

**Expected Output:**
```json
{
  "ping": "pong",
  "environment": "dev",
  "testing": false
}
```

---

#### **Module 2: Docker Configuration** (60 min)

**Learning Objectives:**
- Understand Docker layers and caching
- Configure multi-container apps
- Use volumes for development
- Master environment variables

**Files to Study:**
```
project/Dockerfile           # Development image
docker-compose.yml          # Service orchestration
project/.dockerignore       # Excluded files
```

**Key Concepts Explained:**

**1. Dockerfile Layer Caching**
```dockerfile
# Layer 1 - Rarely changes
FROM python:3.13.3-slim-bookworm

# Layer 2 - Rarely changes
WORKDIR /usr/src/app

# Layer 3 - Changes when requirements change
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Layer 4 - Changes frequently
COPY . .
```

**How caching works:**
```
First Build:
├── Layer 1: Pull base image (slow) ✓
├── Layer 2: Set workdir (fast) ✓
├── Layer 3: Install deps (slow) ✓
└── Layer 4: Copy code (fast) ✓

Second Build (code changed):
├── Layer 1: Use cache (instant) ⚡
├── Layer 2: Use cache (instant) ⚡
├── Layer 3: Use cache (instant) ⚡
└── Layer 4: Rebuild (fast) ✓
```

**2. Environment Variables**
```dockerfile
ENV PYTHONDONTWRITEBYTECODE 1  # Don't create .pyc files
ENV PYTHONUNBUFFERED 1          # Output immediately
```

**Why these matter:**
- `PYTHONDONTWRITEBYTECODE`: Prevents Python from writing bytecode files
  - Smaller image size
  - Faster container startup
  - Cleaner file system

- `PYTHONUNBUFFERED`: Forces stdout/stderr to be unbuffered
  - See logs in real-time
  - Better debugging
  - Logs appear immediately in Docker logs

**3. Volume Mounting**
```yaml
# docker-compose.yml
volumes:
  - ./project:/usr/src/app
```

**What this does:**
```
Host Machine           Container
─────────────────      ─────────────
./project/     ←─────→ /usr/src/app
```

**Benefits:**
- Edit code on host → instantly reflected in container
- No rebuild needed for code changes
- Faster development cycle

**Without volumes:**
```
Edit code → Rebuild image → Restart container (slow!)
```

**With volumes:**
```
Edit code → Auto-reload (fast!)
```

**4. Service Dependencies**
```yaml
depends_on:
  - web-db
```

**What this means:**
- Docker starts `web-db` before `web`
- ⚠️ Doesn't wait for database to be ready!
- That's why we need entrypoint.sh

**Hands-On Exercise:**
```bash
# 1. Build images
docker compose build

# 2. Watch the layers being cached
docker compose build
# Notice: "CACHED" appears for most layers

# 3. Change code in project/app/api/ping.py
# Add a new field to the response

# 4. No rebuild needed! Auto-reload handles it
http GET http://localhost:8004/ping
```

---

#### **Module 3: PostgreSQL Setup** (90 min)

**Learning Objectives:**
- Set up PostgreSQL in Docker
- Use Tortoise ORM for async database operations
- Manage database migrations with Aerich
- Understand database initialization

**Files to Study:**
```
project/db/Dockerfile        # PostgreSQL image
project/db/create.sql        # DB initialization
project/app/db.py           # Database configuration
project/app/models/tortoise.py # ORM models
project/entrypoint.sh       # Startup script
```

**Key Concepts Explained:**

**1. Database Initialization**
```sql
-- project/db/create.sql
CREATE DATABASE web_dev;
CREATE DATABASE web_test;
```

**Why two databases?**
```
web_dev  → Development/Production data
web_test → Test data (isolated, can be destroyed)
```

**2. Entrypoint Script**
```bash
#!/bin/sh
echo "Waiting for postgres..."

while ! nc -z web-db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"
exec "$@"
```

**What this does:**
```
Step 1: Container starts
   ↓
Step 2: Check if postgres is ready
   ↓ (if not ready)
Step 3: Wait 0.1 seconds
   ↓ (loop back to step 2)
Step 4: Postgres is ready!
   ↓
Step 5: Execute the main command
```

**Why it's needed:**
- `depends_on` starts the container
- But database inside needs time to initialize
- This script waits for actual readiness

**3. Tortoise ORM Model**
```python
# project/app/models/tortoise.py
class TextSummary(models.Model):
    url = fields.TextField()
    summary = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
```

**SQL equivalent:**
```sql
CREATE TABLE textsummary (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

**ORM Benefits:**
```
Without ORM:
"SELECT * FROM textsummary WHERE id = 1"

With ORM:
await TextSummary.filter(id=1).first()

✅ Type-safe
✅ Python objects, not raw SQL
✅ Database-agnostic
✅ Prevents SQL injection
```

**4. Database Migrations**
```python
# Create migration
$ docker compose exec web aerich init-db

# Apply migrations
$ docker compose exec web aerich upgrade

# Check history
$ docker compose exec web aerich history
```

**Migration workflow:**
```
1. Define model
     ↓
2. Create migration (aerich init-db)
     ↓
3. Migration file generated
     ↓
4. Apply to database (aerich upgrade)
     ↓
5. Database schema updated
```

**5. Async Database Operations**
```python
# Synchronous (blocks)
summary = TextSummary.filter(id=1).first()  # Everything waits

# Asynchronous (non-blocking)
summary = await TextSummary.filter(id=1).first()  # Other tasks run
```

**Performance comparison:**
```
Synchronous (3 queries):
Query 1 ──────> (200ms)
              Query 2 ──────> (200ms)
                            Query 3 ──────> (200ms)
Total: 600ms

Asynchronous (3 queries):
Query 1 ──────> (200ms)
Query 2 ──────> (200ms)
Query 3 ──────> (200ms)
Total: 200ms (parallel execution)
```

**Hands-On Exercise:**
```bash
# 1. Start services
docker compose up -d --build

# 2. Apply migrations
docker compose exec web aerich upgrade

# 3. Connect to database
docker compose exec web-db psql -U postgres

# 4. In psql, explore the database
\c web_dev                    # Connect to database
\dt                           # List tables
\d textsummary                # Describe table
SELECT * FROM textsummary;    # Query data

# 5. Try direct database operations
docker compose exec web python

# In Python shell:
>>> from app.models.tortoise import TextSummary
>>> import asyncio
>>> async def test():
...     await Tortoise.init(
...         db_url="postgres://postgres:postgres@web-db:5432/web_dev",
...         modules={"models": ["app.models.tortoise"]}
...     )
...     summaries = await TextSummary.all()
...     print(summaries)
>>> asyncio.run(test())
```

---

### **PHASE 2: TESTING**

#### **Module 4: Pytest Setup** (60 min)

**Learning Objectives:**
- Write effective pytest fixtures
- Override dependencies in tests
- Follow Given-When-Then pattern
- Understand test scopes

**Files to Study:**
```
project/tests/conftest.py    # Test fixtures
project/tests/test_ping.py   # Example tests
```

**Key Concepts Explained:**

**1. Test Fixtures**
```python
@pytest.fixture(scope="module")
def test_app():
    # Setup
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    
    with TestClient(app) as test_client:
        yield test_client  # ← Test runs here
    
    # Teardown
```

**Fixture lifecycle:**
```
Before test:
  ├── Create app
  ├── Override dependencies
  └── Create test client

During test:
  └── yield test_client (available as parameter)

After test:
  └── Cleanup (automatic with context manager)
```

**2. Fixture Scopes**
```python
scope="function"  # Default: Run before each test
scope="module"    # Run once per test file
scope="session"   # Run once for all tests
```

**Example:**
```
File: test_summaries.py (5 tests)

scope="function":
Setup → Test 1 → Teardown
Setup → Test 2 → Teardown
Setup → Test 3 → Teardown
Setup → Test 4 → Teardown
Setup → Test 5 → Teardown

scope="module":
Setup → Test 1 → Test 2 → Test 3 → Test 4 → Test 5 → Teardown
```

**3. Dependency Override**
```python
# Production
app.dependency_overrides[get_settings] = get_settings_override
```

**What this does:**
```
Normal request:
  get_settings() → returns Settings(testing=0, database_url=prod_db)

Test request:
  get_settings() → replaced by get_settings_override()
                → returns Settings(testing=1, database_url=test_db)
```

**4. Given-When-Then Pattern**
```python
def test_ping(test_app):
    # GIVEN: We have a test app (from fixture)
    
    # WHEN: We make a GET request to /ping
    response = test_app.get("/ping")
    
    # THEN: We expect specific response
    assert response.status_code == 200
    assert response.json() == {
        "environment": "dev",
        "ping": "pong",
        "testing": True
    }
```

**Benefits of this pattern:**
- ✅ Clear test structure
- ✅ Easy to understand
- ✅ Self-documenting
- ✅ Consistent across team

**5. Test Database Isolation**
```python
@pytest.fixture(scope="module")
def test_app_with_db():
    app = create_application()
    register_tortoise(
        app,
        db_url=os.environ.get("DATABASE_TEST_URL"),  # Separate DB!
        generate_schemas=True,  # Create tables automatically
    )
```

**Why separate database:**
```
Production DB: Real data, must preserve
    ↓
Test DB: Temporary data, can be destroyed
    ↓
Each test run:
  1. Create tables
  2. Run tests
  3. Destroy everything
```

**Hands-On Exercise:**
```bash
# 1. Run all tests
docker compose exec web python -m pytest

# 2. Run with verbose output
docker compose exec web python -m pytest -v

# 3. Run specific test
docker compose exec web python -m pytest tests/test_ping.py::test_ping

# 4. See test coverage
docker compose exec web python -m pytest --cov="."

# 5. Stop after first failure (useful for debugging)
docker compose exec web python -m pytest -x

# 6. Show local variables on failure
docker compose exec web python -m pytest -l --tb=short
```

---

#### **Module 5: App Structure & Routing** (45 min)

**Learning Objectives:**
- Organize FastAPI applications with APIRouter
- Separate concerns (routes, models, business logic)
- Validate requests with Pydantic
- Handle responses properly

**Files to Study:**
```
project/app/api/summaries.py  # Route handlers
project/app/api/crud.py       # Database operations
project/app/models/pydantic.py # Request/response schemas
```

**Key Concepts Explained:**

**1. APIRouter**
```python
# project/app/api/ping.py
router = APIRouter()

@router.get("/ping")
async def pong():
    ...

# project/app/main.py
app.include_router(ping.router)
app.include_router(summaries.router, prefix="/summaries", tags=["summaries"])
```

**Benefits:**
```
Without APIRouter:
  All routes in main.py → Hard to maintain

With APIRouter:
  ping.py → /ping routes
  summaries.py → /summaries routes
  users.py → /users routes
  ✅ Organized by domain
  ✅ Easy to test in isolation
  ✅ Can be versioned (v1, v2)
```

**2. Pydantic Request Validation**
```python
# project/app/models/pydantic.py
class SummaryPayloadSchema(BaseModel):
    url: AnyHttpUrl  # Automatically validates URL format

# project/app/api/summaries.py
@router.post("/")
async def create_summary(payload: SummaryPayloadSchema):
    # If we get here, payload.url is a valid HTTP(S) URL!
```

**Validation flow:**
```
Client sends: {"url": "invalid-url"}
   ↓
FastAPI validates against SummaryPayloadSchema
   ↓
AnyHttpUrl validator checks format
   ↓
Invalid! Return 422 error with details
   ↓
Handler never executes


Client sends: {"url": "https://example.com"}
   ↓
FastAPI validates
   ↓
Valid! Parse into Python object
   ↓
Handler executes with validated payload
```

**3. Response Models**
```python
@router.post("/", response_model=SummaryResponseSchema, status_code=201)
async def create_summary(payload: SummaryPayloadSchema):
    summary_id = await crud.post(payload)
    return {"id": summary_id, "url": payload.url}
```

**What response_model does:**
```
Handler returns: {"id": 1, "url": "https://foo.bar/", "extra": "ignored"}
   ↓
FastAPI filters through SummaryResponseSchema
   ↓
Final response: {"id": 1, "url": "https://foo.bar/"}

✅ Ensures consistent responses
✅ Filters out sensitive data
✅ Auto-generates OpenAPI schema
```

**4. Separation of Concerns**
```
summaries.py (Routes)
    ├── Handle HTTP
    ├── Validate input
    ├── Call business logic
    └── Format response

crud.py (Data Access)
    ├── Database queries
    ├── Data transformation
    └── No HTTP knowledge

models/ (Data Models)
    ├── pydantic.py → API schemas
    └── tortoise.py → Database models
```

**Benefits:**
- ✅ Testable in isolation
- ✅ Reusable functions
- ✅ Clear responsibilities
- ✅ Easy to modify

**Hands-On Exercise:**
```bash
# 1. Test the API with different payloads

# Valid URL
http --json POST http://localhost:8004/summaries/ url=https://testdriven.io

# Invalid URL scheme
http --json POST http://localhost:8004/summaries/ url=ftp://testdriven.io
# Notice: 422 error with validation message

# Missing URL
http --json POST http://localhost:8004/summaries/
# Notice: 422 error saying "Field required"

# 2. Explore auto-generated docs
# Visit: http://localhost:8004/docs
# Try the "Try it out" feature

# 3. Check the OpenAPI schema
http GET http://localhost:8004/openapi.json
```

---

### **PHASE 3: FULL CRUD & TDD**

#### **Module 6: RESTful Routes with TDD** (90 min)

**Learning Objectives:**
- Practice RED-GREEN-REFACTOR cycle
- Implement complete CRUD operations
- Use path parameters and validation
- Handle errors properly

**Files to Study:**
```
project/tests/test_summaries.py  # Integration tests
project/app/api/summaries.py     # All CRUD endpoints
project/app/api/crud.py          # Database operations
```

**Key Concepts Explained:**

**1. RED-GREEN-REFACTOR Cycle**
```
🔴 RED: Write a failing test
   ↓
   def test_read_summary():
       response = test_app.get("/summaries/1/")
       assert response.status_code == 200
   
   $ pytest
   > 404 != 200  # FAIL!

🟢 GREEN: Write minimal code to pass
   ↓
   @router.get("/{id}/")
   async def read_summary(id: int):
       summary = await crud.get(id)
       return summary
   
   $ pytest
   > PASS!

♻️ REFACTOR: Improve code quality
   ↓
   @router.get("/{id}/", response_model=SummarySchema)
   async def read_summary(id: int = Path(..., gt=0)):
       summary = await crud.get(id)
       if not summary:
           raise HTTPException(status_code=404, detail="Summary not found")
       return summary
   
   $ pytest
   > PASS! (still works after refactoring)
```

**Why TDD works:**
- ✅ Tests catch regressions immediately
- ✅ Code is testable by design
- ✅ Clear requirements
- ✅ Confidence when refactoring

**2. Path Parameters**
```python
@router.get("/{id}/")
async def read_summary(id: int = Path(..., gt=0)):
    ...
```

**URL**: `GET /summaries/123/`
**Extracted**: `id = 123`

**Path() parameters:**
```python
Path(..., gt=0)
      │     │
      │     └── Validation: must be > 0
      └── Required (ellipsis means required)
```

**Examples:**
```
GET /summaries/1/   → id=1  ✅ Valid (1 > 0)
GET /summaries/0/   → id=0  ❌ Invalid (0 not > 0) → 422
GET /summaries/-1/  → id=-1 ❌ Invalid (-1 not > 0) → 422
GET /summaries/abc/ → ❌ Invalid (not an integer) → 422
```

**3. Error Handling Patterns**
```python
@router.get("/{id}/")
async def read_summary(id: int = Path(..., gt=0)):
    summary = await crud.get(id)
    
    # Explicit error handling
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    return summary
```

**HTTP Status Codes:**
```
200 OK           - Success
201 Created      - Resource created
404 Not Found    - Resource doesn't exist
422 Unprocessable Entity - Validation failed
500 Server Error - Something went wrong
```

**4. CRUD Operations**
```python
# CREATE
@router.post("/", status_code=201)
async def create_summary(payload: SummaryPayloadSchema):
    summary_id = await crud.post(payload)
    return {"id": summary_id, "url": payload.url}

# READ (single)
@router.get("/{id}/")
async def read_summary(id: int):
    return await crud.get(id)

# READ (all)
@router.get("/")
async def read_all_summaries():
    return await crud.get_all()

# UPDATE
@router.put("/{id}/")
async def update_summary(id: int, payload: SummaryUpdatePayloadSchema):
    return await crud.put(id, payload)

# DELETE
@router.delete("/{id}/")
async def delete_summary(id: int):
    await crud.delete(id)
    return {"message": "Deleted"}
```

**RESTful pattern:**
```
Resource: /summaries

POST   /summaries      → Create new
GET    /summaries      → Get all
GET    /summaries/1    → Get one
PUT    /summaries/1    → Update
DELETE /summaries/1    → Delete
```

**Hands-On Exercise - TDD Practice:**

```bash
# Exercise: Add a new endpoint GET /summaries/count
# Returns the total number of summaries

# Step 1: 🔴 Write the test FIRST
# Add to test_summaries.py:
def test_count_summaries(test_app_with_db):
    # Create some summaries first
    test_app_with_db.post("/summaries/", data=json.dumps({"url": "https://foo.bar"}))
    test_app_with_db.post("/summaries/", data=json.dumps({"url": "https://baz.qux"}))
    
    # Test the count endpoint
    response = test_app_with_db.get("/summaries/count")
    assert response.status_code == 200
    assert response.json()["count"] >= 2

# Step 2: Run test - it should FAIL
docker compose exec web python -m pytest tests/test_summaries.py::test_count_summaries
# Expected: 404 (route doesn't exist)

# Step 3: 🟢 Implement the feature
# Add to crud.py:
async def count() -> int:
    return await TextSummary.all().count()

# Add to summaries.py:
@router.get("/count")
async def count_summaries():
    total = await crud.count()
    return {"count": total}

# Step 4: Run test - it should PASS
docker compose exec web python -m pytest tests/test_summaries.py::test_count_summaries

# Step 5: ♻️ Refactor if needed
# Add response model, better naming, etc.
```

---

## 🎯 Continue Learning

The lab continues with more advanced topics:
- Module 7: Production deployment
- Module 8: Code quality tools
- Module 9-10: CI/CD pipelines
- Module 11: Complete CRUD
- Module 12: Unit testing
- Module 13: Background tasks
- Module 14: Build optimization

Each module builds on previous knowledge and introduces new concepts progressively.

---

## 💡 Key Takeaways

After completing the foundation modules, you should understand:

1. **FastAPI Fundamentals**
   - Application factory pattern
   - Dependency injection
   - Async/await usage
   - Pydantic validation

2. **Docker Skills**
   - Layer caching
   - Multi-container apps
   - Volume mounting
   - Environment configuration

3. **Database Management**
   - ORM usage (Tortoise)
   - Async database operations
   - Migration management
   - Database isolation in tests

4. **Testing Best Practices**
   - Test fixtures and scopes
   - Dependency overriding
   - Given-When-Then pattern
   - Integration vs unit tests

5. **TDD Methodology**
   - RED-GREEN-REFACTOR cycle
   - Test-first development
   - Refactoring with confidence

---

## 🔧 Troubleshooting Guide

### Common Issues:

**1. Port already in use**
```bash
Error: port 8004 is already allocated

Solution:
docker compose down
# Change port in docker-compose.yml
# Or kill process using the port:
lsof -i :8004
kill -9 <PID>
```

**2. Database connection failed**
```bash
Error: could not connect to server

Solution:
# Wait for PostgreSQL to be ready
docker compose logs web-db
# Ensure entrypoint.sh is executable
chmod +x project/entrypoint.sh
docker compose down
docker compose up -d --build
```

**3. Tests failing with database errors**
```bash
Error: relation "textsummary" does not exist

Solution:
# Make sure test database is set up
docker compose exec web-db psql -U postgres -c "CREATE DATABASE web_test;"
# Or use fresh database:
docker compose down -v
docker compose up -d --build
docker compose exec web aerich upgrade
```

---

## 📚 Additional Practice

**Mini Projects:**
1. Add user authentication
2. Implement rate limiting
3. Add caching layer
4. Create admin dashboard
5. Add email notifications

**Challenges:**
1. Write tests achieving 100% coverage
2. Optimize Docker build time
3. Add GraphQL endpoint
4. Implement WebSocket support
5. Add Prometheus metrics

---

## 🎓 Next Steps

After mastering this lab:

1. **Explore FastAPI Advanced Features**
   - OAuth2 authentication
   - WebSockets
   - GraphQL
   - Background workers (Celery)

2. **DevOps Skills**
   - Kubernetes deployment
   - Load balancing
   - Monitoring (Prometheus/Grafana)
   - Log aggregation (ELK stack)

3. **Architecture Patterns**
   - Microservices
   - Event-driven architecture
   - CQRS pattern
   - Domain-driven design

4. **Production Readiness**
   - Security hardening
   - Performance optimization
   - Disaster recovery
   - Scalability planning

---

Happy Learning! 🚀
