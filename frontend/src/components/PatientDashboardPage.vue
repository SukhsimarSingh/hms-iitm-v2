<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref(null)
const token = ref(null)
const dashboard = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')
const selectedDepartment = ref(null)

const userFirstName = computed(() => user.value?.first_name || 'Patient')

onMounted(async () => {
  // Get user from localStorage
  const userData = localStorage.getItem('user')
  const tokenData = localStorage.getItem('token')

  if (!userData || !tokenData) {
    router.push('/login')
    return
  }

  user.value = JSON.parse(userData)
  token.value = tokenData

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
        'Authorization': `Bearer ${token.value}`,
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

const viewDepartment = (department) => {
  selectedDepartment.value = department
}

const closeDepartmentView = () => {
  selectedDepartment.value = null
}

const cancelAppointment = async (appointment) => {
  if (!confirm(`Are you sure you want to cancel this appointment on ${new Date(appointment.date).toLocaleDateString()}?`)) {
    return
  }

  try {
    const response = await fetch(`http://localhost:5000/api/appointment/cancel/${appointment.id}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (response.ok) {
      // Remove the cancelled appointment from the list
      dashboard.value.upcoming_appointments = dashboard.value.upcoming_appointments.filter(apt => apt.id !== appointment.id)
      alert('Appointment cancelled successfully')
    } else {
      alert(data.message || 'Failed to cancel appointment')
    }
  } catch (error) {
    console.error('Error cancelling appointment:', error)
    alert('An error occurred while cancelling the appointment')
  }
}
</script>

<template>
  <!-- Main Dashboard View -->
  <div v-if="!selectedDepartment && user" class="container mt-5">
    <!-- Header with Profile Info -->
    <div class="row mb-4">
      <div class="col-md-12">
        <h2>Welcome {{ userFirstName }}</h2>
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
    <div v-else-if="dashboard">
      <!-- Departments Section -->
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">Departments</h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div v-for="department in dashboard.departments" :key="department.id" class="col-md-6 mb-3">
              <div class="d-flex justify-content-between align-items-center p-3 border rounded">
                <span>{{ department.name }}</span>
                <button class="btn btn-outline-primary btn-sm" @click="viewDepartment(department)">view details</button>
              </div>
            </div>
            <div v-if="!dashboard.departments || dashboard.departments.length === 0" class="col-md-12">
              <p class="text-center text-muted">No departments available</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming Appointments Section -->
      <div class="card">
        <div class="card-header">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Upcoming Appointments</h5>
            <RouterLink to="/book-appointment" class="btn btn-primary btn-sm">
              + Book Appointment
            </RouterLink>
          </div>
        </div>
        <div class="card-body">
          <table class="table">
            <thead class="fw-normal">
              <tr>
                <th scope="col">Sr No.</th>
                <th scope="col">Doctor Name</th>
                <th scope="col">Department</th>
                <th scope="col">Date</th>
                <th scope="col">Time</th>
                <th scope="col">Status</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="appointment in dashboard.upcoming_appointments" :key="appointment.id">
                <td>{{ appointment.id }}</td>
                <td>{{ appointment.doctor.name }}</td>
                <td>{{ appointment.doctor.department || 'N/A' }}</td>
                <td>{{ new Date(appointment.date).toLocaleDateString() }}</td>
                <td>{{ new Date(appointment.time).toLocaleTimeString() }}</td>
                <td><span class="badge bg-warning">{{ appointment.status }}</span></td>
                <td>
                  <button class="btn btn-outline-danger btn-sm" @click="cancelAppointment(appointment)">Cancel</button>
                </td>
              </tr>
              <tr v-if="!dashboard.upcoming_appointments || dashboard.upcoming_appointments.length === 0">
                <td colspan="7" class="text-center text-muted">No upcoming appointments</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="alert alert-warning">
      No dashboard data available
    </div>
  </div>

  <!-- Department Detail View -->
  <div v-else-if="selectedDepartment && user" class="container mt-5">
    <!-- Department Header -->
    <div class="row mb-4">
      <div class="col-md-12">
        <button class="btn btn-link btn-sm" @click="closeDepartmentView">← Back</button>
        <h2>Department of {{ selectedDepartment.name }}</h2>
      </div>
    </div>

    <!-- Department Content -->
    <div class="card">
      <div class="card-body">
        <!-- Overview Section -->
        <div class="mb-5">
          <h5 class="mb-3">Overview</h5>
          <p>{{ selectedDepartment.description || 'No description available' }}</p>
        </div>

        <!-- Doctors List Section -->
        <div>
          <h5 class="mb-3">Doctors List</h5>
          <table class="table">
            <thead class="fw-normal">
              <tr>
                <th scope="col">Doctor Name</th>
                <th scope="col">Specialization</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doctor in selectedDepartment.doctors" :key="doctor.id">
                <td>{{ doctor.name }}</td>
                <td>{{ doctor.specialization || 'N/A' }}</td>
                <td>
                  <button class="btn btn-outline-primary btn-sm">check availability</button>
                  <button class="btn btn-outline-primary btn-sm">view details</button>
                </td>
              </tr>
              <tr v-if="!selectedDepartment.doctors || selectedDepartment.doctors.length === 0">
                <td colspan="3" class="text-center text-muted">No doctors available</td>
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
      <p>Please <RouterLink to="/login">login</RouterLink> to view dashboard</p>
    </div>
  </div>
</template>

<script>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
h1,
h2 {
  color: #333;
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

.table {
  margin-bottom: 0;
}

.table thead th {
  border-top: none;
  background-color: #f8f9fa;
  font-weight: 600;
}

.btn-outline-danger:hover {
  background-color: #dc3545;
  color: white;
}
</style>