<script setup>
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="bg-secondary text-white text-center py-4 mt-5">
    <div class="container-fluid">
      <p class="mb-2">&copy; {{ currentYear }} Hospital Management System. All rights reserved.</p>
      <p class="text-white-50 mb-0">
        <small>Developed by Sukhsimar Singh</small>
      </p>
    </div>
  </footer>
</template>

<style scoped>
</style>
