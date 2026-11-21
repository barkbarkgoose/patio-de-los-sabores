<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import FeatureCard from '@/components/site/FeatureCard.vue'
import MenuItemCard from '@/components/site/MenuItemCard.vue'
import SiteFooter from '@/components/site/SiteFooter.vue'
import SiteHeader from '@/components/site/SiteHeader.vue'
import { fetchSiteContent } from '@/services/site'
import type { SiteContent } from '@/types/site'
import { telLink, whatsappLink } from '@/utils/format'

// The restaurant's public website. Everything shown comes from GET /api/v1/site/,
// which staff edit in the Django admin.
const site = ref<SiteContent | null>(null)
const loading = ref(true)
const failed = ref(false)
const activeCategory = ref('')

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
      [restaurant.value?.address, restaurant.value?.city].filter(Boolean).join(', ') || 'Emboscada, Paraguay'
    )}`
)
const hasContact = computed(() => {
  const r = restaurant.value
  return !!(r && (r.phone || r.whatsapp || r.instagram_url || r.facebook_url))
})

let observer: IntersectionObserver | null = null

// On phones the category bar scrolls sideways: keep the active one in view.
watch(activeCategory, async (slug) => {
  await nextTick()
  document
    .querySelector(`.menu-nav a[href="#menu-${slug}"]`)
    ?.scrollIntoView({ block: 'nearest', inline: 'center' })
})

// Highlight the category the visitor is reading in the sticky category bar.
function watchCategories() {
  observer?.disconnect()
  observer = new IntersectionObserver(
    (entries) => {
      const visible = entries.filter((e) => e.isIntersecting)
      if (visible.length) activeCategory.value = visible[0].target.id.replace(/^menu-/, '')
    },
    { rootMargin: '-140px 0px -60% 0px' }
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
  // The menu renders once loading is off; observe its sections after that.
  await nextTick()
  watchCategories()
}

onMounted(load)
onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <div class="site">
    <SiteHeader :name="name" />

    <!-- Hero -->
    <section id="inicio" class="hero" :class="{ 'hero--photo': restaurant?.hero_image }">
      <template v-if="restaurant?.hero_image">
        <img :src="restaurant.hero_image" alt="" class="hero__backdrop" fetchpriority="high" />
        <div class="hero__shade" />
      </template>
      <div v-else class="hero__glow" />
      <div class="container-site hero__inner">
        <p class="hero__eyebrow">
          <span aria-hidden="true">★</span> Emboscada · Cordillera · Paraguay
        </p>
        <h1 class="hero__title">{{ name }}</h1>
        <p v-if="restaurant?.tagline" class="hero__tagline">{{ restaurant.tagline }}</p>
        <div class="hero__actions">
          <a href="#menu" class="btn btn--primary">Ver el menú</a>
          <a :href="mapsUrl" target="_blank" rel="noopener" class="btn btn--ghost">Cómo llegar</a>
          <a v-if="whatsapp" :href="whatsapp" target="_blank" rel="noopener" class="btn btn--whatsapp">
            WhatsApp
          </a>
        </div>
      </div>
    </section>
    <div class="tricolor" />

    <div>
      <!-- Loading / error -->
      <div v-if="loading" class="container-site section" aria-busy="true" aria-label="Cargando">
        <div class="skeleton h-8 w-64" />
        <div class="featured-grid">
          <div v-for="n in 4" :key="n" class="skeleton h-72" />
        </div>
      </div>
      <div v-else-if="failed" class="container-site section">
        <div class="alert alert--error" role="alert">
          <p class="alert__title">No pudimos cargar el menú.</p>
          <p class="alert__text">Revisá tu conexión e intentá de nuevo.</p>
          <button type="button" class="btn btn--primary mt-4" @click="load">Reintentar</button>
        </div>
      </div>

      <template v-else-if="site && restaurant">
        <!-- Featured -->
        <section v-if="site.featured.length" class="section">
          <div class="container-site">
            <p class="section__eyebrow">Los favoritos de la casa</p>
            <h2 class="section__title">Lo que todos piden</h2>
            <div class="featured-grid">
              <FeatureCard v-for="item in site.featured" :key="item.id" :item="item" />
            </div>
          </div>
        </section>

        <!-- About -->
        <section v-if="aboutParagraphs.length" id="nosotros" class="section section--stone">
          <div class="container-site about" :class="{ 'about--photo': restaurant.about_image }">
            <div>
              <p class="section__eyebrow">Nuestro patio</p>
              <h2 class="section__title">Sabores de la Capital de la Piedra</h2>
              <p v-for="(paragraph, i) in aboutParagraphs" :key="i" class="section__body">
                {{ paragraph }}
              </p>
              <a href="#menu" class="btn btn--primary mt-8">Ver el menú</a>
            </div>
            <figure v-if="restaurant.about_image" class="about__figure">
              <img :src="restaurant.about_image" alt="" class="about__image" loading="lazy" decoding="async" />
            </figure>
          </div>
        </section>

        <!-- Menu -->
        <section id="menu" class="section">
          <div class="container-site">
            <p class="section__eyebrow">Carta</p>
            <h2 class="section__title">Nuestro menú</h2>

            <p v-if="!site.categories.length" class="section__body">
              Estamos preparando el menú. ¡Volvé pronto!
            </p>

            <nav v-else class="menu-nav" aria-label="Categorías del menú">
              <ul class="menu-nav__list">
                <li v-for="category in site.categories" :key="category.id">
                  <a
                    :href="`#menu-${category.slug}`"
                    class="menu-nav__link"
                    :class="{ 'menu-nav__link--active': activeCategory === category.slug }"
                  >
                    {{ category.name }}
                  </a>
                </li>
              </ul>
            </nav>

            <section
              v-for="category in site.categories"
              :id="`menu-${category.slug}`"
              :key="category.id"
              class="menu-category"
            >
              <div class="menu-category__header">
                <h3 class="menu-category__title">{{ category.name }}</h3>
                <p v-if="category.description" class="menu-category__description">
                  {{ category.description }}
                </p>
              </div>
              <ul class="menu-list">
                <MenuItemCard v-for="item in category.items" :key="item.id" :item="item" />
              </ul>
            </section>

            <p v-if="restaurant.menu_note" class="menu-note">{{ restaurant.menu_note }}</p>
          </div>
        </section>

        <!-- Gallery -->
        <section v-if="site.gallery.length" id="el-patio" class="section section--night">
          <div class="container-site">
            <p class="section__eyebrow section__eyebrow--gold">El patio</p>
            <h2 class="section__title section__title--light">Vení a conocernos</h2>
            <ul class="gallery">
              <li v-for="photo in site.gallery" :key="photo.id" class="gallery__item">
                <img :src="photo.image" :alt="photo.caption" class="gallery__image" loading="lazy" decoding="async" />
                <span v-if="photo.caption" class="gallery__caption">{{ photo.caption }}</span>
              </li>
            </ul>
          </div>
        </section>

        <!-- Visit -->
        <section id="visitanos" class="section section--stone">
          <div class="container-site">
            <p class="section__eyebrow">Visitanos</p>
            <h2 class="section__title">Te esperamos en el patio</h2>
            <div class="visit-grid">
              <div class="info-card">
                <h3 class="info-card__title">Dónde estamos</h3>
                <p class="info-card__text">
                  <template v-if="restaurant.address">{{ restaurant.address }}<br /></template>
                  {{ restaurant.city }}
                </p>
                <a :href="mapsUrl" target="_blank" rel="noopener" class="btn btn--outline mt-5">
                  Abrir en Google Maps
                </a>
              </div>

              <div v-if="restaurant.hours.length" class="info-card">
                <h3 class="info-card__title">Horarios</h3>
                <dl class="hours-list">
                  <div v-for="line in restaurant.hours" :key="line.days" class="hours-list__row">
                    <dt class="hours-list__days">{{ line.days }}</dt>
                    <dd class="hours-list__hours">{{ line.hours }}</dd>
                  </div>
                </dl>
              </div>

              <div v-if="hasContact" class="info-card">
                <h3 class="info-card__title">Contacto</h3>
                <div class="contact-list">
                  <a v-if="whatsapp" :href="whatsapp" target="_blank" rel="noopener" class="contact-list__link">
                    WhatsApp
                  </a>
                  <a v-if="restaurant.phone" :href="telLink(restaurant.phone)" class="contact-list__link">
                    {{ restaurant.phone }}
                  </a>
                  <a
                    v-if="restaurant.instagram_url"
                    :href="restaurant.instagram_url"
                    target="_blank"
                    rel="noopener"
                    class="contact-list__link"
                  >
                    Instagram
                  </a>
                  <a
                    v-if="restaurant.facebook_url"
                    :href="restaurant.facebook_url"
                    target="_blank"
                    rel="noopener"
                    class="contact-list__link"
                  >
                    Facebook
                  </a>
                </div>
              </div>
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
  </div>
</template>
