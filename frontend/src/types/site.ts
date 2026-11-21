/** GET /api/v1/site/: everything the public landing page shows. */

export interface MenuItem {
  id: number
  name: string
  description: string
  /** Guaraníes, whole units. */
  price: number
  /** Relative URL (/media/...), or null when there's no photo. */
  photo: string | null
  is_available: boolean
  is_featured: boolean
}

export interface MenuCategory {
  id: number
  name: string
  slug: string
  description: string
  items: MenuItem[]
}

export interface OpeningHoursLine {
  days: string
  hours: string
}

export interface Restaurant {
  name: string
  tagline: string
  about: string
  hero_image: string | null
  about_image: string | null
  address: string
  city: string
  maps_url: string
  phone: string
  whatsapp: string
  instagram_url: string
  facebook_url: string
  menu_note: string
  hours: OpeningHoursLine[]
}

export interface GalleryPhoto {
  id: number
  image: string
  caption: string
}

/** Attribution for a third-party photo on the page (e.g. Wikimedia Commons). */
export interface PhotoCredit {
  subject: string
  credit: string
  url: string
}

export interface SiteContent {
  restaurant: Restaurant
  featured: MenuItem[]
  categories: MenuCategory[]
  gallery: GalleryPhoto[]
  credits: PhotoCredit[]
}
