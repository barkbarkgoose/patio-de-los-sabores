<script setup lang="ts">
interface Props {
  mapsUrl: string
  whatsappHref?: string | null
  hasGallery?: boolean
}

withDefaults(defineProps<Props>(), {
  whatsappHref: null,
  hasGallery: false,
})
</script>

<template>
  <nav class="mobile-dock" aria-label="Accesos rápidos">
    <div class="tricolor mobile-dock__stripe" aria-hidden="true" />
    <div class="mobile-dock__grid">
      <a href="#menu" class="mobile-dock__item mobile-dock__item--menu">
        <svg class="mobile-dock__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h10" />
        </svg>
        <span>Menú</span>
      </a>

      <a :href="hasGallery ? '#el-patio' : '#nosotros'" class="mobile-dock__item">
        <svg class="mobile-dock__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 3l2.4 5 5.6.7-4.1 3.9 1 5.6-4.9-2.7-4.9 2.7 1-5.6L4 8.7l5.6-.7L12 3z"
          />
        </svg>
        <span>{{ hasGallery ? 'El patio' : 'Nosotros' }}</span>
      </a>

      <a :href="mapsUrl" target="_blank" rel="noopener" class="mobile-dock__item">
        <svg class="mobile-dock__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 21s-6.5-5.3-6.5-11A6.5 6.5 0 0 1 18.5 10c0 5.7-6.5 11-6.5 11z"
          />
          <circle cx="12" cy="10" r="2.2" />
        </svg>
        <span>Llegar</span>
      </a>

      <a
        v-if="whatsappHref"
        :href="whatsappHref"
        target="_blank"
        rel="noopener"
        class="mobile-dock__item mobile-dock__item--whatsapp"
      >
        <svg class="mobile-dock__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M20 11.5a8 8 0 0 1-11.8 7l-4.2 1.1 1.2-4A8 8 0 1 1 20 11.5z"
          />
        </svg>
        <span>WhatsApp</span>
      </a>
      <a v-else href="#visitanos" class="mobile-dock__item mobile-dock__item--visit">
        <svg class="mobile-dock__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <circle cx="12" cy="12" r="8.5" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 7.5v4.8l3 1.7" />
        </svg>
        <span>Horarios</span>
      </a>
    </div>
  </nav>
</template>
