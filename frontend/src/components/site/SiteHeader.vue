<script setup lang="ts">
interface Props {
  name: string
  hasGallery?: boolean
  hasAbout?: boolean
  whatsappHref?: string | null
}

withDefaults(defineProps<Props>(), {
  hasGallery: false,
  hasAbout: false,
  whatsappHref: null,
})
</script>

<template>
  <header class="site-header">
    <div class="tricolor" aria-hidden="true" />
    <div class="container-site site-header__bar">
      <a href="#inicio" class="site-header__brand">
        <span class="site-header__emblem" aria-hidden="true">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6-4.9-4.6 6.6-.8z"
            />
          </svg>
        </span>
        <span class="site-header__brand-name">{{ name }}</span>
      </a>

      <nav class="site-header__links" aria-label="Secciones">
        <a href="#menu" class="site-header__link site-header__link--menu">Menú</a>
        <a v-if="hasAbout" href="#nosotros" class="site-header__link hidden md:inline-flex">
          Nosotros
        </a>
        <a v-if="hasGallery" href="#el-patio" class="site-header__link hidden md:inline-flex">
          El patio
        </a>
        <a href="#visitanos" class="site-header__link hidden sm:inline-flex">Visitanos</a>
        <a
          v-if="whatsappHref"
          :href="whatsappHref"
          target="_blank"
          rel="noopener"
          class="site-header__cta hidden sm:inline-flex"
        >
          WhatsApp
        </a>
      </nav>
    </div>
  </header>
</template>
