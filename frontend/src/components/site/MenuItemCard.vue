<script setup lang="ts">
import type { MenuItem } from '@/types/site'
import { formatGs } from '@/utils/format'
import type { CategoryAccent } from '@/utils/menuTheme'

interface Props {
  item: MenuItem
  accent: CategoryAccent
}

interface Emits {
  (e: 'select', item: MenuItem): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
</script>

<template>
  <li
    class="menu-card-shell"
    :class="{ 'menu-card-shell--unavailable': !props.item.is_available }"
    :data-accent="props.accent"
  >
    <button
      type="button"
      class="menu-card"
      :aria-label="`Ver ${props.item.name}, ${formatGs(props.item.price)}${props.item.is_available ? '' : ', agotado'}`"
      @click="emit('select', props.item)"
    >
      <div class="menu-card__thumb">
        <img
          v-if="props.item.photo"
          :src="props.item.photo"
          :alt="props.item.name"
          class="menu-card__photo"
          loading="lazy"
          decoding="async"
          width="112"
          height="112"
        />
        <div v-else class="menu-card__monogram" aria-hidden="true">
          <svg class="h-6 w-6" viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6-4.9-4.6 6.6-.8z"
            />
          </svg>
        </div>
      </div>

      <div class="menu-card__body">
        <div class="menu-card__top">
          <h4 class="menu-card__title">{{ props.item.name }}</h4>
          <span class="menu-card__price">{{ formatGs(props.item.price) }}</span>
        </div>

        <p v-if="props.item.description" class="menu-card__description">
          {{ props.item.description }}
        </p>

        <div v-if="!props.item.is_available || props.item.is_featured" class="menu-card__meta">
          <span v-if="!props.item.is_available" class="badge badge--unavailable">
            <span aria-hidden="true">✕</span>
            <span>Agotado</span>
          </span>
          <span v-else-if="props.item.is_featured" class="badge badge--featured">
            <span aria-hidden="true">★</span>
            <span>Favorito</span>
          </span>
        </div>
      </div>
    </button>
  </li>
</template>
