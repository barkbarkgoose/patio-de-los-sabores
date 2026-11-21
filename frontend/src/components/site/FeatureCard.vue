<script setup lang="ts">
import type { MenuItem } from '@/types/site'
import { formatGs } from '@/utils/format'

interface Props {
  item: MenuItem
}

interface Emits {
  (e: 'select', item: MenuItem): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
</script>

<template>
  <article class="feature-card">
    <button
      type="button"
      class="feature-card__trigger"
      :aria-label="`Ver detalle de ${props.item.name}, ${formatGs(props.item.price)}`"
      @click="emit('select', props.item)"
    >
      <div class="feature-card__media-wrap">
        <img
          v-if="props.item.photo"
          :src="props.item.photo"
          :alt="props.item.name"
          class="feature-card__media"
          decoding="async"
        />
        <div v-else class="feature-card__placeholder" aria-hidden="true">
          <svg class="h-12 w-12" viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6-4.9-4.6 6.6-.8z"
            />
          </svg>
        </div>
        <span class="feature-card__ribbon">
          <span aria-hidden="true">★</span>
          <span>Favorito</span>
        </span>
      </div>

      <div class="feature-card__body">
        <h3 class="feature-card__title">{{ props.item.name }}</h3>
        <p v-if="props.item.description" class="feature-card__description">
          {{ props.item.description }}
        </p>
        <div class="feature-card__footer">
          <span class="feature-card__price">{{ formatGs(props.item.price) }}</span>
          <span class="feature-card__hint" aria-hidden="true">Ver plato →</span>
        </div>
      </div>
    </button>
  </article>
</template>
