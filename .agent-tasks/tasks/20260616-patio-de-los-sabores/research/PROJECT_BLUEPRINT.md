# Project Blueprint: Patio de los Sabores

**Created:** 2026-06-16
**Status:** Draft
**Stack:** Django + DRF / Vue 3 + TypeScript / SQLite

---

## 1. Overview

Patio de los Sabores is a public restaurant website for a small restaurant in Emboscada, Paraguay. The MVP focuses on a polished landing page that displays dynamic restaurant information and menu content managed from a Django backend.

The site will be built in English first, with Spanish available through a translation map and a language-switching frontend. The translation design must support adding more languages later without rewriting the frontend or changing core menu item records.

Restaurant staff will manage menu categories, menu items, descriptions, prices, item availability, and language-specific text from the backend. Public visitors will browse the landing page and menu without authentication.

## 2. Requirements

### Functional Requirements

- [FR-01] Public visitors can view a landing page for Patio de los Sabores.
- [FR-02] Public visitors can view dynamic menu categories and menu items from the backend.
- [FR-03] Menu items include name, description, price, availability, featured state, and ordering controls.
- [FR-04] Restaurant staff can create, update, publish/unpublish, reorder, and delete menu categories.
- [FR-05] Restaurant staff can create, update, publish/unpublish, reorder, and delete menu items.
- [FR-06] The application supports English and Spanish content at launch.
- [FR-07] The language system supports adding more languages later through data/configuration rather than hardcoded conditionals.
- [FR-08] Frontend visitors can switch language between English and Spanish.
- [FR-09] The frontend falls back to the default language when a translation is missing.
- [FR-10] Backend staff access is authenticated and restricted to staff users.
- [FR-11] The Django admin provides a usable interface for menu management in the MVP.
- [FR-12] Public APIs expose only published and available public-facing content.
- [FR-13] The frontend can display restaurant contact/location metadata, including Emboscada, Paraguay.

### Non-Functional Requirements

- [NFR-01] Backend and frontend are independent services with separate dependency management and `.env` files.
- [NFR-02] API responses use stable JSON contracts under `/api/v1/`.
- [NFR-03] The public landing page should load quickly on mobile and desktop.
- [NFR-04] Styling uses Tailwind CSS theme tokens and reusable BEM component classes to avoid utility-class sprawl.
- [NFR-05] The backend remains database-agnostic through the Django ORM; SQLite is used for local MVP development.
- [NFR-06] All staff write operations require authenticated staff permissions.
- [NFR-07] Public endpoints must not expose unpublished categories or unpublished menu items.
- [NFR-08] Translation fallback behavior must be deterministic and covered by tests.

### Assumptions

- The MVP uses Django admin for restaurant staff menu editing instead of a custom admin frontend.
- The copied boilerplate includes an existing custom user, organization model, auth API, and Vue auth/dashboard screens; these should be retained only where useful for staff authentication and should not drive the public homepage experience.
- There is one restaurant/location, not a multi-tenant restaurant platform.
- Public users do not need accounts.
- Staff accounts are created by a superuser in Django admin.
- Prices are stored in Paraguayan Guarani as integer minor units or whole-unit amounts, with display formatting handled by the frontend.
- The default language is English (`en`), and Spanish (`es`) is enabled at launch.
- Images are optional for the MVP; the data model allows adding an image field later but does not require upload/storage setup in Phase 1.
- Online ordering, reservations, payments, delivery integrations, and real-time stock updates are outside the landing-page MVP.

### Out of Scope

- Online ordering or checkout.
- Payment processing.
- Reservation booking.
- Delivery provider integrations.
- Custom staff dashboard frontend.
- Production deployment automation.
- Multi-restaurant tenancy.
- Real-time menu updates via WebSockets.

## 3. Tech Stack

Versions for all technologies are defined in `VERSIONS.md` from the greenfield defaults.

| Layer | Choice | Deviation from default? |
|-------|--------|------------------------|
| Backend | Python + Django + DRF | No |
| Frontend | Node.js LTS + Vue 3 + TypeScript | No |
| State | Pinia | No |
| Styling | Tailwind CSS 4 + SASS/BEM | No |
| Database | SQLite for local MVP | No |
| Auth | Django admin sessions + simplejwt for staff API support | No |
| Environment | uv for backend, npm for frontend | No |

No stack deviations are required for the MVP. Docker is not required initially because there are no service dependencies beyond SQLite.

## 4. Design System

### Theme Tokens

Use CSS custom properties as the source of truth for brand colors. Tailwind theme entries should reference these tokens.

| Token | Value | Purpose |
|-------|-------|---------|
| `--color-primary` | `#8b3a1d` | Warm terracotta restaurant brand color |
| `--color-primary-dark` | `#642814` | Primary hover/active states |
| `--color-primary-light` | `#c96f45` | Highlights and accents |
| `--color-secondary` | `#2f5d50` | Herbal green supporting color |
| `--color-secondary-dark` | `#1f4037` | Secondary hover/active states |
| `--color-surface` | `#fff8ef` | Warm page background |
| `--color-error` | `#b91c1c` | Validation and error states |
| `--color-success` | `#15803d` | Success states |

### BEM Component Classes

Define reusable classes in `frontend/src/assets/styles/main.scss` under `@layer components`:

- `.btn`, `.btn--primary`, `.btn--secondary`, `.btn--ghost`, `.btn--disabled`
- `.nav-link`, `.nav-link--active`, `.nav-link--inactive`
- `.menu-card`, `.menu-card__header`, `.menu-card__title`, `.menu-card__description`, `.menu-card__price`, `.menu-card--featured`, `.menu-card--unavailable`
- `.section`, `.section__eyebrow`, `.section__title`, `.section__body`
- `.language-switcher`, `.language-switcher__option`, `.language-switcher__option--active`
- `.alert`, `.alert--error`, `.alert--success`, `.alert__title`, `.alert__text`
- `.form-input`, `.form-input--error`

### Spacing Scale

Use only these spacing steps for layout decisions unless a component has a specific visual need: `2`, `4`, `6`, `8`, `12`, `16`, `24`, `32`.

### Typography Ramp

| Style | Use |
|-------|-----|
| Display | Landing hero title |
| H1 | Page-level title |
| H2 | Section titles |
| H3 | Menu category titles |
| Body | Descriptions and regular text |
| Caption | Metadata, labels, availability notes |

## 5. Data Model

### Entities

#### Language

| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField | PK |
| code | CharField | max_length=10, unique, examples: `en`, `es` |
| name | CharField | max_length=100 |
| is_default | BooleanField | only one default language should be true |
| is_active | BooleanField | default true |
| sort_order | PositiveIntegerField | default 0 |
| created_at | DateTimeField | auto_now_add |
| updated_at | DateTimeField | auto_now |

**Relationships:** Referenced by category and item translations.

#### RestaurantProfile

| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField | PK |
| name | CharField | max_length=255 |
| city | CharField | max_length=120, default `Emboscada` |
| country | CharField | max_length=120, default `Paraguay` |
| phone | CharField | max_length=50, blank allowed |
| address | TextField | blank allowed |
| opening_hours | TextField | blank allowed |
| default_language | ForeignKey(Language) | PROTECT |
| created_at | DateTimeField | auto_now_add |
| updated_at | DateTimeField | auto_now |

**Relationships:** One profile is expected for the MVP. It points to the default language.

#### RestaurantProfileTranslation

| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField | PK |
| profile | ForeignKey(RestaurantProfile) | CASCADE, related_name=`translations` |
| language | ForeignKey(Language) | PROTECT |
| tagline | CharField | max_length=255, blank allowed |
| intro | TextField | blank allowed |
| created_at | DateTimeField | auto_now_add |
| updated_at | DateTimeField | auto_now |

**Relationships:** Unique constraint on `(profile, language)`.

#### MenuCategory

| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField | PK |
| slug | SlugField | unique |
| is_published | BooleanField | default true |
| sort_order | PositiveIntegerField | default 0 |
| created_at | DateTimeField | auto_now_add |
| updated_at | DateTimeField | auto_now |

**Relationships:** Has many translations and menu items.

#### MenuCategoryTranslation

| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField | PK |
| category | ForeignKey(MenuCategory) | CASCADE, related_name=`translations` |
| language | ForeignKey(Language) | PROTECT |
| name | CharField | max_length=255 |
| description | TextField | blank allowed |
| created_at | DateTimeField | auto_now_add |
| updated_at | DateTimeField | auto_now |

**Relationships:** Unique constraint on `(category, language)`.

#### MenuItem

| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField | PK |
| category | ForeignKey(MenuCategory) | CASCADE, related_name=`items` |
| slug | SlugField | unique |
| price | PositiveIntegerField | stores whole Guarani amount for MVP |
| currency | CharField | max_length=3, default `PYG` |
| is_available | BooleanField | default true |
| is_published | BooleanField | default true |
| is_featured | BooleanField | default false |
| sort_order | PositiveIntegerField | default 0 |
| created_at | DateTimeField | auto_now_add |
| updated_at | DateTimeField | auto_now |

**Relationships:** Belongs to one menu category and has many translations.

#### MenuItemTranslation

| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField | PK |
| item | ForeignKey(MenuItem) | CASCADE, related_name=`translations` |
| language | ForeignKey(Language) | PROTECT |
| name | CharField | max_length=255 |
| description | TextField | blank allowed |
| created_at | DateTimeField | auto_now_add |
| updated_at | DateTimeField | auto_now |

**Relationships:** Unique constraint on `(item, language)`.

### Entity Relationship Summary

A single `RestaurantProfile` defines the restaurant metadata. `Language` records define enabled languages, with English as the default and Spanish active at launch. Translatable text is stored in translation tables tied to profile, menu category, and menu item records. `MenuCategory` groups `MenuItem` records. Public APIs resolve translated fields for the requested language and fall back to the default language when needed.

## 6. Development Phases

### Phase 1: Project Scaffolding

- **Goal:** Reconcile the copied Django/Vue boilerplate with the Patio de los Sabores MVP structure, dependencies, environment files, Tailwind setup, and runnable dev servers.
- **Depends on:** None
- **Parallel streams:** Yes, backend and frontend can scaffold independently.
- **Validation gate:** Run `uv run python manage.py check` from `backend/` with no errors, and run `npm run build` from `frontend/` with no errors.
- **Scope:**
  - Preserve the existing `backend/` Django project and verify DRF, settings split, CORS, `requirements.txt`, and `.env.example` match project needs.
  - Preserve the existing `frontend/` Vue project and verify TypeScript, Vite, Pinia, Vue Router, Axios, Tailwind 4, package scripts, and `.env.example` match project needs.
  - Add missing scaffold details such as `.python-version`, `.nvmrc`, `.gitignore` entries, `backend/static/`, and any dependency required by existing scripts such as `vue-tsc`.
  - Confirm backend dev server is configured for port `8800` and frontend dev server for port `5177`.
  - Confirm Vite proxy covers `/api`, `/admin`, and `/static`.
  - Replace generic boilerplate theme tokens with the restaurant theme tokens and BEM component layer.
  - Remove or repurpose public-facing auth redirects so `/` renders the restaurant landing page instead of redirecting public visitors to login.
  - Decide whether to keep the copied organization model as staff-account metadata or remove it before menu migrations become dependent on it.

### Phase 2: Backend Data Layer and Admin

- **Goal:** Implement restaurant, language, menu category, menu item, and translation models with Django admin management.
- **Depends on:** Phase 1
- **Parallel streams:** No
- **Validation gate:** Run `uv run python manage.py migrate`, create seed menu content, and confirm categories/items are editable in Django admin.
- **Scope:**
  - Create Django app for menu/content management.
  - Implement models and constraints.
  - Register admin classes with inline translations.
  - Add seed data command or fixtures for English and Spanish sample content.
  - Add model/admin tests for translation uniqueness and default language behavior.

### Phase 3: Public Menu API and Staff API

- **Goal:** Expose public landing/menu read endpoints and staff-authenticated CRUD endpoints that follow the API contract.
- **Depends on:** Phase 2
- **Parallel streams:** Yes, frontend can build against `API_CONTRACT.md` while backend implements endpoints.
- **Validation gate:** Public GET requests return seeded published content without auth; staff write requests reject anonymous users and allow staff users.
- **Scope:**
  - Implement serializers with language resolution and fallback.
  - Implement public profile/menu endpoints.
  - Implement staff CRUD viewsets for categories and items.
  - Configure JWT endpoints for future staff API clients.
  - Add API tests for language switching, fallback, published filtering, and permissions.

### Phase 4: Frontend Landing Page

- **Goal:** Build the public landing page that fetches and renders restaurant profile and menu content from the API.
- **Depends on:** Phase 1 and API contract from Phase 3
- **Parallel streams:** Yes, can begin using mocked contract responses before backend endpoints are complete.
- **Validation gate:** Run `npm run build`; with backend seed data running, the landing page renders profile text and menu categories/items in English.
- **Scope:**
  - Create typed API service and TypeScript menu/profile types.
  - Build landing page sections: hero, restaurant intro, featured/menu sections, location/contact, footer.
  - Add loading and error states.
  - Apply responsive desktop/mobile styling using theme tokens and BEM component classes.

### Phase 5: Internationalization Integration

- **Goal:** Add frontend language switching and backend language-aware responses for English and Spanish.
- **Depends on:** Phases 3 and 4
- **Parallel streams:** Yes, frontend language store and backend language query behavior can be verified independently against contract examples.
- **Validation gate:** Switching from `en` to `es` updates landing-page copy and menu content; missing Spanish translations fall back to English.
- **Scope:**
  - Add frontend translation map for static UI labels.
  - Add Pinia language store with active language code and persistence.
  - Fetch API content with `?lang=en` or `?lang=es`.
  - Render backend-provided translated menu/profile fields.
  - Add tests for translation-map fallback and language API parameter handling.

### Phase 6: MVP Polish and Verification

- **Goal:** Harden the MVP with accessibility checks, edge cases, test coverage, and content cleanup.
- **Depends on:** Phases 1-5
- **Parallel streams:** Yes, frontend and backend verification can run independently before final integration.
- **Validation gate:** Run backend tests, frontend build/tests, and manually verify public landing page in English and Spanish on desktop and mobile viewport sizes.
- **Scope:**
  - Improve empty states for unavailable or unpublished menu content.
  - Verify staff-only API permissions.
  - Confirm mobile layout and language switcher accessibility.
  - Add `.env.example` documentation inside each service through comments/examples as appropriate.
  - Ensure no secrets are committed.

## 7. API Contract Reference

See: `API_CONTRACT.md`

## 8. Risks & Open Questions

- Exact restaurant address, phone number, opening hours, tagline, and initial menu content are not provided yet; seed data will use clearly marked placeholders.
- The copied boilerplate includes organization/auth/dashboard functionality beyond the MVP. Keeping it is acceptable if it remains isolated to staff auth; otherwise Phase 1 should trim it before more code depends on it.
- The copied frontend build script uses `vue-tsc`; Phase 1 must verify it is installed or adjust the build script.
- Price formatting for Paraguayan Guarani should be confirmed with real content, especially whether staff prefer thousands separators and whether decimals are ever needed.
- Image support is deferred; if the landing page requires food photos, the plan should add media upload/storage tasks.
- Production deployment target is not specified; deployment-specific settings remain out of scope for MVP planning.
