---
description: CRITICAL - Supabase database calls ONLY on the server (never client-side)
globs:
  - "**/*.tsx"
  - "**/*.ts"
  - "**/*.jsx"
  - "**/*.js"
alwaysApply: true
---

# CRITICAL SECURITY RULE: Supabase Database Calls ONLY on the Server

Supabase client instances that perform database operations (queries, inserts, updates, deletes, RPCs) MUST NEVER be created or used in client-side code.

## Allowed (Server-side only)

- Server Components (default in App Router — no `'use client'`)
- Server Actions (`'use server'` directive)
- Route Handlers (`app/api/.../route.ts`)
- Pages API routes (`/pages/api` — legacy)
- Service files imported only from server contexts (`src/services/*`)
- Any file that imports `'server-only'`

## Strictly forbidden (Client-side)

- Any file with `'use client'` at the top
- Client Components
- Hooks (`src/hooks/*`)
- Browser-executed code
- Direct usage in `.tsx` files rendered on the client

## Implementation rules

### 1. Create Supabase clients centrally

- Server-side client: `src/lib/supabase/server.ts` (use with admin/service_role if needed, but carefully)
- Auth-aware server client: Use cookies/headers to get session
- NEVER create a client with `createClient()` using public anon key in client code for DB operations

### 2. Protect server-only Supabase code

Always import `'server-only'` at the top of any file that creates or uses a Supabase client for DB access:

```ts
import 'server-only';
import { createServerClient } from '@/lib/supabase/server';
```

### 3. Client-side Supabase usage (limited)

- Only allowed for auth (`signIn`, `signOut`, `getSession`) using `@supabase/auth-helpers-nextjs`
- Never perform `.from('table').select()/insert()/update()` etc. on client
- If data is needed on client → fetch via Server Action, Route Handler, or Server Component

## Examples

### ✅ Correct — Server Component / Server Action

```ts
import 'server-only';
import { createServerClient } from '@/lib/supabase/server';
const supabase = createServerClient();
const { data } = await supabase.from('boards').select('*');
```

### ✅ Correct — Service called from server context

```ts
// src/services/boardService.ts
import 'server-only';
// ...
await supabase.from('boards').insert(...);
```

### ❌ FORBIDDEN — Client Component

```tsx
'use client'; // This makes it client-side → NEVER do DB calls here
import { createClient } from '@supabase/supabase-js'; // DANGER
const supabase = createClient(...); // Even worse if using anon key
await supabase.from('boards').select('*'); // EXPOSES DATA / RLS BYPASS RISK
```
