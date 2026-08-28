---
description: Vercel-inspired data fetching optimizations (parallel fetches, bundle size)
alwaysApply: false
---

# Frontend Data Fetching Optimizations (Vercel-Inspired)

Enhance App Router and TanStack Query rules with Vercel best practices for async efficiency and bundle size.

## Eliminate Async Waterfalls

- In Server Components, fetch data in parallel (e.g., via `Promise.all` for independent requests).
- In client-side (TanStack Query), use parallel queries instead of sequential awaits.
- Only `await` when data is interdependent; skip unnecessary fetches based on conditions.

```ts
// ✅ Parallel fetches (Server Component)
const [dataA, dataB] = await Promise.all([fetchA(), fetchB()]);

// ❌ Waterfall
const dataA = await fetchA();
const dataB = await fetchB(dataA); // Only if truly dependent
```

## Reduce Bundle Size in Client Components

- Minimize client-side JS: Use `'use client'` sparingly; prefer Server Components.
- Avoid shipping unused code (e.g., no conditional branches that both include heavy logic).
- Direct imports (already required) help; additionally, tree-shake by avoiding dynamic imports for small modules.

## Client-Side vs. Server-Side Fetching

- Default to Server Components for initial data.
- Use TanStack Query for client interactivity; parallelize with `useQueries`.
- Hydrate only necessary data to reduce client load.

```ts
// ✅ Parallel client queries
const { data: [queryA, queryB] } = useQueries({
  queries: [{ queryKey: ['a'], queryFn: fetchA }, { queryKey: ['b'], queryFn: fetchB }],
});
```

## Code Review Checklist

- Fetches are parallelized where possible.
- No unnecessary async waterfalls.
- Client bundle minimized via Server Components.
- TanStack Query uses efficient patterns.
