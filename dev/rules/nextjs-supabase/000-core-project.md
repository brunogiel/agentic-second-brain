---
description: Core project best practices, data fetching, folder structure
alwaysApply: true
---

**General best practices:**
- Files ≤ 300 lines (split if >200).
- Dumb components: minimal logic.
- TypeScript strict types always.
- Tailwind CSS only.
- UI: ShadCN exclusively.
- Libraries: TanStack Query, server-only, Axios (central), zod, react-hook-form.

**Data Fetching & State Management:**
- **TanStack Query exclusively**: Use `@tanstack/react-query` for all client-side data fetching
- **NEVER use old `react-query`**: Always use `@tanstack/react-query` (the current package)
- **Authenticated API calls**: Use `authenticatedFetch` from `@/lib/authenticatedFetch` for all API calls needing auth
- Server state: Prefer Server Components with fetch, use TanStack Query for client needs
- Cache invalidation: Use TanStack Query's invalidation patterns, not manual cache management

**Preferred folder structure (use /src if possible):**
```
src/
├── app/                  # Routes & API (App Router priority)
│   └── api/              # Route Handlers
├── components/
│   └── ui/               # ShadCN components
├── actions/              # Server Actions ('use server')
├── services/             # Business logic & data access
├── hooks/                # Custom hooks
├── lib/                  # Utils, logger, validation, supabase clients
├── providers/            # TanStack Query, etc.
├── types/                # Shared types
└── utils/ or helpers/    # Pure functions
```

## Import Paths

- **Always use `@/` alias** for all imports from `src/` directory
- **Never use relative paths** like `../../` or `../` when importing from `src/`
- The `@` alias points to the `src/` directory root

**Examples:**

```ts
// ✅ Correct
import { Button } from '@/components/ui/button';
import type { ProjectCard } from '@/types/project';
import { useProjectsAppRouter } from '@/hooks/useProjectsAppRouter';
import { createServerClient } from '@/lib/supabase/server';

// ❌ Incorrect
import { Button } from '../../../components/ui/button';
import type { ProjectCard } from '../../types/project';
import { useProjectsAppRouter } from '../hooks/useProjectsAppRouter';
```
