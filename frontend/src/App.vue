<script setup lang="ts">
import Navbar from '@/components/Navbar.vue'
import PasskeyPrompt from '@/components/PasskeyPrompt.vue'
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <Navbar v-if="!route.meta.site" />
    <main>
      <router-view />
    </main>
    <PasskeyPrompt />
  </div>
</template>
