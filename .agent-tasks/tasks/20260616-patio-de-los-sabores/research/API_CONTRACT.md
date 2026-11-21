# API Contract: Patio de los Sabores

**Version:** 1.0
**Base URL:** `/api/v1`
**Auth:** Bearer JWT for staff endpoints; public endpoints require no auth

---

## Conventions

- Public language selection uses `?lang=<language_code>`.
- If `lang` is omitted, the backend uses the default language.
- If a requested translation is missing, translated fields fall back to the default language.
- Public menu responses include only published categories and published menu items.
- Staff endpoints require an authenticated staff user.
- List endpoints use DRF pagination unless explicitly marked unpaginated.

## Authentication

### POST /api/v1/auth/login/

**Auth required:** No

**Request:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "access": "string (JWT)",
  "refresh": "string (JWT)"
}
```

**Errors:**
- 401: `{ "detail": "No active account found with the given credentials" }`

---

### POST /api/v1/auth/refresh/

**Auth required:** No

**Request:**
```json
{
  "refresh": "string (JWT)"
}
```

**Response (200):**
```json
{
  "access": "string (JWT)"
}
```

**Errors:**
- 401: `{ "detail": "Token is invalid or expired" }`

---

## Public Languages

### GET /api/v1/languages/

**Auth required:** No

**Query params:** None

**Response (200):**
```json
{
  "default_language": "en",
  "results": [
    {
      "code": "en",
      "name": "English",
      "is_default": true
    },
    {
      "code": "es",
      "name": "Spanish",
      "is_default": false
    }
  ]
}
```

---

## Public Restaurant Profile

### GET /api/v1/public/profile/

**Auth required:** No

**Query params:**
- `lang` (string, optional, default: default language)

**Response (200):**
```json
{
  "id": 1,
  "name": "Patio de los Sabores",
  "city": "Emboscada",
  "country": "Paraguay",
  "phone": "string | null",
  "address": "string | null",
  "opening_hours": "string | null",
  "language": "en",
  "fallback_language": "en",
  "tagline": "Fresh flavors from Emboscada",
  "intro": "string"
}
```

**Errors:**
- 404: `{ "detail": "Restaurant profile not found." }`

---

## Public Menu

### GET /api/v1/public/menu/

**Auth required:** No

**Query params:**
- `lang` (string, optional, default: default language)
- `featured` (boolean, optional)

**Response (200):**
```json
{
  "language": "en",
  "fallback_language": "en",
  "currency": "PYG",
  "categories": [
    {
      "id": 1,
      "slug": "starters",
      "name": "Starters",
      "description": "Small plates to begin with.",
      "sort_order": 1,
      "items": [
        {
          "id": 10,
          "category_id": 1,
          "slug": "mandioca-frita",
          "name": "Fried Mandioca",
          "description": "Crispy mandioca served with house sauce.",
          "price": 25000,
          "currency": "PYG",
          "is_available": true,
          "is_featured": true,
          "sort_order": 1
        }
      ]
    }
  ]
}
```

**Errors:**
- 400: `{ "lang": ["Unsupported language code."] }`

---

## Staff Menu Categories

### GET /api/v1/staff/menu-categories/

**Auth required:** Yes, staff only

**Query params:**
- `page` (number, default: 1)
- `page_size` (number, default: 20)
- `search` (string, optional)
- `ordering` (string, optional, examples: `sort_order`, `-created_at`)

**Response (200):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "slug": "starters",
      "is_published": true,
      "sort_order": 1,
      "translations": [
        {
          "language": "en",
          "name": "Starters",
          "description": "Small plates to begin with."
        },
        {
          "language": "es",
          "name": "Entradas",
          "description": "Platos pequenos para empezar."
        }
      ],
      "created_at": "ISO 8601 datetime",
      "updated_at": "ISO 8601 datetime"
    }
  ]
}
```

---

### POST /api/v1/staff/menu-categories/

**Auth required:** Yes, staff only

**Request:**
```json
{
  "slug": "starters",
  "is_published": true,
  "sort_order": 1,
  "translations": [
    {
      "language": "en",
      "name": "Starters",
      "description": "Small plates to begin with."
    },
    {
      "language": "es",
      "name": "Entradas",
      "description": "Platos pequenos para empezar."
    }
  ]
}
```

**Response (201):**
```json
{
  "id": 1,
  "slug": "starters",
  "is_published": true,
  "sort_order": 1,
  "translations": [
    {
      "language": "en",
      "name": "Starters",
      "description": "Small plates to begin with."
    }
  ],
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

**Errors:**
- 400: `{ "slug": ["This field is required."] }`
- 400: `{ "translations": ["A translation for the default language is required."] }`
- 401: `{ "detail": "Authentication credentials were not provided." }`
- 403: `{ "detail": "You do not have permission to perform this action." }`

---

### GET /api/v1/staff/menu-categories/:id/

**Auth required:** Yes, staff only

**Response (200):** Same shape as category create response.

**Errors:**
- 404: `{ "detail": "Not found." }`

---

### PATCH /api/v1/staff/menu-categories/:id/

**Auth required:** Yes, staff only

**Request:** Partial category object.

**Response (200):** Same shape as category create response.

**Errors:**
- 400: `{ "translations": ["Duplicate language translation."] }`
- 404: `{ "detail": "Not found." }`

---

### DELETE /api/v1/staff/menu-categories/:id/

**Auth required:** Yes, staff only

**Response:** 204 No Content

**Errors:**
- 404: `{ "detail": "Not found." }`

---

## Staff Menu Items

### GET /api/v1/staff/menu-items/

**Auth required:** Yes, staff only

**Query params:**
- `page` (number, default: 1)
- `page_size` (number, default: 20)
- `category` (number, optional)
- `is_published` (boolean, optional)
- `is_available` (boolean, optional)
- `search` (string, optional)
- `ordering` (string, optional, examples: `sort_order`, `-created_at`)

**Response (200):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 10,
      "category": 1,
      "slug": "mandioca-frita",
      "price": 25000,
      "currency": "PYG",
      "is_available": true,
      "is_published": true,
      "is_featured": true,
      "sort_order": 1,
      "translations": [
        {
          "language": "en",
          "name": "Fried Mandioca",
          "description": "Crispy mandioca served with house sauce."
        },
        {
          "language": "es",
          "name": "Mandioca frita",
          "description": "Mandioca crocante con salsa de la casa."
        }
      ],
      "created_at": "ISO 8601 datetime",
      "updated_at": "ISO 8601 datetime"
    }
  ]
}
```

---

### POST /api/v1/staff/menu-items/

**Auth required:** Yes, staff only

**Request:**
```json
{
  "category": 1,
  "slug": "mandioca-frita",
  "price": 25000,
  "currency": "PYG",
  "is_available": true,
  "is_published": true,
  "is_featured": true,
  "sort_order": 1,
  "translations": [
    {
      "language": "en",
      "name": "Fried Mandioca",
      "description": "Crispy mandioca served with house sauce."
    },
    {
      "language": "es",
      "name": "Mandioca frita",
      "description": "Mandioca crocante con salsa de la casa."
    }
  ]
}
```

**Response (201):** Same shape as staff menu item list result object.

**Errors:**
- 400: `{ "category": ["This field is required."] }`
- 400: `{ "price": ["Ensure this value is greater than or equal to 0."] }`
- 400: `{ "translations": ["A translation for the default language is required."] }`
- 401: `{ "detail": "Authentication credentials were not provided." }`
- 403: `{ "detail": "You do not have permission to perform this action." }`

---

### GET /api/v1/staff/menu-items/:id/

**Auth required:** Yes, staff only

**Response (200):** Same shape as staff menu item list result object.

**Errors:**
- 404: `{ "detail": "Not found." }`

---

### PATCH /api/v1/staff/menu-items/:id/

**Auth required:** Yes, staff only

**Request:** Partial item object.

**Response (200):** Same shape as staff menu item list result object.

**Errors:**
- 400: `{ "translations": ["Duplicate language translation."] }`
- 404: `{ "detail": "Not found." }`

---

### DELETE /api/v1/staff/menu-items/:id/

**Auth required:** Yes, staff only

**Response:** 204 No Content

**Errors:**
- 404: `{ "detail": "Not found." }`

---

## Static UI Translation Map

The frontend owns static UI labels that are not restaurant-managed content. The initial map should use this shape and allow adding new language keys later.

```ts
export const messages = {
  en: {
    nav: {
      menu: 'Menu',
      location: 'Location',
      contact: 'Contact'
    },
    menu: {
      unavailable: 'Temporarily unavailable',
      featured: 'Featured',
      empty: 'Menu items will be available soon.'
    },
    language: {
      label: 'Language',
      english: 'English',
      spanish: 'Spanish'
    }
  },
  es: {
    nav: {
      menu: 'Menu',
      location: 'Ubicacion',
      contact: 'Contacto'
    },
    menu: {
      unavailable: 'Temporalmente no disponible',
      featured: 'Destacado',
      empty: 'Los platos estaran disponibles pronto.'
    },
    language: {
      label: 'Idioma',
      english: 'Ingles',
      spanish: 'Espanol'
    }
  }
} as const
```
