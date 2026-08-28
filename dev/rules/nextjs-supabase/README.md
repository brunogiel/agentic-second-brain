# Next.js + Supabase

Para repos con **Next.js (App Router) + TypeScript + ShadCN + TanStack Query + Supabase**, con
arquitectura por capas: handler, service, repository.

| # | Archivo | Qué cubre |
|---|---|---|
| 000 | `000-core-project.md` | Best practices generales, data fetching, estructura de carpetas |
| 050 | `050-build-and-worktrees.md` | Turbopack y worktrees: un `node_modules` symlinkeado rompe el build |
| 100 | `100-frontend-app-router.md` | Server components por default, route handlers, server actions |
| 125 | `125-frontend-data-fetching.md` | Fetches en paralelo, bundle size, cliente contra servidor |
| 200 | `200-components-and-ui.md` | Componentes, tipos, iconos, props |
| 250 | `250-code-organization.md` | Constantes, dónde viven los tipos, extracción de hooks, sin barrel files |
| 275 | `275-performance-organization.md` | Memo, lazy init, un solo pase por loop |
| 300 | `300-backend-general.md` | Arquitectura por capas: handler → validación → service → base |
| 400 | `400-backend-app-router.md` | Route handlers y server actions, logging, validación, revalidate |
| 410 | `410-backend-clean-architecture.md` | Controller, service, repository, y sus anti-patterns |
| 500 | `500-supabase-and-security.md` | **La más crítica:** las llamadas a la base van del lado del servidor |

## Antes de copiarlas

- Los `globs:` del frontmatter asumen `src/` o `app/`. Si tu repo no los usa, ajustalos o las
  reglas no se activan nunca.
- **La 500 es la que no es opcional.** Las otras son criterio; esa es seguridad.
- La 125 y la 275 son optimizaciones y vienen como `alwaysApply: false`, para activarlas por
  archivo cuando hagan falta.
