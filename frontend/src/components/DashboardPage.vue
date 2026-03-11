<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref(null)
const dashboard = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')

const userFirstName = computed(() => user.value?.first_name || 'User')
const userRole = computed(() => {
  const role = user.value?.role || ''
  return role.charAt(0).toUpperCase() + role.slice(1)
})

onMounted(async () => {
  // Get user from localStorage
  const userData = localStorage.getItem('user')
  const token = localStorage.getItem('token')

  if (!userData || !token) {
    router.push('/login')
    return
  }

  user.value = JSON.parse(userData)

  try {
    // Fetch dashboard data based on user role
    const endpoint = user.value.role === 'admin'
      ? '/api/admin/dashboard'
      : user.value.role === 'doctor'
        ? '/api/doctor/dashboard'
        : '/api/patient/dashboard'

    const response = await fetch(`http://localhost:5000${endpoint}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (response.ok) {
      dashboard.value = data
    } else {
      errorMessage.value = data.message || 'Failed to load dashboard'
    }
  } catch (error) {
    errorMessage.value = 'An error occurred while loading dashboard'
    console.error('Dashboard error:', error)
  } finally {
    isLoading.value = false
  }
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/')
}
</script>

<template>
  <div class="container mt-5" v-if="user">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-md-8">
        <h1>Welcome, {{ userFirstName }}!</h1>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="alert alert-info">
      <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
      Loading dashboard...
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="alert alert-danger">
      {{ errorMessage }}
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="dashboard" class="row">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">{{ userRole }} Dashboard</h5>
          </div>
          <div class="card-body">
            <p>Dashboard content for <strong>{{ user.role }}</strong> role</p>
            <!-- Render different content based on role -->
            <div class="alert alert-info">
              <p>Dashboard data loaded successfully!</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="alert alert-warning">
      No dashboard data available
    </div>
  </div>

  <!-- Not Logged In -->
  <div v-else class="container mt-5">
    <div class="alert alert-warning">
      <p>Please <RouterLink to="/login">login</RouterLink> to view dashboard</p>
    </div>
  </div>
</template>

<script>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.text-muted {
  color: #6c757d;
}

.card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.btn-outline-danger:hover {
  background-color: #dc3545;
  color: white;
}
</style>