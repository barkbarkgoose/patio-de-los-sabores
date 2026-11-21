<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import DetailDialog, { type DetailSelection } from '@/components/site/DetailDialog.vue'
import FeatureCard from '@/components/site/FeatureCard.vue'
import MenuItemCard from '@/components/site/MenuItemCard.vue'
import MobileBottomBar from '@/components/site/MobileBottomBar.vue'
import SiteFooter from '@/components/site/SiteFooter.vue'
import SiteHeader from '@/components/site/SiteHeader.vue'
import { fetchSiteContent } from '@/services/site'
import type { GalleryPhoto, MenuCategory, MenuItem, SiteContent } from '@/types/site'
import { telLink, whatsappLink } from '@/utils/format'
import {
  categoryAccent,
  filterMenuCategories,
  type CategoryAccent,
} from '@/utils/menuTheme'

// The restaurant's public website. Everything shown comes from GET /api/v1/site/,
// which staff edit in the Django admin.
const site = ref<SiteContent | null>(null)
const loading = ref(true)
const failed = ref(false)
const activeCategory = ref('')

// Interactive menu filters & detail dialog state
const searchQuery = ref('')
const onlyFeatured = ref(false)
const onlyAvailable = ref(false)
const selectedDetail = ref<DetailSelection | null>(null)
const menuNavRef = ref<HTMLElement | null>(null)

const restaurant = computed(() => site.value?.restaurant)
const name = computed(() => restaurant.value?.name || 'Patio de los Sabores')
const aboutParagraphs = computed(() =>
  (restaurant.value?.about || '').split(/\n\s*\n/).filter((p) => p.trim())
)
const whatsapp = computed(() =>
  whatsappLink(restaurant.value?.whatsapp || '', `¡Hola ${name.value}! Quería consultar…`)
)
const mapsUrl = computed(
  () =>
    restaurant.value?.maps_url ||
    `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
      [restaurant.value?.address, restaurant.value?.city].filter(Boolean).join(', ') ||
        'Emboscada, Paraguay'
    )}`
)
const hasContact = computed(() => {
  const r = restaurant.value
  return !!(r && (r.phone || r.whatsapp || r.instagram_url || r.facebook_url))
})

const categoryAccentMap = computed(() => {
  const map = new Map<number, CategoryAccent>()
  ;(site.value?.categories ?? []).forEach((category, index) => {
    map.set(category.id, categoryAccent(category.slug, index))
  })
  return map
})

const totalDishCount = computed(() =>
  (site.value?.categories ?? []).reduce((sum, category) => sum + category.items.length, 0)
)

const hasUnavailableDishes = computed(() =>
  (site.value?.categories ?? []).some((category) =>
    category.items.some((item) => !item.is_available)
  )
)

const hasActiveFilters = computed(
  () => searchQuery.value.trim().length > 0 || onlyFeatured.value || onlyAvailable.value
)

const filteredCategories = computed<MenuCategory[]>(() =>
  filterMenuCategories(site.value?.categories ?? [], {
    query: searchQuery.value,
    onlyFeatured: onlyFeatured.value,
    onlyAvailable: onlyAvailable.value,
  })
)

const visibleDishCount = computed(() =>
  filteredCategories.value.reduce((sum, category) => sum + category.items.length, 0)
)

const primaryHoursHighlight = computed(() => {
  const hours = restaurant.value?.hours ?? []
  return hours.find((line) => !/cerrado/i.test(line.hours)) ?? hours[0] ?? null
})

function accentForCategory(categoryId: number): CategoryAccent {
  return categoryAccentMap.value.get(categoryId) ?? 'terracota'
}

function findCategoryForItem(itemId: number): MenuCategory | undefined {
  return site.value?.categories.find((cat) => cat.items.some((item) => item.id === itemId))
}

function openDishDetail(item: MenuItem, category?: MenuCategory) {
  const resolvedCategory = category ?? findCategoryForItem(item.id)
  selectedDetail.value = {
    kind: 'dish',
    item,
    categoryName: resolvedCategory?.name,
    accent: resolvedCategory ? accentForCategory(resolvedCategory.id) : 'sol',
  }
}

function openPhotoDetail(photo: GalleryPhoto) {
  selectedDetail.value = { kind: 'photo', photo }
}

function clearFilters() {
  searchQuery.value = ''
  onlyFeatured.value = false
  onlyAvailable.value = false
}

function isClosedHours(hoursText: string): boolean {
  return /^cerrado$/i.test(hoursText.trim())
}

let observer: IntersectionObserver | null = null

// On phones the category bar scrolls sideways: keep the active pill centered
// inside the bar without ever scrolling the page window vertically.
watch(activeCategory, async (slug) => {
  if (!slug) return
  await nextTick()
  const nav = menuNavRef.value
  if (!nav) return
  const link = nav.querySelector<HTMLElement>(`a[href="#menu-${CSS.escape(slug)}"]`)
  if (!link) return
  const targetLeft = link.offsetLeft - (nav.clientWidth - link.offsetWidth) / 2
  const prefersReduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  nav.scrollTo({
    left: Math.max(0, targetLeft),
    behavior: prefersReduced ? 'auto' : 'smooth',
  })
})

// Re-observe menu sections whenever filtered categories change.
watch(
  filteredCategories,
  async (categories) => {
    if (!categories.some((cat) => cat.slug === activeCategory.value)) {
      activeCategory.value = categories[0]?.slug ?? ''
    }
    await nextTick()
    watchCategories()
  },
  { flush: 'post' }
)

// Highlight the category the visitor is reading in the sticky category bar.
function watchCategories() {
  observer?.disconnect()
  observer = new IntersectionObserver(
    (entries) => {
      const visible = entries.filter((e) => e.isIntersecting)
      if (visible.length) activeCategory.value = visible[0].target.id.replace(/^menu-/, '')
    },
    { rootMargin: '-150px 0px -55% 0px' }
  )
  document.querySelectorAll('.menu-category').forEach((el) => observer?.observe(el))
}

async function load() {
  loading.value = true
  failed.value = false
  try {
    site.value = await fetchSiteContent()
  } catch {
    failed.value = true
    return
  } finally {
    loading.value = false
  }
  document.title = `${name.value} · Emboscada`
  activeCategory.value = site.value.categories[0]?.slug ?? ''
  await nextTick()
  watchCategories()
}

onMounted(load)
onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <div class="site">
    <SiteHeader
      :name="name"
      :has-about="aboutParagraphs.length > 0"
      :has-gallery="(site?.gallery.length ?? 0) > 0"
      :whatsapp-href="whatsapp"
    />

    <!-- Hero -->
    <section id="inicio" class="hero" :class="{ 'hero--photo': restaurant?.hero_image }">
      <template v-if="restaurant?.hero_image">
        <img :src="restaurant.hero_image" alt="" class="hero__backdrop" fetchpriority="high" />
        <div class="hero__shade" aria-hidden="true" />
      </template>
      <div v-else class="hero__glow" aria-hidden="true" />

      <div class="container-site hero__inner">
        <p class="hero__eyebrow">
          <span class="hero__star" aria-hidden="true">★</span>
          <span>{{ restaurant?.city || 'Emboscada · Cordillera · Paraguay' }}</span>
        </p>

        <h1 class="hero__title">{{ name }}</h1>

        <p v-if="restaurant?.tagline" class="hero__tagline">{{ restaurant.tagline }}</p>

        <div v-if="primaryHoursHighlight || totalDishCount > 0" class="hero__pills">
          <a v-if="primaryHoursHighlight" href="#visitanos" class="hero__pill">
            <svg class="h-4 w-4 shrink-0 text-oro-bright" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <circle cx="12" cy="12" r="9" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 7v5l3 2" />
            </svg>
            <span>{{ primaryHoursHighlight.days }}: {{ primaryHoursHighlight.hours }}</span>
          </a>
          <a v-if="totalDishCount > 0" href="#menu" class="hero__pill">
            <svg class="h-4 w-4 shrink-0 text-oro-bright" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h10" />
            </svg>
            <span>{{ totalDishCount }} platos en carta</span>
          </a>
        </div>

        <div class="hero__actions">
          <a href="#menu" class="btn btn--primary btn--hero">
            <span>Ver el menú</span>
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14m-6-6 6 6-6 6" />
            </svg>
          </a>
          <a :href="mapsUrl" target="_blank" rel="noopener" class="btn btn--ghost btn--hero">
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 21s-6.5-5.3-6.5-11A6.5 6.5 0 0 1 18.5 10c0 5.7-6.5 11-6.5 11z" />
              <circle cx="12" cy="10" r="2.2" />
            </svg>
            <span>Cómo llegar</span>
          </a>
          <a
            v-if="whatsapp"
            :href="whatsapp"
            target="_blank"
            rel="noopener"
            class="btn btn--whatsapp btn--hero"
          >
            <span>WhatsApp</span>
          </a>
        </div>
      </div>
    </section>
    <div class="tricolor tricolor--thick" aria-hidden="true" />

    <div>
      <!-- Loading / error -->
      <div v-if="loading" class="container-site section" aria-busy="true" aria-label="Cargando">
        <div class="skeleton h-8 w-56" />
        <div class="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="n in 4" :key="n" class="skeleton h-72" />
        </div>
      </div>

      <div v-else-if="failed" class="container-site section">
        <div class="alert alert--error" role="alert">
          <div class="flex items-start gap-3">
            <span class="alert__icon" aria-hidden="true">!</span>
            <div>
              <p class="alert__title">No pudimos cargar el menú.</p>
              <p class="alert__text">Revisá tu conexión e intentá de nuevo.</p>
              <button type="button" class="btn btn--primary mt-4" @click="load">Reintentar</button>
            </div>
          </div>
        </div>
      </div>

      <template v-else-if="site && restaurant">
        <!-- Featured -->
        <section v-if="site.featured.length" id="favoritos" class="section section--sunlit">
          <div class="container-site">
            <div class="section__head">
              <div>
                <p class="section__eyebrow section__eyebrow--terracota">
                  <span aria-hidden="true">★</span> Los favoritos de la casa
                </p>
                <h2 class="section__title">Lo que todos piden</h2>
              </div>
              <p class="section__swipe-hint sm:hidden" aria-hidden="true">Deslizá para ver más →</p>
            </div>

            <div
              class="featured-rail"
              role="region"
              aria-label="Platos favoritos de la casa"
              tabindex="0"
            >
              <FeatureCard
                v-for="item in site.featured"
                :key="item.id"
                :item="item"
                @select="(dish) => openDishDetail(dish)"
              />
            </div>
          </div>
        </section>

        <!-- Menu -->
        <section id="menu" class="section section--menu">
          <div class="container-site">
            <div class="section__head">
              <div>
                <p class="section__eyebrow section__eyebrow--primary">Carta del patio</p>
                <h2 class="section__title">Nuestro menú</h2>
              </div>
              <p v-if="totalDishCount > 0" class="menu-count-pill">
                {{ visibleDishCount }} {{ visibleDishCount === 1 ? 'plato' : 'platos' }}
              </p>
            </div>

            <p v-if="!site.categories.length" class="section__body">
              Estamos preparando el menú. ¡Volvé pronto!
            </p>

            <template v-else>
              <!-- Search & quick filters -->
              <div class="menu-tools">
                <div class="menu-search">
                  <svg class="menu-search__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <circle cx="11" cy="11" r="7" />
                    <path stroke-linecap="round" d="m20 20-3.5-3.5" />
                  </svg>
                  <input
                    v-model="searchQuery"
                    type="search"
                    class="menu-search__input"
                    placeholder="Buscar chipa, parrilla, tereré…"
                    aria-label="Buscar en el menú"
                  />
                  <button
                    v-if="searchQuery"
                    type="button"
                    class="menu-search__clear"
                    aria-label="Borrar búsqueda"
                    @click="searchQuery = ''"
                  >
                    ✕
                  </button>
                </div>

                <div class="menu-filters" role="group" aria-label="Filtros del menú">
                  <button
                    v-if="site.featured.length"
                    type="button"
                    class="filter-chip"
                    :class="{ 'filter-chip--active-sol': onlyFeatured }"
                    :aria-pressed="onlyFeatured"
                    @click="onlyFeatured = !onlyFeatured"
                  >
                    <span aria-hidden="true">★</span>
                    <span>Favoritos</span>
                  </button>

                  <button
                    v-if="hasUnavailableDishes"
                    type="button"
                    class="filter-chip"
                    :class="{ 'filter-chip--active-selva': onlyAvailable }"
                    :aria-pressed="onlyAvailable"
                    @click="onlyAvailable = !onlyAvailable"
                  >
                    <span aria-hidden="true">✓</span>
                    <span>Disponibles</span>
                  </button>

                  <button
                    v-if="hasActiveFilters"
                    type="button"
                    class="filter-chip filter-chip--reset"
                    @click="clearFilters"
                  >
                    Limpiar
                  </button>
                </div>
              </div>

              <!-- Sticky color-coded category bar -->
              <nav
                v-if="filteredCategories.length"
                ref="menuNavRef"
                class="menu-nav"
                aria-label="Categorías del menú"
              >
                <ul class="menu-nav__list">
                  <li v-for="category in filteredCategories" :key="category.id">
                    <a
                      :href="`#menu-${category.slug}`"
                      class="menu-nav__link"
                      :data-accent="accentForCategory(category.id)"
                      :class="{ 'menu-nav__link--active': activeCategory === category.slug }"
                    >
                      <span class="menu-nav__dot" aria-hidden="true" />
                      <span>{{ category.name }}</span>
                    </a>
                  </li>
                </ul>
              </nav>

              <!-- Empty filter state -->
              <div v-if="!filteredCategories.length" class="menu-empty" role="status">
                <p class="menu-empty__title">No encontramos platos con ese filtro.</p>
                <p class="menu-empty__text">
                  Probá con otra palabra o limpiá los filtros para ver toda la carta.
                </p>
                <button type="button" class="btn btn--primary mt-4" @click="clearFilters">
                  Ver todo el menú
                </button>
              </div>

              <!-- Category sections -->
              <section
                v-for="category in filteredCategories"
                :id="`menu-${category.slug}`"
                :key="category.id"
                class="menu-category"
                :data-accent="accentForCategory(category.id)"
              >
                <div class="menu-category__header">
                  <div class="menu-category__title-row">
                    <span class="menu-category__swatch" aria-hidden="true" />
                    <h3 class="menu-category__title">{{ category.name }}</h3>
                    <span class="menu-category__count">{{ category.items.length }}</span>
                  </div>
                  <p v-if="category.description" class="menu-category__description">
                    {{ category.description }}
                  </p>
                </div>

                <ul class="menu-list">
                  <MenuItemCard
                    v-for="item in category.items"
                    :key="item.id"
                    :item="item"
                    :accent="accentForCategory(category.id)"
                    @select="(dish) => openDishDetail(dish, category)"
                  />
                </ul>
              </section>

              <p v-if="restaurant.menu_note" class="menu-note">
                <span aria-hidden="true">✦</span> {{ restaurant.menu_note }}
              </p>
            </template>
          </div>
        </section>

        <!-- About -->
        <section v-if="aboutParagraphs.length" id="nosotros" class="section section--terracota">
          <div class="container-site about" :class="{ 'about--photo': restaurant.about_image }">
            <div class="about__copy">
              <p class="section__eyebrow section__eyebrow--terracota">Nuestro patio</p>
              <h2 class="section__title">Sabores de la Capital de la Piedra</h2>
              <p v-for="(paragraph, i) in aboutParagraphs" :key="i" class="section__body">
                {{ paragraph }}
              </p>
              <div class="mt-8 flex flex-wrap gap-3">
                <a href="#visitanos" class="btn btn--primary">Ver horarios y ubicación</a>
                <a
                  v-if="whatsapp"
                  :href="whatsapp"
                  target="_blank"
                  rel="noopener"
                  class="btn btn--whatsapp"
                >
                  Escribinos por WhatsApp
                </a>
              </div>
            </div>
            <figure v-if="restaurant.about_image" class="about__figure">
              <img
                :src="restaurant.about_image"
                alt=""
                class="about__image"
                loading="lazy"
                decoding="async"
              />
            </figure>
          </div>
        </section>

        <!-- Gallery -->
        <section v-if="site.gallery.length" id="el-patio" class="section section--night">
          <div class="container-site">
            <div class="section__head">
              <div>
                <p class="section__eyebrow section__eyebrow--gold">El patio</p>
                <h2 class="section__title section__title--light">Vení a conocernos</h2>
              </div>
              <p class="section__swipe-hint section__swipe-hint--light sm:hidden" aria-hidden="true">
                Tocá una foto para agrandar →
              </p>
            </div>

            <ul class="gallery" role="region" aria-label="Galería del patio" tabindex="0">
              <li v-for="photo in site.gallery" :key="photo.id" class="gallery__item">
                <button
                  type="button"
                  class="gallery__trigger"
                  :aria-label="`Ver foto: ${photo.caption || name}`"
                  @click="openPhotoDetail(photo)"
                >
                  <img
                    :src="photo.image"
                    :alt="photo.caption"
                    class="gallery__image"
                    loading="lazy"
                    decoding="async"
                  />
                  <span v-if="photo.caption" class="gallery__caption">{{ photo.caption }}</span>
                </button>
              </li>
            </ul>
          </div>
        </section>

        <!-- Visit -->
        <section id="visitanos" class="section section--visit">
          <div class="container-site">
            <p class="section__eyebrow section__eyebrow--azul">Visitanos</p>
            <h2 class="section__title">Te esperamos en el patio</h2>

            <div class="visit-grid">
              <article class="info-card info-card--cielo">
                <div class="info-card__head">
                  <span class="info-card__icon" aria-hidden="true">
                    <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 21s-6.5-5.3-6.5-11A6.5 6.5 0 0 1 18.5 10c0 5.7-6.5 11-6.5 11z" />
                      <circle cx="12" cy="10" r="2.2" />
                    </svg>
                  </span>
                  <h3 class="info-card__title">Dónde estamos</h3>
                </div>
                <p class="info-card__text">
                  <template v-if="restaurant.address">{{ restaurant.address }}<br /></template>
                  {{ restaurant.city }}
                </p>
                <a :href="mapsUrl" target="_blank" rel="noopener" class="btn btn--azul mt-6 w-full sm:w-auto">
                  Abrir en Google Maps
                </a>
              </article>

              <article v-if="restaurant.hours.length" class="info-card info-card--sol">
                <div class="info-card__head">
                  <span class="info-card__icon" aria-hidden="true">
                    <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="9" />
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 7v5l3 2" />
                    </svg>
                  </span>
                  <h3 class="info-card__title">Horarios</h3>
                </div>
                <dl class="hours-list">
                  <div v-for="line in restaurant.hours" :key="line.days" class="hours-list__row">
                    <dt class="hours-list__days">{{ line.days }}</dt>
                    <dd
                      class="hours-list__hours"
                      :class="{ 'hours-list__hours--closed': isClosedHours(line.hours) }"
                    >
                      {{ line.hours }}
                    </dd>
                  </div>
                </dl>
              </article>

              <article v-if="hasContact" class="info-card info-card--selva">
                <div class="info-card__head">
                  <span class="info-card__icon" aria-hidden="true">
                    <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M20 11.5a8 8 0 0 1-11.8 7l-4.2 1.1 1.2-4A8 8 0 1 1 20 11.5z" />
                    </svg>
                  </span>
                  <h3 class="info-card__title">Contacto</h3>
                </div>
                <div class="contact-list">
                  <a
                    v-if="whatsapp"
                    :href="whatsapp"
                    target="_blank"
                    rel="noopener"
                    class="btn btn--whatsapp w-full"
                  >
                    Escribir por WhatsApp
                  </a>
                  <a
                    v-if="restaurant.phone"
                    :href="telLink(restaurant.phone)"
                    class="contact-list__pill"
                  >
                    <svg class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z" />
                    </svg>
                    <span>{{ restaurant.phone }}</span>
                  </a>
                  <div v-if="restaurant.instagram_url || restaurant.facebook_url" class="contact-list__socials">
                    <a
                      v-if="restaurant.instagram_url"
                      :href="restaurant.instagram_url"
                      target="_blank"
                      rel="noopener"
                      class="contact-list__social contact-list__social--ig"
                    >
                      Instagram
                    </a>
                    <a
                      v-if="restaurant.facebook_url"
                      :href="restaurant.facebook_url"
                      target="_blank"
                      rel="noopener"
                      class="contact-list__social contact-list__social--fb"
                    >
                      Facebook
                    </a>
                  </div>
                </div>
              </article>
            </div>
          </div>
        </section>
      </template>
    </div>

    <SiteFooter
      :name="name"
      :city="restaurant?.city || 'Emboscada, Cordillera, Paraguay'"
      :credits="site?.credits ?? []"
    />

    <MobileBottomBar
      :maps-url="mapsUrl"
      :whatsapp-href="whatsapp"
      :has-gallery="(site?.gallery.length ?? 0) > 0"
    />

    <DetailDialog
      :detail="selectedDetail"
      :restaurant-name="name"
      :whatsapp-number="restaurant?.whatsapp"
      @close="selectedDetail = null"
    />
  </div>
</template>
