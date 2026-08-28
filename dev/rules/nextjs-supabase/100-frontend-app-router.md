---
description: Rules for new frontend code - App Router only
globs:
  - "app/**/*"
  - "src/app/**/*"
alwaysApply: true
---

# New Frontend Code - App Router Only

All new pages and features must use App Router.

- React Server Components by default (no 'use client' unless needed for hooks, events, or local state).
- Nested layouts, loading.tsx, error.tsx where useful.
- Route Groups (folder) for organization.
- Direct fetch in Server Components.
- Metadata: generateMetadata function.
- 'use client' only at file top when required.
- TanStack Query hydration: <HydrationBoundary>.
- New API endpoints: app/api/.../route.ts (Route Handlers).
- Prefer Server Actions for mutations over POST routes.
