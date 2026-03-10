<script setup>
import { ref } from 'vue';

const formData = ref({
    username: '',
    password: '',
});

const isLoading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');
const formErrors = ref({});

const validateForm = () => {
    formErrors.value = {};

    if (!formData.value.username.trim()) {
        formErrors.value.username = 'Username is required';
    }

    if (!formData.value.password) {
        formErrors.value.password = 'Password is required';
    }

    if (formData.value.password && formData.value.password.length < 6) {
        formErrors.value.password = 'Password must be at least 6 characters';
    }

    return Object.keys(formErrors.value).length === 0;
};

const handleLogin = async (e) => {
    e.preventDefault();
    errorMessage.value = '';
    successMessage.value = '';

    if (!validateForm()) {
        return;
    }

    isLoading.value = true;

    try {
        const response = await fetch('http://localhost:5000/auth/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: formData.value.username,
                password: formData.value.password,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            errorMessage.value = data.message || data.error || 'Login failed. Please try again.';
            return;
        }

        successMessage.value = 'Login successful! Redirecting...';

        // Store token and user data
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));

        // Redirect to dashboard after short delay
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 1000);
    } catch (error) {
        errorMessage.value = 'An error occurred. Please check the connection and try again.';
        console.error('Login error:', error);
    } finally {
        isLoading.value = false;
    }
};

const clearError = (field) => {
    if (field) {
        delete formErrors.value[field];
    } else {
        formErrors.value = {};
    }
};
</script>

<template>
    <div class="container">
        <br><br>
        <h3>Login</h3>
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

        <!-- Login Form -->
        <form @submit="handleLogin" novalidate>
            <!-- Username Field -->
            <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input type="text" class="form-control" :class="{ 'is-invalid': formErrors.username }" id="username"
                    name="username" v-model="formData.username" placeholder="Enter your username" required
                    @input="clearError('username')" :disabled="isLoading">
                <div v-if="formErrors.username" class="invalid-feedback" style="display: block;">
                    {{ formErrors.username }}
                </div>
            </div>

            <!-- Password Field -->
            <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" :class="{ 'is-invalid': formErrors.password }" id="password"
                    name="password" v-model="formData.password" placeholder="Enter your password" required
                    @input="clearError('password')" :disabled="isLoading">
                <div v-if="formErrors.password" class="invalid-feedback" style="display: block;">
                    {{ formErrors.password }}
                </div>
            </div>

            <!-- Remember Me Checkbox -->
            <div class="mb-3 form-check">
                <input type="checkbox" class="form-check-input" id="rememberMe" name="rememberMe" :disabled="isLoading">
                <label class="form-check-label" for="rememberMe">
                    Remember me
                </label>
            </div>

            <!-- Submit Button -->
            <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="isLoading">
                <span v-if="isLoading">
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Signing in...
                </span>
                <span v-else>Sign In</span>
            </button>
        </form>

        <!-- Registration Link -->
        <div class="text-center">
            <p class="mb-0">
                Don't have an account?
                <a href="/register" class="text-decoration-none">Register here</a>
            </p>
        </div>

        <!-- Forgot Password Link -->
        <div class="text-center">
            <p class="mb-0">
                <a href="/forgot-password" class="text-decoration-none text-muted">Forgot your password?</a>
            </p>
        </div>
    </div>
    <!-- Footer Text -->
    <div class="text-center mt-4">
        <p class="text-muted small">&copy; 2024 Hospital Management System. All rights reserved.</p>
    </div>
</template>

<style scoped>
/* Component-specific styles */
.text-muted {
    color: #6c757d;
}

.is-invalid {
    border-color: #dc3545 !important;
}

.invalid-feedback {
    color: #dc3545;
    font-size: 0.875rem;
    margin-top: 0.25rem;
}

.form-check-label {
    user-select: none;
    cursor: pointer;
}

.spinner-border-sm {
    width: 1rem;
    height: 1rem;
    border-width: 0.2em;
}
</style>