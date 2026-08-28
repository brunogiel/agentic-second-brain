---
description: Vercel-inspired performance optimizations (re-renders, lazy init, loops)
alwaysApply: false
---

# Performance Optimizations (Vercel-Inspired)

Integrate these with existing component/hook rules to align with Vercel React best practices. Focus on reducing re-renders, lazy initialization, and efficient data processing.

## Re-Render Optimization

- Use `React.memo` for pure components that receive stable props.
- Memoize expensive computations with `useMemo` to prevent recalculation on every render.
- Avoid unnecessary state updates; check if new value differs before setting state.

```ts
// ✅ Optimized
const expensiveValue = useMemo(() => computeExpensive(data), [data]);

// ❌ Unoptimized (recomputes on every render)
const expensiveValue = computeExpensive(data);
```

## Lazy State Initialization

- For initial state requiring computation (e.g., parsing data), use callback form: `useState(() => initialValue)`.
- This ensures setup runs only once, not on re-renders.

```ts
// ✅ Lazy init
const [parsedData, setParsedData] = useState(() => JSON.parse(rawData));

// ❌ Runs on every render
const [parsedData, setParsedData] = useState(JSON.parse(rawData));
```

## Combine Loop Iterations

- When processing arrays (e.g., filtering + mapping in lists), merge into a single loop to avoid multiple passes.
- Prefer `reduce` or single `map` with logic inside for large datasets.

```ts
// ❌ Multiple passes
const filtered = items.filter(isActive);
const transformed = filtered.map(addStatus);

// ✅ Single pass
const result = items.reduce((acc, item) => {
  if (isActive(item)) acc.push(addStatus(item));
  return acc;
}, []);
```

## Code Review Checklist

- [ ] Expensive init uses lazy `useState`.
- [ ] Computations are memoized with `useMemo`.
- [ ] Array processing uses single loops.
- [ ] Components avoid unnecessary re-renders.
