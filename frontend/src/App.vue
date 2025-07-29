<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// Check authentication status on app load
onMounted(async () => {
  await authStore.checkAuth()
})
</script>

<style>
/* Global styles are in main.css */
#app {
  min-height: 100vh;
}
</style>
