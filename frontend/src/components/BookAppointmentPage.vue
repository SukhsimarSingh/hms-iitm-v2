<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref(null)
const isLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const token = ref(null)
const doctors = ref([])

const formData = ref({
  doctor_id: '',
  date: '',
  time: ''
})

onMounted(async () => {
  const userData = localStorage.getItem('user')
  const tokenData = localStorage.getItem('token')

  if (!userData || !tokenData) {
    router.push('/login')
    return
  }

  user.value = JSON.parse(userData)
  token.value = tokenData

  if (user.value.role !== 'patient') {
    router.push('/dashboard')
    return
  }

  await fetchDoctors()
})

const fetchDoctors = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/get/doctor', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
    })

    if (response.ok) {
      const data = await response.json()
      // Filter to only active (not blacklisted) doctors
      const doctorList = Array.isArray(data) ? data : []
      doctors.value = doctorList.filter(doctor => doctor.active === true)
    }
  } catch (error) {
    console.error('Error fetching doctors:', error)
    errorMessage.value = 'Failed to load doctors list'
  }
}

const getAvailableSlots = () => {
  const slots = []
  const today = new Date()
  
  // Generate slots for next 7 days
  for (let i = 0; i < 7; i++) {
    const date = new Date(today)
    date.setDate(date.getDate() + i)
    const dateStr = date.toISOString().split('T')[0]
    const dateDisplay = date.toLocaleDateString('en-GB')
    
    // Morning slot
    slots.push({
      label: `${dateDisplay} - 08:00 - 12:00 PM`,
      date: dateStr,
      time: '08:00:00'
    })
    
    // Evening slot
    slots.push({
      label: `${dateDisplay} - 04:00 - 09:00 PM`,
      date: dateStr,
      time: '16:00:00'
    })
  }
  
  return slots
}

const handleBookAppointment = async () => {
  if (!formData.value.doctor_id || !formData.value.date || !formData.value.time) {
    errorMessage.value = 'Please fill in all required fields'
    return
  }

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    // First, get the patient ID for the current user from patient dashboard
    const dashboardResponse = await fetch('http://localhost:5000/api/patient/dashboard', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
    })

    if (!dashboardResponse.ok) {
      throw new Error('Failed to get patient information')
    }

    const dashboardData = await dashboardResponse.json()
    console.log('Dashboard data:', dashboardData)
    
    const patientId = dashboardData.patient?.patient_id

    if (!patientId) {
      console.error('Patient data:', dashboardData.patient)
      throw new Error('Patient record not found. Please complete your profile first.')
    }

    // Book the appointment
    const appointmentData = {
      patient_id: patientId,
      doctor_id: parseInt(formData.value.doctor_id),
      date: formData.value.date,
      time: formData.value.time
    }

    const response = await fetch('http://localhost:5000/api/appointment/create', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(appointmentData),
    })

    const data = await response.json()

    if (response.ok) {
      successMessage.value = 'Appointment booked successfully!'
      formData.value = {
        doctor_id: '',
        date: '',
        time: ''
      }
      setTimeout(() => {
        router.push('/patient/dashboard')
      }, 2000)
    } else {
      errorMessage.value = data.message || 'Failed to book appointment'
    }
  } catch (error) {
    errorMessage.value = error.message || 'An error occurred while booking appointment'
    console.error('Error:', error)
  } finally {
    isLoading.value = false
  }
}

const handleSlotChange = (event) => {
  const selectedSlot = getAvailableSlots()[event.target.value]
  if (selectedSlot) {
    formData.value.date = selectedSlot.date
    formData.value.time = selectedSlot.time
  }
}
</script>

<template>
  <div class="container mt-5" v-if="user && user.role === 'patient'">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-md-8">
        <h2>Book Appointment</h2>
        <p class="text-muted">Schedule a new appointment with a doctor</p>
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="alert alert-success alert-dismissible fade show">
      {{ successMessage }}
      <button type="button" class="btn-close" @click="successMessage = ''"></button>
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show">
      {{ errorMessage }}
      <button type="button" class="btn-close" @click="errorMessage = ''"></button>
    </div>

    <!-- Booking Form -->
    <div class="row">
      <div class="col-md-8">
        <div class="card">
          <div class="card-body">
            <form @submit.prevent="handleBookAppointment">
              <div class="mb-3">
                <label class="form-label">Select Doctor <span class="text-danger">*</span></label>
                <select class="form-control" v-model="formData.doctor_id" required>
                  <option value="">-- Choose a doctor --</option>
                  <option v-for="doctor in doctors" :key="doctor.id" :value="doctor.doctor_details?.doctor_id || doctor.id">
                    {{ doctor.first_name }} {{ doctor.last_name }} - {{ doctor.doctor_details?.specialization || 'General' }}
                  </option>
                </select>
                <small class="text-muted d-block mt-2" v-if="doctors.length === 0">
                  No active doctors available
                </small>
              </div>

              <div class="mb-3">
                <label class="form-label">Select Date & Time <span class="text-danger">*</span></label>
                <select class="form-control" @change="handleSlotChange" required>
                  <option value="">-- Choose a time slot --</option>
                  <option v-for="(slot, index) in getAvailableSlots()" :key="index" :value="index">
                    {{ slot.label }}
                  </option>
                </select>
              </div>

              <div class="mt-4">
                <button type="submit" class="btn btn-primary" :disabled="isLoading">
                  <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  {{ isLoading ? 'Booking...' : 'Book Appointment' }}
                </button>
                <button type="button" class="btn btn-secondary ms-2" @click="router.back()">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Info Panel -->
      <div class="col-md-4">
        <div class="card bg-light">
          <div class="card-body">
            <h5>Appointment Guidelines</h5>
            <ul class="small">
              <li>Book appointments at least 24 hours in advance</li>
              <li>Available slots for next 7 days</li>
              <li>Morning: 08:00 - 12:00 PM</li>
              <li>Evening: 04:00 - 09:00 PM</li>
              <li>Arrive 10 minutes early</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Not Authorized -->
  <div v-else class="container mt-5">
    <div class="alert alert-warning">
      <p>You do not have permission to access this page</p>
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
}

.card-body {
  padding: 2rem;
}

.form-label {
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.form-control {
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  padding: 0.5rem 0.75rem;
}

.form-control:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

.text-danger {
  color: #dc3545;
}

button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.bg-light {
  background-color: #f8f9fa !important;
}

ul {
  margin-bottom: 0;
  padding-left: 1.5rem;
}

li {
  margin-bottom: 0.5rem;
  line-height: 1.5;
}
</style>
