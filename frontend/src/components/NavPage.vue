<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

const router = useRouter()
const isNavOpen = ref(false)
const user = ref(null)

const isLoggedIn = computed(() => !!user.value)

const toggleNav = () => {
  isNavOpen.value = !isNavOpen.value
}

const closeNav = () => {
  isNavOpen.value = false
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  user.value = null
  closeNav()
  router.push('/')
}

onMounted(() => {
  // Check if user is logged in
  const userData = localStorage.getItem('user')
  if (userData) {
    user.value = JSON.parse(userData)
  }
})
</script>

<template>
  <nav class="navbar navbar-expand-md bg-body-tertiary sticky-top">
    <div class="container-fluid">
      <RouterLink class="navbar-brand" to="/">Hospital Management System</RouterLink>
      <button class="navbar-toggler" type="button" @click="toggleNav" :aria-expanded="isNavOpen"
        aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" :class="{ show: isNavOpen }" id="navbarSupportedContent">
        <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <RouterLink class="nav-link" to="/" @click="closeNav">Home</RouterLink>
          </li>

          <!-- When NOT logged in -->
          <template v-if="!isLoggedIn">
            <li class="nav-item">
              <RouterLink class="nav-link" to="/register" @click="closeNav">Register</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/login" @click="closeNav">Login</RouterLink>
            </li>
          </template>

          <!-- When logged in -->
          <template v-else>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/dashboard" @click="closeNav">
                Dashboard
              </RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/profile" @click="closeNav">
                Edit Profile
              </RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/history" @click="closeNav">
                History
              </RouterLink>
            </li>
            <li class="nav-item">
              <button class="nav-link" @click="handleLogout">
                Logout
              </button>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar-brand {
  font-size: 1.5rem;
  font-weight: semibold;
}

.nav-link:hover {
  color: #0d6efd !important;
}

.nav-link.router-link-active {
  color: #0d6efd !important;
  font-weight: 500;
}

.btn {
  padding: 0.4rem 0.8rem;
  font-size: 0.9rem;
  font-weight: 500;
}

.btn-primary {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.btn-primary:hover {
  background-color: #0b5ed7;
  border-color: #0a58ca;
}

.btn-danger {
  background-color: #dc3545;
  border-color: #dc3545;
}

.btn-danger:hover {
  background-color: #bb2d3b;
  border-color: #b02a37;
}

.nav-link.btn {
  border: none;
  background: none;
  padding: 0.5rem 1rem;
  cursor: pointer;
  text-decoration: none;
  color: inherit;
}
</style>