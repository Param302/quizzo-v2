<template>
  <div id="app">
    <Header />
    <main class="layout-content">
      <Transition name="fade" mode="out-in">
        <router-view />
      </Transition>
    </main>
    <Footer />
  </div>
</template>

<script setup>
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
</script>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.layout-content {
  flex: 1;
}
</style>
