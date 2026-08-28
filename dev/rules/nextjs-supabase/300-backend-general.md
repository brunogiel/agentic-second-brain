---
description: Backend architecture and critical rules (layering, logger, validation)
globs:
  - "pages/api/**/*"
  - "app/api/**/*"
  - "services/**/*"
  - "actions/**/*"
alwaysApply: true
---

# Backend Architecture & Critical Rules

Layered architecture:

```
Handler → Validation → Service → DB/External
```

## Handlers (API routes or Route Handlers)

- Authenticate user
- Validate input with Zod
- Call service methods
- Log with Pino
- Return HTTP responses
- NO business logic, NO direct DB queries

## Services (`src/services/`)

- All business logic
- Data transformations
- Database operations
- External API calls
- Return typed data

## Critical rules

- **NO `console.log/warn/error`** → Use Pino logger only (`createApiLogger` or `createServiceLogger`)
- All inputs (body/query) validated with Zod schemas (`src/lib/validation/schemas.ts`)
- Use `validateRequest` helper in handlers
- Separate function per HTTP method in handlers
- Consistent responses: `{ ok: true, data }` or `{ error: string }`
- Proper HTTP status codes

## Data-layer performance

- **Heavy aggregation belongs in the database, not the service.** Counting, deduping, or grouping many rows? Do it in Postgres (`COUNT(DISTINCT)` / `GROUP BY`, a view, or an RPC) and return the small result set. Pulling thousands of rows into Node to compute in JS is the slow path: the bottleneck is the network round-trip plus the JS loop, not Postgres. Tens of thousands of rows aggregate in ~hundreds of ms natively vs seconds in the app.
- **If a read is slow, make the computation cheap before reaching for a cache.** A time-based cache that depends on an external warmer (a cron pinging an endpoint) is fragile: the warmer fails silently, the entry gets evicted, and you pay the cold path anyway. Push the work to the DB so cold loads are already fast and no warming is needed.
