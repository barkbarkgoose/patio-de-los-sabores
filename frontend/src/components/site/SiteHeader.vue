<script setup lang="ts">
defineProps<{ name: string }>()
</script>

<template>
  <header class="site-header">
    <div class="tricolor" />
    <div class="container-site site-header__bar">
      <a href="#inicio" class="site-header__brand">{{ name }}</a>
      <nav class="site-header__links" aria-label="Secciones">
        <a href="#menu" class="site-header__link">Menú</a>
        <a href="#visitanos" class="site-header__link">Visitanos</a>
      </nav>
    </div>
  </header>
</template>
