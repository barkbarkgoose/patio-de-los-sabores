import { describe, expect, it } from 'vitest'
import type { MenuCategory } from '@/types/site'
import { categoryAccent, filterMenuCategories, normalizeSearchText } from '../menuTheme'

const SAMPLE_CATEGORIES: MenuCategory[] = [
  {
    id: 1,
    slug: 'para-compartir',
    name: 'Para compartir',
    description: 'Clásicos para empezar',
    items: [
      {
        id: 10,
        name: 'Mbejú',
        description: 'Almidón de mandioca y queso',
        price: 15000,
        photo: null,
        is_available: true,
        is_featured: false,
      },
      {
        id: 11,
        name: 'Chipa guasu',
        description: 'Pastel de choclo fresco',
        price: 18000,
        photo: null,
        is_available: true,
        is_featured: true,
      },
    ],
  },
  {
    id: 2,
    slug: 'parrilla',
    name: 'Parrilla',
    description: 'A la leña',
    items: [
      {
        id: 20,
        name: 'Costilla de res',
        description: 'Costilla a la leña',
        price: 60000,
        photo: null,
        is_available: false,
        is_featured: true,
      },
    ],
  },
]

describe('menuTheme', () => {
  it('assigns semantic accents by Spanish menu slug and cycles unknown slugs', () => {
    expect(categoryAccent('para-compartir', 0)).toBe('sol')
    expect(categoryAccent('parrilla', 2)).toBe('brasa')
    expect(categoryAccent('postres', 3)).toBe('lapacho')
    expect(categoryAccent('bebidas', 4)).toBe('selva')
    expect(categoryAccent('especiales-del-dia', 1)).toBe('terracota')
  })

  it('normalizes accents and casing for mobile search', () => {
    expect(normalizeSearchText('  Mbejú & Mamón  ')).toBe('mbeju & mamon')
  })

  it('filters dishes accent-insensitively and omits empty categories', () => {
    const result = filterMenuCategories(SAMPLE_CATEGORIES, {
      query: 'mbeju',
      onlyFeatured: false,
      onlyAvailable: false,
    })
    expect(result).toHaveLength(1)
    expect(result[0].items.map((item) => item.name)).toEqual(['Mbejú'])
  })

  it('combines featured and available filters', () => {
    const result = filterMenuCategories(SAMPLE_CATEGORIES, {
      query: '',
      onlyFeatured: true,
      onlyAvailable: true,
    })
    expect(result).toHaveLength(1)
    expect(result[0].items.map((item) => item.name)).toEqual(['Chipa guasu'])
  })
})
