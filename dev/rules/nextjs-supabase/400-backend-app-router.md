---
description: Backend - Route Handlers and Server Actions
globs:
  - "app/api/**/*"
  - "actions/**/*"
alwaysApply: true
---

# New Backend - App Router & Server Actions

- New endpoints → `app/api/.../route.ts` (`NextResponse`)
- Mutations → Prefer Server Actions in `/actions` (`'use server'`)
- Use Pino logger (`createApiLogger` for handlers)
- Zod validation (`safeParse` on URL/searchParams or formData)
- Call services as usual
- After mutation: `revalidatePath()` or `revalidateTag()`
- Server Actions example return: `{ success: true, data }` or `{ success: false, error }`
