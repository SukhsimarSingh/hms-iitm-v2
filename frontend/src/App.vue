<script setup>
import NavPage from './components/NavPage.vue'
import FootPage from './components/FootPage.vue'
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="d-flex flex-column" style="min-height: 100vh;">
    <NavPage />
    <main class="flex-grow-1">
      <RouterView />
    </main>
    <FootPage />
  </div>
</template>

<style scoped>
main {
  flex: 1;
}
</style>