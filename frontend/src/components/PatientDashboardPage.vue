<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref(null)
const dashboard = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')

const userFirstName = computed(() => user.value?.first_name || 'Patient')

onMounted(async () => {
  // Get user from localStorage
  const userData = localStorage.getItem('user')
  const token = localStorage.getItem('token')

  if (!userData || !token) {
    router.push('/login')
    return
  }

  user.value = JSON.parse(userData)

  // Verify user is a patient
  if (user.value.role !== 'patient') {
    router.push('/dashboard')
    return
  }

  try {
    // Fetch patient dashboard data
    const response = await fetch('http://localhost:5000/api/patient/dashboard', {
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
      errorMessage.value = data.message || 'Failed to load patient dashboard'
    }
  } catch (error) {
    errorMessage.value = 'An error occurred while loading dashboard'
    console.error('Dashboard error:', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="container mt-5" v-if="user">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-md-8">
        <h2>Welcome, {{ userFirstName }}!</h2>
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
      <!-- Quick Stats -->
      <div class="col-md-3 mb-4">
        <div class="card">
          <div class="card-body text-center">
            <h3 class="text-primary">--</h3>
            <p class="text-muted small">Upcoming Appointments</p>
          </div>
        </div>
      </div>

      <div class="col-md-3 mb-4">
        <div class="card">
          <div class="card-body text-center">
            <h3 class="text-success">--</h3>
            <p class="text-muted small">Completed Treatments</p>
          </div>
        </div>
      </div>

      <div class="col-md-3 mb-4">
        <div class="card">
          <div class="card-body text-center">
            <h3 class="text-info">--</h3>
            <p class="text-muted small">Active Prescriptions</p>
          </div>
        </div>
      </div>

      <div class="col-md-3 mb-4">
        <div class="card">
          <div class="card-body text-center">
            <h3 class="text-warning">--</h3>
            <p class="text-muted small">My Doctors</p>
          </div>
        </div>
      </div>

      <!-- Upcoming Appointments -->
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Upcoming Appointments</h5>
          </div>
          <div class="card-body">
            <table class="table">
              <thead class="fw-normal">
                <tr>
                  <th scope="col">Sr No.</th>
                  <th scope="col">Patient Name</th>
                  <th scope="col">Patient History</th>
                  <th scope="col">Date</th>
                  <th scope="col">Time</th>
                  <th scope="col">Status</th>
                  <th scope="col">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="appointment in dashboard.upcoming_appointments" :key="appointment.id">
                  <td>{{ appointment.id }}</td>
                  <td>{{ appointment.patient.name }}</td>
                  <td>{{ appointment.patient.username }}</td>
                  <td><button class="btn btn-primary">Update History</button></td>
                  <td>{{ new Date(appointment.date).toLocaleDateString() }}</td>
                  <td>{{ new Date(appointment.time).toLocaleTimeString() }}</td>
                  <td>{{ appointment.status }}</td>
                  <td>
                    <button class="btn btn-primary">View</button>
                    <button class="btn btn-secondary">Edit</button>
                    <button class="btn btn-danger">Cancel</button>
                  </td>
                </tr>
                <tr v-if="!dashboard.upcoming_appointments || dashboard.upcoming_appointments.length === 0">
                  <td colspan="7" class="text-center text-muted">No upcoming appointments</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <br>
        <!-- Assigned Patients -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Assigned Patients</h5>
          </div>
          <div class="card-body">
            <table class="table">
              <thead class="fw-normal">
                <tr>
                  <th scope="col">Patient</th>
                  <th scope="col">Total Appointments</th>
                  <th scope="col">Last Visit</th>
                  <th scope="col">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="patient in dashboard.patient_history" :key="patient.patient_id">
                  <td>{{ patient.name }}</td>
                  <td>{{ patient.total_appointments }}</td>
                  <td>{{ new Date(patient.last_visit).toLocaleDateString() }}</td>
                  <td><button class="btn btn-primary">View</button></td>
                </tr>
                <tr v-if="!dashboard.patient_history || dashboard.patient_history.length === 0">
                  <td colspan="4" class="text-center text-muted">No assigned patients</td>
                </tr>
              </tbody>
            </table>
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

.table thead th {
  font-weight: normal;
}

.btn-outline-danger:hover {
  background-color: #dc3545;
  color: white;
}
</style>