<script setup lang="ts">
import type { MenuItem } from '@/types/site'
import { formatGs } from '@/utils/format'

defineProps<{ item: MenuItem }>()
</script>

<template>
  <article class="feature-card">
    <img
      v-if="item.photo"
      :src="item.photo"
      :alt="item.name"
      class="feature-card__media"
      loading="lazy"
      decoding="async"
    />
    <div v-else class="feature-card__placeholder" aria-hidden="true">
      <!-- a five-pointed star, as on the flag's seal -->
      <svg class="h-12 w-12" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6-4.9-4.6 6.6-.8z" />
      </svg>
    </div>
    <div class="feature-card__body">
      <h3 class="feature-card__title">{{ item.name }}</h3>
      <p v-if="item.description" class="feature-card__description">{{ item.description }}</p>
      <p class="feature-card__price">{{ formatGs(item.price) }}</p>
    </div>
  </article>
</template>
