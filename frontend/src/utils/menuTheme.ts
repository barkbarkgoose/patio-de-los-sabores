import type { MenuCategory } from '@/types/site'

export type CategoryAccent = 'sol' | 'terracota' | 'brasa' | 'lapacho' | 'selva' | 'cielo'

const ACCENT_CYCLE: CategoryAccent[] = ['sol', 'terracota', 'brasa', 'lapacho', 'selva', 'cielo']

const SLUG_ACCENT_HINTS: Array<{ match: RegExp; accent: CategoryAccent }> = [
  { match: /compartir|entrada|chipa|picada/i, accent: 'sol' },
  { match: /principal|plato|guiso|sopa|caldo/i, accent: 'cielo' },
  { match: /parrilla|asado|brasa|carne/i, accent: 'brasa' },
  { match: /postre|dulce|helado|merienda/i, accent: 'lapacho' },
  { match: /bebida|trago|terere|jugo|cerveza/i, accent: 'selva' },
]

/**
 * Pick a lively Paraguayan patio accent for a menu category.
 * Matches common Spanish menu slugs first, then falls back to a stable cycle.
 */
export function categoryAccent(slug: string, index: number): CategoryAccent {
  const hint = SLUG_ACCENT_HINTS.find((entry) => entry.match.test(slug))
  return hint ? hint.accent : ACCENT_CYCLE[index % ACCENT_CYCLE.length]
}

/** Lowercase and strip accents so "mbeju" matches "Mbejú" on mobile keyboards. */
export function normalizeSearchText(value: string): string {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
}

export interface MenuFilterOptions {
  query: string
  onlyFeatured: boolean
  onlyAvailable: boolean
}

/** Filter categories and their items while dropping categories that become empty. */
export function filterMenuCategories(
  categories: MenuCategory[],
  options: MenuFilterOptions
): MenuCategory[] {
  const needle = normalizeSearchText(options.query)

  return categories
    .map((category) => {
      const categoryMatches =
        needle.length > 0 &&
        (normalizeSearchText(category.name).includes(needle) ||
          normalizeSearchText(category.description).includes(needle))

      const items = category.items.filter((item) => {
        if (options.onlyFeatured && !item.is_featured) return false
        if (options.onlyAvailable && !item.is_available) return false
        if (!needle || categoryMatches) return true
        return (
          normalizeSearchText(item.name).includes(needle) ||
          normalizeSearchText(item.description).includes(needle)
        )
      })

      return { ...category, items }
    })
    .filter((category) => category.items.length > 0)
}
