<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref(null)
const isLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const token = ref(null)

const formData = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  age: '',
  gender: ''
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

  // Populate form with user data
  formData.value = {
    first_name: user.value.first_name || '',
    last_name: user.value.last_name || '',
    email: user.value.email || '',
    phone: user.value.phone || '',
    age: user.value.age || '',
    gender: user.value.gender || ''
  }
})

const handleSaveProfile = async () => {
  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await fetch('http://localhost:5000/api/user/profile', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData.value),
    })

    const data = await response.json()

    if (response.ok) {
      successMessage.value = 'Profile updated successfully!'
      // Update localStorage
      const updatedUser = { ...user.value, ...formData.value }
      localStorage.setItem('user', JSON.stringify(updatedUser))
      user.value = updatedUser
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = data.message || 'Failed to update profile'
    }
  } catch (error) {
    errorMessage.value = 'An error occurred while updating profile'
    console.error('Error:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="container mt-5" v-if="user">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-md-8">
        <h2>Edit Profile</h2>
        <p class="text-muted">Update your personal information</p>
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

    <!-- Profile Form -->
    <div class="row">
      <div class="col-md-8">
        <div class="card">
          <div class="card-body">
            <form @submit.prevent="handleSaveProfile">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">First Name</label>
                  <input type="text" class="form-control" v-model="formData.first_name" />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Last Name</label>
                  <input type="text" class="form-control" v-model="formData.last_name" />
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Email</label>
                <input type="email" class="form-control" v-model="formData.email" />
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Phone</label>
                  <input type="tel" class="form-control" v-model="formData.phone" />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Age</label>
                  <input type="number" class="form-control" v-model="formData.age" />
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Gender</label>
                <select class="form-control" v-model="formData.gender">
                  <option value="">Select Gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div class="mt-4">
                <button type="submit" class="btn btn-primary" :disabled="isLoading">
                  <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  {{ isLoading ? 'Saving...' : 'Save Changes' }}
                </button>
                <button type="button" class="btn btn-secondary ms-2" @click="router.back()">
                  Cancel
                </button>
              </div>
            </form>
          </div>
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

button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
</style>
