# PSMS Frontend

Primary School Management System — frontend in Next.js 16, App Router.
Backend is a separate Django API; we never call it directly from the browser.

## Source of truth
- Project goals, milestones, roles: see `docs/project_spec.md`
- Architecture, layers, security model: see `docs/architecture.md`

Read these before non-trivial work. If a request conflicts with them, flag it.

## Dependencies:**
- Prefer Shadcn components over adding new UI libraries

## Repository Etiquette

**Branching:**
- ALWAYS create a feature branch before starting major changes
- NEVER commit directly to main
- Branch naming: `feature/description` or `fix-description`

**Git workflow for major changes:**
1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Develop and commit on the feature branch
3. Test locally before pushing:
   - `npm run dev` - start dev server at localhost:3000
   - `npm run lint` - check for linting errors
   - `npm run build` - production build to check type errors
4. Push the branch: `git push -u origin feature/your-feature-name`
5. Use the `update-docs-and-commit` slash command for commits - this ensures docs are updated alongside code changes

**Commits:**
- Write clear commit messages describing the change
- Keep commits focused on single changes

**Pull Requests:**
- NEVER force push to `main`
- Include descriptions of what changed and why

**Before Pushing:**
- Run `npm run lint`
- Run `npm run build` to catch type errors 

## Commands
- `npm dev` — start dev server (Turbopack, default in Next.js 16)
- `npm build` — production build (Turbopack)
- `npm lint` — ESLint
- `npm typecheck` — `tsc --noEmit`
- `npm test` — Vitest

# Claude Code Configuration
- Pre-commit hook: `npm run lint`
- Test command: `npm test`
- Build command: `npm run build`


## Hard rules (non-negotiable)
- JWTs go in HttpOnly cookies only. Never localStorage, sessionStorage, or any JS variable.
- Browser never calls Django directly. All API traffic goes through Route Handlers under `app/api/*` that inject the bearer token server-side.
- Authorisation lives in `middleware.ts` at the Edge. Don't re-implement role checks in pages.
- Server Components by default. `"use client"` only when interactivity actually requires it.
- `dangerouslySetInnerHTML` is banned (ESLint enforced).
- `medicalNotes` is admin-only; never render it in accountant or parent spaces.

## Conventions
- TypeScript strict, no `any`.
- Types per module in `lib/types/[module].ts`.
- PascalCase components, camelCase functions, SCREAMING_SNAKE_CASE constants.
- Zod schemas co-located with their types; reused server-side in Route Handlers.

## What not to do
- Don't add a webpack config — Next.js 16 builds with Turbopack by default and a webpack-only config will fail the build.
- Don't put secrets behind `NEXT_PUBLIC_*` — those leak into the browser bundle.
- Don't refactor `middleware.ts` without re-reading the RBAC section of architecture.md.