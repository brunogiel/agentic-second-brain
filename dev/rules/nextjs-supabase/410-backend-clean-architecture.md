---
description: Clean Architecture for API endpoints (Controller / Service / Repository)
globs:
  - "app/api/**/*"
  - "pages/api/**/*"
alwaysApply: true
---

# Clean Architecture for API Endpoints

## Layered Architecture Pattern

All API endpoints **MUST** follow clean architecture principles with strict separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│   CONTROLLER LAYER (Route Handler)                          │
│   - Authenticate user                                        │
│   - Validate input (Zod)                                     │
│   - Map input to internal objects                            │
│   - Call service (ONE method call)                           │
│   - Map service response to HTTP response                    │
├─────────────────────────────────────────────────────────────┤
│   SERVICE LAYER (Business Logic)                             │
│   - Validate business rules                                  │
│   - Orchestrate operations                                   │
│   - Call repositories                                        │
│   - Transform data                                           │
│   - Log business events                                      │
├─────────────────────────────────────────────────────────────┤
│   REPOSITORY LAYER (Data Access)                             │
│   - Database queries                                         │
│   - Map snake_case ↔ camelCase                               │
│   - Handle DB errors                                         │
└─────────────────────────────────────────────────────────────┘
```

**Golden Rule: Controllers → Services → Repositories (NEVER skip layers)**

---

## Controller Layer (Route Handlers)

### The Five Commandments of Controllers

Controllers **MUST** do exactly these 5 things, in this order:

1. **Check authentication** (`verifyAuthApp`)
2. **Validate input** (Zod schemas)
3. **Map input to internal objects** (extract validated data)
4. **Call service** (ONE service method with all business logic)
5. **Map service response to HTTP response** (return `NextResponse`)

### STRICTLY FORBIDDEN

- ❌ **NO business logic** - delegate to services
- ❌ **NO direct repository calls** - ONLY call services
- ❌ **NO helper functions with business logic** - move to service
- ❌ **NO permission checks** - move to service
- ❌ **NO entity validation** - move to service
- ❌ **NO data transformation** - keep in service/repository layers
- ❌ **NO external API calls** - use services
- ❌ **NO multiple service calls for one operation** - create a service orchestration method

---

## Service Layer (Business Logic)

### Core Responsibilities

Services contain **ALL business logic** and orchestrate operations:

- ✅ **Validate business rules** (permissions, entity relationships, invariants)
- ✅ **Orchestrate multiple repository calls**
- ✅ **Transform data** between layers
- ✅ **Log business events** (using Pino)
- ✅ **Handle errors** with proper context
- ✅ **Coordinate transactions** (when supported)
- ✅ **Call external APIs** if needed

### STRICTLY FORBIDDEN

- ❌ **NO HTTP concerns** (status codes, headers, `NextResponse`)
- ❌ **NO Zod validation** (input validation is controller's job)
- ❌ **NO direct database queries** (use repositories)

### Service Method Checklist

When creating a service method, ensure it:

- [ ] Has a clear, descriptive name ending in `WithAuth` if it requires authorization
- [ ] Accepts primitive types or simple DTOs (not HTTP request objects)
- [ ] Returns a structured result object (not HTTP responses)
- [ ] Contains ALL business logic (no logic in controller)
- [ ] Validates all business rules
- [ ] Checks permissions if needed
- [ ] Calls repositories for data access
- [ ] Logs important business events
- [ ] Handles errors appropriately
- [ ] Returns meaningful error messages with status codes

---

## Repository Layer (Data Access)

### Core Responsibilities

Repositories handle **ONLY data access** and mapping:

- ✅ **Database query abstraction** (Supabase client)
- ✅ **Data mapping** (snake_case ↔ camelCase)
- ✅ **Connection management** (Supabase client)
- ✅ **Query optimization**
- ✅ **Handle database errors** with descriptive messages

### STRICTLY FORBIDDEN

- ❌ **NO business logic** (move to service)
- ❌ **NO permission checks** (move to service)
- ❌ **NO business validation** (move to service)
- ❌ **NO HTTP concerns** (status codes, responses)

### Repository Method Naming Convention

**CRUD operations:**

- `get{Entity}ById(id: string): Promise<Entity | null>`
- `get{Entity}By{Criteria}(criteria: string): Promise<Entity[]>`
- `create{Entity}(data: CreateEntityDTO): Promise<Entity>`
- `update{Entity}(id: string, data: UpdateEntityDTO): Promise<Entity>`
- `delete{Entity}(id: string): Promise<void>`

**Business-specific queries:**

- `getMemberById(memberId: string): Promise<ProjectMemberBasic | null>`
- `getProjectBasicDetails(projectId: string): Promise<ProjectBasicDetails | null>`
- `logRoleChange(params: RoleChangeLog): Promise<void>`

### Repository Method Checklist

When creating a repository method, ensure it:

- [ ] Has a clear, descriptive name following CRUD conventions
- [ ] Returns domain models (not raw database rows)
- [ ] Handles "not found" gracefully (return `null`, not throwing)
- [ ] Throws descriptive errors for database failures
- [ ] Maps snake_case to camelCase (and vice versa)
- [ ] Has NO business logic
- [ ] Has NO permission checks
- [ ] Has NO HTTP concerns
- [ ] Is ONLY called by services (never by controllers)

---

## Critical Rules

### Dependency Direction

- Controllers → Services → Repositories
- **NEVER** skip layers (Controller → Repository)

### Export Cleanliness

- **Repositories** MUST only export methods called by services
- **Services** MUST only export methods called by controllers/route handlers
- **Private/internal methods** should remain unexported
- **Legacy services** (`src/services/` non-v2) may maintain existing exports during migration
- **New v2 services** must follow export rules strictly

### Error Handling

- **Controllers**: HTTP status codes + consistent error format
- **Services**: Business logic errors + Pino logging
- **Repositories**: Database errors + descriptive messages

### Data Flow

- **Input validation** happens in controllers
- **Business validation** happens in services
- **Data transformation** happens in repositories/services

### Testing

- **Controllers**: HTTP behavior testing
- **Services**: Business logic unit tests
- **Repositories**: Data access integration tests

## Export Cleanliness Rules

### Repository Exports

Repositories **MUST** only export methods that are actually used by their immediate upper layer (services).

### Service Exports

Services **MUST** only export methods that are actually used by their immediate upper layer (controllers/route handlers).

### Validation Process

When adding new methods to repositories or services:

1. **Identify the caller**: Determine which upper layer will use the method
2. **Verify necessity**: Ensure the method is actually needed by that layer
3. **Export only if used**: Only export if the method will be imported and called by the upper layer
4. **Regular cleanup**: Periodically audit and remove unused exports

### Benefits

- **Clean interfaces**: Clear contracts between layers
- **Reduced coupling**: Upper layers only depend on what they actually use
- **Better maintainability**: Unused code is immediately visible and removable
- **Architecture compliance**: Enforces proper layered architecture boundaries

## Common Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Fat Controllers (Controller with Business Logic)

**Problem:** Controller contains business logic that should be in service.

### ❌ Anti-Pattern 2: Controller Calling Repositories Directly

**Problem:** Controller skips service layer and calls repository directly.

### ❌ Anti-Pattern 3: Anemic Services (Service with No Business Logic)

**Problem:** Service just passes data through to repository without adding value.

### ❌ Anti-Pattern 4: Repository with Business Logic

**Problem:** Repository contains business rules that should be in service.

### ❌ Anti-Pattern 5: Multiple Service Calls in Controller

**Problem:** Controller orchestrates multiple service calls (orchestration is service's job).

### ❌ Anti-Pattern 6: Service Returning HTTP Status Codes

**Problem:** Service is HTTP-aware (should be framework-agnostic).

### ❌ Anti-Pattern 7: Helper Functions with Business Logic in Controller

**Problem:** Controller has helper functions containing business logic.
