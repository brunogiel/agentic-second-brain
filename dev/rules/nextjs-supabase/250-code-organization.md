---
description: Code organization rules - constants, types, hooks, components, files
alwaysApply: true
---

# Code Organization Rules

## Constants

- **Never define constants inline** in components
- Move all constants to `src/constants/` directory
- Group related constants in domain-specific files (e.g., `roadmap.ts`, `features.ts`)
- Examples of what belongs in constants:
  - View options arrays
  - Status options arrays
  - Style configurations (colors, gradients, shadows)
  - Configuration objects (timeline ranges, pagination sizes)

```ts
// ❌ Incorrect - inline constants
const VIEW_OPTIONS = [
  { value: 'grid', labelKey: 'roadmap.viewToggle.grid' },
];
const STATUS_COLORS = { done: '#22c55e', pending: '#fbbf24' };

// ✅ Correct - import from constants
import { PROJECT_VIEW_OPTIONS, TIMELINE_BAR_STYLES } from '@/constants/roadmap';
```

## Types

- **Check existing types** before creating new ones
- Use `type` imports: `import type { MyType } from '@/types/...'`
- Prefer optional props (`?`) over union with null when both undefined and null are acceptable

### Where Types Belong

| Type | Location |
|------|----------|
| **Component props** | In the component file itself |
| **Domain/shared types** | `src/types/` directory |
| **Hook return types** | In the hook file itself |
| **API response types** | `src/types/` directory |

```ts
// ❌ Incorrect - component props in types file
// src/types/initiative.ts
export interface InitiativesSectionProps {
  projectId: string;
  initiatives: Initiative[];
}

// src/components/InitiativesSection.tsx
import type { InitiativesSectionProps } from '@/types/initiative';

// ✅ Correct - component props in component file
// src/components/InitiativesSection.tsx
interface InitiativesSectionProps {
  projectId: string;
  initiatives: Initiative[];
}
export const InitiativesSection = (props: InitiativesSectionProps) => { ... };

// ✅ Correct - shared domain types in types file
// src/types/initiative.ts
export interface InitiativeStep {
  key: string;
  labelKey: string;
  isCompleted: boolean;
}
export interface InitiativeUpdates {
  status?: string;
  startDate?: string | null;
}
```

## Hooks - Extract Complex Logic

- **Extract complex logic** from components into custom hooks
- Create hooks when a component has:
  - Multiple related `useEffect` hooks
  - Complex calculations with `useMemo`
  - Scroll/resize/event listener management
  - Timeline/date calculations
  - State management that involves filtering, transforming, or syncing data
  - Update handlers that modify data and track changes

```tsx
// ❌ Incorrect - logic mixed in component
const ProjectsView = () => {
  const [viewMode, setViewMode] = useState('grid');
  const [statusFilter, setStatusFilter] = useState('all');
  const [hasChanges, setHasChanges] = useState(false);
  const filteredItems = useMemo(() => { /* filtering */ }, []);
  const handleUpdate = useCallback(async (id, updates) => {
    await updateProject(id, updates);
    setHasChanges(true);
  }, []);
  useEffect(() => { /* sync on view change */ }, [viewMode]);
  // ... more logic
};

// ✅ Correct - extract to hook
const ProjectsView = () => {
  const {
    viewMode,
    setViewMode,
    statusFilter,
    setStatusFilter,
    filteredItems,
    handleUpdate,
  } = useProjectsRoadmap({ projects, updateProject, loadProjects });
  // Component focuses on rendering
};
```

## Reusable UI Components

- **Extract repeated UI patterns** into reusable components
- If the same UI element appears in multiple places, create a shared component
- Components should be in `src/components/` organized by domain

```tsx
// ❌ Incorrect - duplicated dropdown in multiple files
<div className="relative">
  <select value={filter} onChange={(e) => setFilter(e.target.value)}>
    <option value="all">{t('allStatuses')}</option>
    {options.map((opt) => <option key={opt.value}>{t(opt.labelKey)}</option>)}
  </select>
  <ChevronDownIcon />
</div>

// ✅ Correct - reusable component
import { StatusFilter } from '@/components/roadmap/StatusFilter';
<StatusFilter value={filter} onChange={setFilter} options={STATUS_OPTIONS} />
```

## TypeScript Generics

- Use **generics** for components/hooks that work with different data types sharing a base interface
- This provides type safety while avoiding code duplication

```ts
// ❌ Incorrect - loses type information
const useRoadmap = (items: RoadmapItem[]) => {
  // Returns generic RoadmapItem, loses specific properties
};

// ✅ Correct - preserves specific type
const useRoadmap = <T extends RoadmapItem>(items: T[]) => {
  const filtered: T[] = items.filter(/* ... */);
  return { filtered }; // Type T is preserved
};
// Usage - TypeScript knows filteredProjects is ProjectCard[]
const { filteredProjects } = useProjectsRoadmap({ projects });
```

## Avoid Hardcoded Values

- **Never hardcode dates** - use relative calculations with `date-fns`
- **Never hardcode magic numbers** - extract to named constants with comments
- Configuration should be adjustable in one place

```ts
// ❌ Incorrect - hardcoded dates
const TIMELINE_START = new Date(2025, 5, 1); // June 2025
const TIMELINE_END = new Date(2027, 11, 31); // December 2027

// ✅ Correct - dynamic relative to current date
import { startOfMonth, addMonths, subMonths } from 'date-fns';
const TIMELINE_CONFIG = {
  monthsBefore: 12,
  monthsAfter: 18,
};
const getTimelineRange = () => {
  const now = new Date();
  return {
    start: startOfMonth(subMonths(now, TIMELINE_CONFIG.monthsBefore)),
    end: endOfMonth(addMonths(now, TIMELINE_CONFIG.monthsAfter)),
  };
};
```

## Barrel Files (index.ts)

- **Never use barrel files** for exports
- Import directly from the source file
- Reference: <https://tkdodo.eu/blog/please-stop-using-barrel-files>

```ts
// ❌ Incorrect - barrel export
// src/components/roadmap/index.ts
export { ViewToggle } from './ViewToggle';
export { RoadmapView } from './RoadmapView';

// ❌ Incorrect - import from barrel
import { ViewToggle, RoadmapView } from '@/components/roadmap';

// ✅ Correct - direct imports
import { ViewToggle } from '@/components/roadmap/ViewToggle';
import { RoadmapView } from '@/components/roadmap/RoadmapView';
```

## File Size Guidelines

- Keep component files **under 200 lines** when possible
- If a file exceeds 300 lines, it likely needs refactoring:
  - Extract hooks for logic
  - Extract sub-components for UI sections
  - Move constants to `src/constants/`
  - Move types to `src/types/`

## Code Review Checklist

When creating or modifying code, verify:

1. [ ] Constants are in `src/constants/` (not inline)
2. [ ] **Component props are in the component file** (not in `src/types/`)
3. [ ] Shared domain types are in `src/types/` (check for existing types first)
4. [ ] Complex logic is extracted to hooks in `src/hooks/`
5. [ ] Repeated UI patterns are extracted to components
6. [ ] No barrel files (`index.ts`) for exports
7. [ ] Direct imports instead of barrel imports
8. [ ] No hardcoded dates - use date-fns with relative calculations
9. [ ] Generics used when handling multiple types with shared interface
10. [ ] File size is under 300 lines
