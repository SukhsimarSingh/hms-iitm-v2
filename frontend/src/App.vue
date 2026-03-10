<script setup>
import LoginPage from './components/LoginPage.vue'
import NavPage from './components/NavPage.vue'
import FooterPage from './components/FootPage.vue'
</script>

<template>
  <NavPage />
  <LoginPage />
  <FooterPage />
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}

.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}

.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
