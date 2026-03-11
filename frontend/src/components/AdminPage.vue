<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref(null)
const adminData = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')
const token = ref(null)
const selectedDoctor = ref(null)
const selectedPatient = ref(null)
const showDoctorModal = ref(false)
const showPatientModal = ref(false)
const showEditDoctorModal = ref(false)
const showEditPatientModal = ref(false)
const editDoctorForm = ref(null)
const editPatientForm = ref(null)

onMounted(async () => {
  token.value = localStorage.getItem('token')
  const userData = localStorage.getItem('user')

  if (!token.value || !userData) {
    router.push('/login')
    return
  }

  user.value = JSON.parse(userData)
  if (user.value.role !== 'admin') {
    router.push('/dashboard')
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
  router.push('/')
}

const viewDoctor = (doctor) => {
  selectedDoctor.value = doctor
  showDoctorModal.value = true
}

const viewPatient = (patient) => {
  selectedPatient.value = patient
  showPatientModal.value = true
}

const closeDoctorModal = () => {
  showDoctorModal.value = false
  selectedDoctor.value = null
}

const closePatientModal = () => {
  showPatientModal.value = false
  selectedPatient.value = null
}

const editDoctor = (doctor) => {
  editDoctorForm.value = { ...doctor }
  showEditDoctorModal.value = true
}

const editPatient = (patient) => {
  editPatientForm.value = { ...patient }
  showEditPatientModal.value = true
}

const closeEditDoctorModal = () => {
  showEditDoctorModal.value = false
  editDoctorForm.value = null
}

const closeEditPatientModal = () => {
  showEditPatientModal.value = false
  editPatientForm.value = null
}

const saveEditedDoctor = async () => {
  try {
    const response = await fetch(`http://localhost:5000/api/admin/doctor/${editDoctorForm.value.user_id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(editDoctorForm.value),
    })

    if (response.ok) {
      successMessage.value = 'Doctor updated successfully'
      setTimeout(() => { successMessage.value = '' }, 3000)
      closeEditDoctorModal()
      location.reload()
    } else {
      const data = await response.json()
      errorMessage.value = data.message || 'Failed to update doctor'
    }
  } catch (error) {
    errorMessage.value = 'An error occurred while updating doctor'
    console.error('Error:', error)
  }
}

const saveEditedPatient = async () => {
  try {
    const response = await fetch(`http://localhost:5000/api/admin/patient/${editPatientForm.value.user_id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(editPatientForm.value),
    })

    if (response.ok) {
      successMessage.value = 'Patient updated successfully'
      setTimeout(() => { successMessage.value = '' }, 3000)
      closeEditPatientModal()
      location.reload()
    } else {
      const data = await response.json()
      errorMessage.value = data.message || 'Failed to update patient'
    }
  } catch (error) {
    errorMessage.value = 'An error occurred while updating patient'
    console.error('Error:', error)
  }
}

const deleteDoctor = async (doctor) => {
  if (!confirm(`Are you sure you want to delete ${doctor.name}?`)) {
    return
  }

  try {
    const response = await fetch(`http://localhost:5000/api/admin/doctor/${doctor.user_id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
    })

    if (response.ok) {
      successMessage.value = 'Doctor deleted successfully'
      setTimeout(() => { successMessage.value = '' }, 3000)
      location.reload()
    } else {
      const data = await response.json()
      errorMessage.value = data.message || 'Failed to delete doctor'
    }
  } catch (error) {
    errorMessage.value = 'An error occurred while deleting doctor'
    console.error('Error:', error)
  }
}

const deletePatient = async (patient) => {
  if (!confirm(`Are you sure you want to delete ${patient.first_name} ${patient.last_name}?`)) {
    return
  }

  try {
    const response = await fetch(`http://localhost:5000/api/admin/patient/${patient.user_id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
    })

    if (response.ok) {
      successMessage.value = 'Patient deleted successfully'
      setTimeout(() => { successMessage.value = '' }, 3000)
      location.reload()
    } else {
      const data = await response.json()
      errorMessage.value = data.message || 'Failed to delete patient'
    }
  } catch (error) {
    errorMessage.value = 'An error occurred while deleting patient'
    console.error('Error:', error)
  }
}

const blacklistDoctor = async (doctor) => {
  if (!confirm(`Are you sure you want to blacklist ${doctor.name}?`)) {
    return
  }

  try {
    const response = await fetch(`http://localhost:5000/api/admin/doctor/${doctor.user_id}/blacklist`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
    })

    if (response.ok) {
      successMessage.value = 'Doctor blacklisted successfully'
      setTimeout(() => { successMessage.value = '' }, 3000)
      location.reload()
    } else {
      const data = await response.json()
      errorMessage.value = data.message || 'Failed to blacklist doctor'
    }
  } catch (error) {
    errorMessage.value = 'An error occurred while blacklisting doctor'
    console.error('Error:', error)
  }
}

const blacklistPatient = async (patient) => {
  if (!confirm(`Are you sure you want to blacklist ${patient.first_name} ${patient.last_name}?`)) {
    return
  }

  try {
    const response = await fetch(`http://localhost:5000/api/admin/patient/${patient.user_id}/blacklist`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
    })

    if (response.ok) {
      successMessage.value = 'Patient blacklisted successfully'
      setTimeout(() => { successMessage.value = '' }, 3000)
      location.reload()
    } else {
      const data = await response.json()
      errorMessage.value = data.message || 'Failed to blacklist patient'
    }
  } catch (error) {
    errorMessage.value = 'An error occurred while blacklisting patient'
    console.error('Error:', error)
  }
}
</script>

<template>
  <div class="container mt-5" v-if="adminData">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-md-8">
        <h2>Welcome, {{ user.first_name }}!</h2>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="alert alert-info">
      <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
      Loading admin dashboard...
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="alert alert-success alert-dismissible fade show">
      {{ successMessage }}
      <button type="button" class="btn-close" @click="successMessage = ''"></button>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="alert alert-danger">
      {{ errorMessage }}
    </div>

    <!-- Admin Dashboard Content -->
    <div v-else-if="adminData" class="row">
      <!-- Stats Cards -->
      <div class="col-md-3 mb-4" v-if="adminData.stats">
        <div class="card">
          <div class="card-body text-center">
            <h3 class="text-primary">{{ adminData.stats.total_users }}</h3>
            <p class="text-muted small">Total Users</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-4" v-if="adminData.stats">
        <div class="card">
          <div class="card-body text-center">
            <h3 class="text-success">{{ adminData.stats.total_doctors }}</h3>
            <p class="text-muted small">Doctors</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-4" v-if="adminData.stats">
        <div class="card">
          <div class="card-body text-center">
            <h3 class="text-info">{{ adminData.stats.total_patients }}</h3>
            <p class="text-muted small">Patients</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-4" v-if="adminData.stats">
        <div class="card">
          <div class="card-body text-center">
            <h3 class="text-warning">{{ adminData.stats.total_appointments }}</h3>
            <p class="text-muted small">Appointments</p>
          </div>
        </div>
      </div>

      <!-- Registered Doctors -->
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Registered Doctors</h5>
          </div>
          <div class="card-body">
            <table class="table">
              <thead class="fw-normal">
                <tr>
                  <th scope="col">Doctor Name</th>
                  <th scope="col">View</th>
                  <th scope="col">Edit</th>
                  <th scope="col">Delete</th>
                  <th scope="col">Blacklist</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="doctor in adminData.registered_doctors" :key="doctor.user_id">
                  <td>{{ doctor.name }}</td>
                  <td><button class="btn btn-outline-primary btn-sm" @click="viewDoctor(doctor)">View</button></td>
                  <td><button class="btn btn-outline-secondary btn-sm" @click="editDoctor(doctor)">Edit</button></td>
                  <td><button class="btn btn-outline-danger btn-sm" @click="deleteDoctor(doctor)">Delete</button></td>
                  <td><button class="btn btn-outline-warning btn-sm" @click="blacklistDoctor(doctor)">Blacklist</button>
                  </td>
                </tr>
                <tr v-if="!adminData.registered_doctors || adminData.registered_doctors.length === 0">
                  <td colspan="5" class="text-center text-muted">No registered doctors</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <br>
        <!-- Registered Patients -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Registered Patients</h5>
          </div>
          <div class="card-body">
            <table class="table">
              <thead class="fw-normal">
                <tr>
                  <th scope="col">Patient Name</th>
                  <th scope="col">View</th>
                  <th scope="col">Edit</th>
                  <th scope="col">Delete</th>
                  <th scope="col">Blacklist</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="patient in adminData.registered_patients" :key="patient.user_id">
                  <td>{{ patient.first_name + ' ' + patient.last_name || patient.username }}</td>
                  <td><button class="btn btn-outline-primary btn-sm" @click="viewPatient(patient)">View</button></td>
                  <td><button class="btn btn-outline-secondary btn-sm" @click="editPatient(patient)">Edit</button></td>
                  <td><button class="btn btn-outline-danger btn-sm" @click="deletePatient(patient)">Delete</button></td>
                  <td><button class="btn btn-outline-warning btn-sm"
                      @click="blacklistPatient(patient)">Blacklist</button></td>
                </tr>
                <tr v-if="!adminData.registered_patients || adminData.registered_patients.length === 0">
                  <td colspan="5" class="text-center text-muted">No registered patients</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <br>
        <!-- Upcoming Appointments -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Upcoming Appointments</h5>
          </div>
          <div class="card-body">
            <table class="table">
              <thead class="fw-normal">
                <tr>
                  <th scope="col">Appointment ID</th>
                  <th scope="col">Patient Name</th>
                  <th scope="col">Doctor Name</th>
                  <th scope="col">Department</th>
                  <th scope="col">Date</th>
                  <th scope="col">Time</th>
                  <th scope="col">Status</th>
                  <th scope="col">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="appointment in adminData.upcoming_appointments" :key="appointment.id">
                  <td>{{ appointment.id }}</td>
                  <td>{{ appointment.patient.name }}</td>
                  <td>{{ appointment.doctor.name }}</td>
                  <td>{{ appointment.doctor.department.name }}</td>
                  <td>{{ new Date(appointment.date).toLocaleDateString() }}</td>
                  <td>{{ new Date(appointment.time).toLocaleTimeString() }}</td>
                  <td>{{ appointment.status }}</td>
                  <td>
                    <button class="btn btn-outline-primary btn-sm" @click="viewAppointment(appointment)">View</button>
                    <button class="btn btn-outline-secondary btn-sm" @click="editAppointment(appointment)">Edit</button>
                    <button class="btn btn-outline-danger btn-sm"
                      @click="deleteAppointment(appointment)">Delete</button>
                    <button class="btn btn-outline-warning btn-sm"
                      @click="cancelAppointment(appointment)">Cancel</button>
                  </td>
                </tr>
                <tr v-if="!adminData.upcoming_appointments || adminData.upcoming_appointments.length === 0">
                  <td colspan="8" class="text-center text-muted">No upcoming appointments</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Doctor Details Modal -->
  <div v-if="showDoctorModal" class="modal d-block" style="background-color: rgba(0, 0, 0, 0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Doctor Details</h5>
          <button type="button" class="btn-close" @click="closeDoctorModal"></button>
        </div>
        <div class="modal-body" v-if="selectedDoctor">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label fw-bold">Name:</label>
              <p>{{ selectedDoctor.name }}</p>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label fw-bold">Email:</label>
              <p>{{ selectedDoctor.email || 'N/A' }}</p>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label fw-bold">License Number:</label>
              <p>{{ selectedDoctor.license_number || 'N/A' }}</p>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label fw-bold">Specialization:</label>
              <p>{{ selectedDoctor.specialization || 'N/A' }}</p>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label fw-bold">Phone:</label>
              <p>{{ selectedDoctor.phone || 'N/A' }}</p>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label fw-bold">Status:</label>
              <p>{{ selectedDoctor.status || 'Active' }}</p>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeDoctorModal">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Patient Details Modal -->
  <div v-if="showPatientModal" class="modal d-block" style="background-color: rgba(0, 0, 0, 0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Patient Details</h5>
          <button type="button" class="btn-close" @click="closePatientModal"></button>
        </div>
        <div class="modal-body" v-if="selectedPatient">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label fw-bold">First Name:</label>
              <p>{{ selectedPatient.first_name || 'N/A' }}</p>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label fw-bold">Last Name:</label>
              <p>{{ selectedPatient.last_name || 'N/A' }}</p>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label fw-bold">Email:</label>
              <p>{{ selectedPatient.email || 'N/A' }}</p>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label fw-bold">Phone:</label>
              <p>{{ selectedPatient.phone || 'N/A' }}</p>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label fw-bold">Age:</label>
              <p>{{ selectedPatient.age || 'N/A' }}</p>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label fw-bold">Gender:</label>
              <p>{{ selectedPatient.gender || 'N/A' }}</p>
            </div>
            <div class="col-md-12 mb-3">
              <label class="form-label fw-bold">Medical History:</label>
              <p>{{ selectedPatient.medical_history || 'No records' }}</p>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closePatientModal">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Edit Doctor Modal -->
  <div v-if="showEditDoctorModal" class="modal d-block" style="background-color: rgba(0, 0, 0, 0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Edit Doctor</h5>
          <button type="button" class="btn-close" @click="closeEditDoctorModal"></button>
        </div>
        <div class="modal-body" v-if="editDoctorForm">
          <form @submit.prevent="saveEditedDoctor">
            <div class="mb-3">
              <label class="form-label">Name:</label>
              <input v-model="editDoctorForm.name" type="text" class="form-control" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Email:</label>
              <input v-model="editDoctorForm.email" type="email" class="form-control">
            </div>
            <div class="mb-3">
              <label class="form-label">License Number:</label>
              <input v-model="editDoctorForm.license_number" type="text" class="form-control">
            </div>
            <div class="mb-3">
              <label class="form-label">Specialization:</label>
              <input v-model="editDoctorForm.specialization" type="text" class="form-control">
            </div>
            <div class="mb-3">
              <label class="form-label">Phone:</label>
              <input v-model="editDoctorForm.phone" type="tel" class="form-control">
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeEditDoctorModal">Cancel</button>
          <button type="button" class="btn btn-primary" @click="saveEditedDoctor">Save Changes</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Edit Patient Modal -->
  <div v-if="showEditPatientModal" class="modal d-block" style="background-color: rgba(0, 0, 0, 0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Edit Patient</h5>
          <button type="button" class="btn-close" @click="closeEditPatientModal"></button>
        </div>
        <div class="modal-body" v-if="editPatientForm">
          <form @submit.prevent="saveEditedPatient">
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">First Name:</label>
                <input v-model="editPatientForm.first_name" type="text" class="form-control" required>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Last Name:</label>
                <input v-model="editPatientForm.last_name" type="text" class="form-control" required>
              </div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Email:</label>
                <input v-model="editPatientForm.email" type="email" class="form-control">
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Phone:</label>
                <input v-model="editPatientForm.phone" type="tel" class="form-control">
              </div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Age:</label>
                <input v-model="editPatientForm.age" type="number" class="form-control">
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Gender:</label>
                <select v-model="editPatientForm.gender" class="form-control">
                  <option value="">Select Gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Medical History:</label>
              <textarea v-model="editPatientForm.medical_history" class="form-control" rows="4"></textarea>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeEditPatientModal">Cancel</button>
          <button type="button" class="btn btn-primary" @click="saveEditedPatient">Save Changes</button>
        </div>
      </div>
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

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-dialog {
  position: relative;
}

.modal-content {
  border-radius: 0.25rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.form-control,
.form-select {
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
}

.form-control:focus,
.form-select:focus {
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-label {
  margin-bottom: 0.5rem;
  color: #333;
}
</style>