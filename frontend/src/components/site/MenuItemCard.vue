<script setup lang="ts">
import type { MenuItem } from '@/types/site'
import { formatGs } from '@/utils/format'

defineProps<{ item: MenuItem }>()
</script>

<template>
  <li class="menu-card" :class="{ 'menu-card--unavailable': !item.is_available }">
    <img
      v-if="item.photo"
      :src="item.photo"
      :alt="item.name"
      class="menu-card__photo"
      loading="lazy"
      decoding="async"
      width="96"
      height="96"
    />
    <div class="menu-card__body">
      <div class="menu-card__header">
        <h4 class="menu-card__title">
          {{ item.name }}
          <span v-if="!item.is_available" class="badge badge--unavailable">Agotado</span>
          <span v-else-if="item.is_featured" class="badge badge--featured">Favorito</span>
        </h4>
        <span class="menu-card__leader" aria-hidden="true" />
        <span class="menu-card__price">{{ formatGs(item.price) }}</span>
      </div>
      <p v-if="item.description" class="menu-card__description">{{ item.description }}</p>
    </div>
  </li>
</template>
