<script setup>
import { ref, onMounted } from 'vue'

const adminData = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')
const token = ref(null)

onMounted(async () => {
  token.value = localStorage.getItem('token')
  const user = localStorage.getItem('user')

  if (!token.value || !user) {
    window.location.href = '/login'
    return
  }

  const userData = JSON.parse(user)
  if (userData.role !== 'admin') {
    window.location.href = '/dashboard'
    return
  }

  try {
    const response = await fetch('http://localhost:5000/api/admin/dashboard', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (response.ok) {
      adminData.value = data
    } else {
      errorMessage.value = data.message || 'Failed to load admin data'
    }
  } catch (error) {
    errorMessage.value = 'An error occurred while loading admin data'
    console.error('Admin error:', error)
  } finally {
    isLoading.value = false
  }
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  window.location.href = '/'
}
</script>

<template>
  <div class="container mt-5">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-md-8">
        <h1>Admin Dashboard</h1>
        <p class="text-muted">System Administration & Management</p>
      </div>
      <div class="col-md-4 text-end">
        <button class="btn btn-danger" @click="handleLogout">Logout</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="alert alert-info">
      <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
      Loading admin dashboard...
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="alert alert-danger">
      {{ errorMessage }}
    </div>

    <!-- Admin Dashboard Content -->
    <div v-else-if="adminData" class="row">
      <div class="col-md-12">
        <!-- Stats Cards -->
        <div class="row mb-4" v-if="adminData.stats">
          <div class="col-md-3">
            <div class="card">
              <div class="card-body text-center">
                <h3>{{ adminData.stats.total_users }}</h3>
                <p class="text-muted">Total Users</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card">
              <div class="card-body text-center">
                <h3>{{ adminData.stats.total_doctors }}</h3>
                <p class="text-muted">Doctors</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card">
              <div class="card-body text-center">
                <h3>{{ adminData.stats.total_patients }}</h3>
                <p class="text-muted">Patients</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card">
              <div class="card-body text-center">
                <h3>{{ adminData.stats.total_appointments }}</h3>
                <p class="text-muted">Appointments</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Management Sections -->
        <div class="card">
          <div class="card-header">
            <h5>Admin Tools</h5>
          </div>
          <div class="card-body">
            <p>Admin management tools and reports will be displayed here</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="alert alert-warning">
      No admin data available
    </div>
  </div>
</template>

<style scoped>
h1 {
  color: #333;
  font-weight: bold;
}

.text-muted {
  color: #6c757d;
}

.card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-body h3 {
  font-size: 2rem;
  color: #0d6efd;
  margin-bottom: 0.5rem;
}
</style>