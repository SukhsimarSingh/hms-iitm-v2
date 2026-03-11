<script setup>
import { ref } from 'vue'

const formData = ref({
    name: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    age: '',
    contact: '',
})

const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const formErrors = ref({})

const validateForm = () => {
    formErrors.value = {}

    if (!formData.value.name.trim()) {
        formErrors.value.name = 'Name is required'
    }

    if (!formData.value.email.trim()) {
        formErrors.value.email = 'Email is required'
    } else if (!isValidEmail(formData.value.email)) {
        formErrors.value.email = 'Please enter a valid email'
    }

    if (!formData.value.username.trim()) {
        formErrors.value.username = 'Username is required'
    }

    if (!formData.value.password) {
        formErrors.value.password = 'Password is required'
    } else if (formData.value.password.length < 6) {
        formErrors.value.password = 'Password must be at least 6 characters'
    }

    if (formData.value.password !== formData.value.confirmPassword) {
        formErrors.value.confirmPassword = 'Passwords do not match'
    }

    if (!formData.value.age) {
        formErrors.value.age = 'Age is required'
    }

    return Object.keys(formErrors.value).length === 0
}

const isValidEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return re.test(email)
}

const handleRegister = async (e) => {
    e.preventDefault()
    errorMessage.value = ''
    successMessage.value = ''

    if (!validateForm()) {
        return
    }

    isLoading.value = true

    try {
        const payload = {
            username: formData.value.username,
            email: formData.value.email,
            password: formData.value.password,
            first_name: formData.value.name.split(' ')[0],
            last_name: formData.value.name.split(' ').slice(1).join(' '),
            role: 'patient',
            age: formData.value.age,
            contact: formData.value.contact,
        }

        const response = await fetch('http://localhost:5000/auth/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        })

        const data = await response.json()

        if (!response.ok) {
            errorMessage.value = data.message || data.error || 'Registration failed. Please try again.'
            return
        }

        successMessage.value = 'Registration successful! Redirecting to login...'

        setTimeout(() => {
            window.location.href = '/login'
        }, 1500)
    } catch (error) {
        errorMessage.value = 'An error occurred. Please try again.'
        console.error('Registration error:', error)
    } finally {
        isLoading.value = false
    }
}

const clearError = (field) => {
    if (field) {
        delete formErrors.value[field]
    } else {
        formErrors.value = {}
    }
}
</script>

<template>
    <div class="d-flex justify-content-center align-items-center" style="min-height: 100vh;">
        <div style="width: 100%; max-width: 800px; padding: 0 15px;">
            <div class="card">
                <div class="card-body p-5">
                    <h2 class="mb-2">Register</h2>
                    <p class="mb-4 text-muted">Create your patient account</p>
                    
                    <!-- Success Message -->
                    <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
                        {{ successMessage }}
                        <button type="button" class="btn-close" @click="successMessage = ''" aria-label="Close">
                        </button>
                    </div>

                    <!-- Error Message -->
                    <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
                        {{ errorMessage }}
                        <button type="button" class="btn-close" @click="errorMessage = ''" aria-label="Close">
                        </button>
                    </div>

                    <!-- Registration Form -->
                    <form @submit="handleRegister" novalidate>
                        <!-- Name Field -->
                        <div class="mb-3">
                            <label for="name" class="form-label">Full Name</label>
                            <input type="text" class="form-control" :class="{ 'is-invalid': formErrors.name }" id="name"
                                name="name" v-model="formData.name" placeholder="Enter your full name" required
                                @input="clearError('name')" :disabled="isLoading">
                            <div v-if="formErrors.name" class="invalid-feedback" style="display: block;">
                                {{ formErrors.name }}
                            </div>
                        </div>

                        <!-- Email Field -->
                        <div class="mb-3">
                            <label for="email" class="form-label">Email</label>
                            <input type="email" class="form-control" :class="{ 'is-invalid': formErrors.email }"
                                id="email" name="email" v-model="formData.email" placeholder="Enter your email" required
                                @input="clearError('email')" :disabled="isLoading">
                            <div v-if="formErrors.email" class="invalid-feedback" style="display: block;">
                                {{ formErrors.email }}
                            </div>
                        </div>

                        <!-- Username Field -->
                        <div class="mb-3">
                            <label for="username" class="form-label">Username</label>
                            <input type="text" class="form-control" :class="{ 'is-invalid': formErrors.username }"
                                id="username" name="username" v-model="formData.username"
                                placeholder="Choose a username" required @input="clearError('username')"
                                :disabled="isLoading">
                            <div v-if="formErrors.username" class="invalid-feedback" style="display: block;">
                                {{ formErrors.username }}
                            </div>
                        </div>

                        <!-- Password Field -->
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" :class="{ 'is-invalid': formErrors.password }"
                                id="password" name="password" v-model="formData.password"
                                placeholder="Enter a password (min 6 characters)" required
                                @input="clearError('password')" :disabled="isLoading">
                            <div v-if="formErrors.password" class="invalid-feedback" style="display: block;">
                                {{ formErrors.password }}
                            </div>
                        </div>

                        <!-- Confirm Password Field -->
                        <div class="mb-3">
                            <label for="confirmPassword" class="form-label">Confirm Password</label>
                            <input type="password" class="form-control"
                                :class="{ 'is-invalid': formErrors.confirmPassword }" id="confirmPassword"
                                name="confirmPassword" v-model="formData.confirmPassword"
                                placeholder="Confirm your password" required @input="clearError('confirmPassword')"
                                :disabled="isLoading">
                            <div v-if="formErrors.confirmPassword" class="invalid-feedback" style="display: block;">
                                {{ formErrors.confirmPassword }}
                            </div>
                        </div>

                        <!-- Age Field -->
                        <div class="mb-3">
                            <label for="age" class="form-label">Age</label>
                            <input type="number" class="form-control" :class="{ 'is-invalid': formErrors.age }"
                                id="age" name="age" v-model="formData.age" placeholder="Enter your age" min="1"
                                max="150" required @input="clearError('age')" :disabled="isLoading">
                            <div v-if="formErrors.age" class="invalid-feedback" style="display: block;">
                                {{ formErrors.age }}
                            </div>
                        </div>

                        <!-- Contact Number Field -->
                        <div class="mb-3">
                            <label for="contact" class="form-label">Contact Number</label>
                            <input type="tel" class="form-control" id="contact" name="contact"
                                v-model="formData.contact" placeholder="Enter your contact number"
                                :disabled="isLoading">
                        </div>

                        <!-- Submit Button -->
                        <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="isLoading">
                            <span v-if="isLoading">
                                <span class="spinner-border spinner-border-sm me-2" role="status"
                                    aria-hidden="true"></span>
                                Registering...
                            </span>
                            <span v-else>Create Account</span>
                        </button>
                    </form>

                    <!-- Login Link -->
                    <div class="text-center">
                        <p class="mb-0">
                            Already have an account?
                            <a href="/login" class="text-decoration-none">Login here</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.is-invalid {
    border-color: #dc3545 !important;
}

.invalid-feedback {
    color: #dc3545;
    font-size: 0.875rem;
    margin-top: 0.25rem;
}

.text-muted {
    color: #6c757d;
}

.spinner-border-sm {
    width: 1rem;
    height: 1rem;
    border-width: 0.2em;
}
</style>