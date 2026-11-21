<script setup lang="ts">
import type { PhotoCredit } from '@/types/site'

interface Props {
  name: string
  city: string
  credits: PhotoCredit[]
}

defineProps<Props>()

const year = new Date().getFullYear()
</script>

<template>
  <footer class="site-footer">
    <div class="tricolor" aria-hidden="true" />
    <div class="container-site site-footer__inner">
      <div class="site-footer__identity">
        <span class="site-footer__star" aria-hidden="true">★</span>
        <div>
          <p class="site-footer__brand">{{ name }}</p>
          <p class="mt-0.5 text-white/80">{{ city }}</p>
        </div>
      </div>

      <div class="flex flex-col gap-1.5 sm:items-end">
        <p class="text-white/80">© {{ year }} {{ name }}</p>
        <router-link :to="{ name: 'login' }" class="site-footer__staff">
          Acceso del personal
        </router-link>
      </div>
    </div>

    <!-- Attribution the photos' licenses require; empty once the restaurant uses its own. -->
    <details v-if="credits.length" class="container-site site-footer__credits">
      <summary class="site-footer__credits-toggle">Créditos de las fotos</summary>
      <ul class="site-footer__credits-list">
        <li v-for="credit in credits" :key="credit.subject + credit.credit">
          {{ credit.subject }}:
          <a v-if="credit.url" :href="credit.url" target="_blank" rel="noopener" class="underline">
            {{ credit.credit }}
          </a>
          <template v-else>{{ credit.credit }}</template>
        </li>
      </ul>
    </details>
  </footer>
</template>
