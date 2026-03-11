<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref(null)
const history = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')
const token = ref(null)

onMounted(async () => {
  const userData = localStorage.getItem('user')
  const tokenData = localStorage.getItem('token')

  if (!userData || !tokenData) {
    router.push('/login')
    return
  }

  user.value = JSON.parse(userData)
  token.value = tokenData

  try {
    const response = await fetch('http://localhost:5000/api/appointments/history', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`)
    }

    const data = await response.json()
    history.value = data
  } catch (error) {
    errorMessage.value = 'Appointment history endpoint not yet configured. Please check with your administrator.'
    console.error('Error:', error)
  } finally {
    isLoading.value = false
  }
})

const getStatusBadgeClass = (status) => {
  switch (status) {
    case 'Completed':
      return 'bg-success'
    case 'Pending':
      return 'bg-warning'
    case 'Cancelled':
      return 'bg-danger'
    default:
      return 'bg-secondary'
  }
}
</script>

<template>
  <div class="container mt-5" v-if="user">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-md-8">
        <h2>Patient History</h2>
      </div>
      <div class="col-md-4 text-end">
        <button class="btn btn-outline-primary btn-md me-2">Export as CSV</button>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show">
      {{ errorMessage }}
      <button type="button" class="btn-close" @click="errorMessage = ''"></button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="alert alert-info">
      <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
      Loading appointment history...
    </div>

    <!-- History Table -->
    <div v-else class="card">
      <div class="card-header">
        <h5 class="mb-0">Visit History</h5>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table">
            <thead class="fw-normal">
              <tr>
                <th scope="col">Visit No.</th>
                <th scope="col">Visit Type</th>
                <th scope="col">Tests Done</th>
                <th scope="col">Diagnosis</th>
                <th scope="col">Prescription</th>
                <th scope="col">Medicines</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(visit, index) in history?.visits || []" :key="index">
                <td>{{ index + 1 }}</td>
                <td>{{ visit.visit_type || 'In-person' }}</td>
                <td>{{ visit.tests_done || '-' }}</td>
                <td>{{ visit.diagnosis || '-' }}</td>
                <td>{{ visit.prescription || '-' }}</td>
                <td>{{ visit.medicines || '-' }}</td>
              </tr>
              <tr v-if="!history?.visits || history.visits.length === 0">
                <td colspan="6" class="text-center text-muted py-4">
                  No visit history available
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- Not Logged In -->
  <div v-else class="container mt-5">
    <div class="alert alert-warning">
      <p>Please login to view this page</p>
    </div>
  </div>
</template>

<style scoped>
h2 {
  color: #333;
}

.card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-2px);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.card-body h3 {
  font-size: 2rem;
  margin: 0;
}

.table {
  margin-bottom: 0;
}

.table thead th {
  border-top: none;
  background-color: #f8f9fa;
  font-weight: 600;
}

.badge {
  padding: 0.4rem 0.8rem;
  font-size: 0.875rem;
  text-transform: capitalize;
}

.btn-outline-primary:hover {
  background-color: #0d6efd;
  color: white;
}
</style>
