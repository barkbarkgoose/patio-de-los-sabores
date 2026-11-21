# Phase 1: Project Scaffolding

**Source:** PROJECT_BLUEPRINT.md, Phase 1
**Goal:** Reconcile the copied Django/Vue boilerplate with the Patio de los Sabores MVP structure, dependencies, environment files, Tailwind setup, and make it runnable for local development.
**Validation gate:** Run `uv run python manage.py check` from `backend/` with no errors, and run `npm run build` from `frontend/` with no errors.

---

## Work Items

### 1. Backend Environment Setup & Validation
**Category:** Scaffolding / Configuration
**Dependencies:** None | None
**Parallel with:** 2. Frontend Environment Setup
**What to do:**
- Verify the existing Django project structure in `backend/`.
- Ensure `requirements.txt` accurately reflects all dependencies needed for the MVP (e.g., DRF, core packages).
- Verify settings split and ensure `.env.example` is robust for both local development and initial API usage.
- Run necessary checks to confirm Django's ability to run basic migrations without error against a dummy database or SQLite in memory.
**Scope:** `backend/`, `requirements.txt`, `.env.*` files.
**Validation:**
- [X] Execute `uv run python manage.py check` from the `backend/` directory and confirm zero errors.

---

### 2. Frontend Environment Setup & Validation
**Category:** Scaffolding / Configuration
**Dependencies:** None | None
**Parallel with:** 1. Backend Environment Setup & Validation
**What to do:**
- Verify the existing Vue project structure in `frontend/`.
- Ensure `package.json` scripts (especially for build) and dependency list are correct for Vite, TypeScript, Pinia, and Tailwind CSS setup.
- Validate that environment variables (`.env`) correctly manage API base URLs (using the contract's `/api/v1`).
- Run a local build attempt to ensure the boilerplate compiles without immediate errors.
**Scope:** `frontend/`, `package.json`, `.env.*` files.
**Validation:**
- [X] Execute `npm run build` from the `frontend/` directory and confirm zero build errors.

---

### 3. Infrastructure Consistency & Code Cleanup (Shared)
**Category:** Integration / Scaffolding
**Dependencies:** 1. Backend Environment Setup & Validation, 2. Frontend Environment Setup & Validation
**Parallel with:** None
**What to do:**
- Standardize tooling: Add or confirm the presence of `.python-version`, `.nvmrc`, and a comprehensive `.gitignore` across both services root folders (`backend/` and `frontend/`).
- Proxy Configuration: Confirm that Vite proxy configuration (in `vite.config.ts`) correctly routes `/api`, `/admin`, and `/static` requests to the backend running at port `8800`.
- Boilerplate cleanup: Remove or mark for removal any public-facing authentication redirects (`/login`, `/dashboard`) so that the root path (`/`) defaults to rendering the restaurant landing page component.
**Scope:** Project roots, `.gitignore`, frontend configuration files.
**Validation:**
- [X] A successful check of proxy routing via `npm run dev` (frontend) and a confirmed working connection to backend endpoints.

---

### 4. Styling System Implementation (Shared)
**Category:** Components / Configuration
**Dependencies:** None | None
**Parallel with:** 1. Backend Environment Setup & Validation, 2. Frontend Environment Setup & Validation
**What to do:**
- **Theme Tokens:** Update CSS variables/Tailwind theme configuration in both services' style layers to use the restaurant brand colors: `--color-primary` (`#8b3a1d`), `--color-secondary` (`#2f5d50`), etc.
- **Component Library:** Implement all BEM component classes defined in `PROJECT_BLUEPRINT.md` (e.g., `.menu-card`, `.btn`) within the primary SCSS files of both services, ensuring consistency with Tailwind utilities where applicable.
**Scope:** Shared CSS/SCSS assets and theme config files.
**Validation:**
- [X] Inspect a sample component page (`frontend/src/App.vue` or similar) and confirm that all major elements are styled using the new BEM classes and defined tokens, with no utility class sprawl observed in critical components.

---

## Execution Order

1. Items 1, 2, and 4 can run in parallel (they mostly deal with setup/configuration).
2. Item 3 must wait for all of items 1, 2, and 4 to have been implemented so that the environment is fully consistent before checking infrastructure links.

## Phase Complete When

- [ ] All work items complete
- [ ] Phase validation gate passes: Backend checks pass, frontend builds successfully, proxy routing works, and initial styling is applied consistently across the scaffolded components.