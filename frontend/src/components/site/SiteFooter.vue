<script setup lang="ts">
import type { PhotoCredit } from '@/types/site'

defineProps<{ name: string; city: string; credits: PhotoCredit[] }>()

const year = new Date().getFullYear()
</script>

<template>
  <footer class="site-footer">
    <div class="tricolor" />
    <div class="container-site site-footer__inner">
      <div>
        <p class="site-footer__brand">{{ name }}</p>
        <p class="mt-1">{{ city }}</p>
      </div>
      <div class="flex flex-col gap-1 sm:items-end">
        <p>© {{ year }} {{ name }}</p>
        <router-link :to="{ name: 'login' }" class="site-footer__staff">Acceso del personal</router-link>
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
