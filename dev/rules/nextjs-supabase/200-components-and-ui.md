---
description: Component and ShadCN UI rules
globs:
  - "components/**/*"
  - "src/components/**/*"
alwaysApply: true
---

# Components & ShadCN UI

- All basic UI (buttons, inputs, cards, etc.) → ShadCN only.
- Add via: `npx shadcn@latest add [name]` → place in `/components/ui` or `/src/components/ui`.
- Composite/domain components → `/components` (outside `/ui`).
- Reusable → `/components`; route-specific can be colocated.
- Always use ShadCN variants/props correctly.
- Never recreate primitives if ShadCN provides one.
- Ensure accessibility and Tailwind consistency.

## Component Declaration

- **Always use arrow functions** for React components and hooks:

```tsx
// ✅ Correct
export const MyComponent = ({ prop }: Props) => {
  return <div>...</div>;
};

// ❌ Incorrect
export function MyComponent({ prop }: Props) {
  return <div>...</div>;
}
```

## Type Definitions

- **All types must be defined in `src/types/`** directory, organized by domain
- **Check existing types** before creating new ones - reuse when possible
- **Never define types inline** in components - extract to type files
- **Use `type` imports** for types: `import type { MyType } from '@/types/...'`

## Icon Components

- **All SVG icons must be extracted** to `src/components/icons/` as reusable components
- **Never use inline SVG** in components
- Icon components should accept `className` prop for styling
- Example: `src/components/icons/LanguageIcon.tsx`

## File Organization

- Types: `src/types/{domain}.ts` (e.g., `project.ts`, `navbar.ts`)
- Icons: `src/components/icons/{Name}Icon.tsx`
- Components: `src/components/{domain}/{ComponentName}.tsx`

## Component Prop Types

- **Never define prop types inline** in component files
- **Extract all prop types** to `src/types/` directory, organized by domain
- **Component-specific types** (like `ButtonVariant`, `ButtonSize`) should go in `src/types/ui.ts` or appropriate domain file
- **Reuse existing types** before creating new ones

```ts
// ✅ Correct - Types extracted to src/types/ui.ts
import type { ButtonVariant, ButtonSize } from '@/types/ui';

export interface ButtonProps {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

// ❌ Incorrect - Types defined inline
export interface ButtonProps {
  variant?: "default" | "destructive" | "outline";
  size?: "default" | "sm" | "lg";
}
```

## Code Review Checklist

When reviewing code, ensure:

1. Components use arrow functions
2. Types are in `src/types/` directory
3. Existing types are reused
4. SVG icons are in `src/components/icons/`
5. No inline type definitions (including prop types)
6. Type imports use `type` keyword
7. Component prop types are extracted to type files
