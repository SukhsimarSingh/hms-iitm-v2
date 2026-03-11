<script setup>
import { ref } from 'vue'

const features = ref([
  {
    title: 'Appointment Scheduling',
    description: 'Schedule and manage appointments between patients and doctors with ease.'
  },
  {
    title: 'Doctor Management',
    description: 'Manage doctor profiles, specializations, and availability.'
  },
  {
    title: 'Patient Records',
    description: 'Maintain comprehensive patient medical history and records.'
  },
  {
    title: 'Treatment Tracking',
    description: 'Track treatments, prescriptions, and medical recommendations.'
  },
  {
    title: 'Secure Access',
    description: 'JWT-based authentication with role-based access control.'
  },
  {
    title: 'Admin Dashboard',
    description: 'Comprehensive admin dashboard for system overview and management.'
  }
])
</script>

<template>
  <div class="container-fluid p-0">
    <!-- Hero Section -->
    <section class="hero bg-primary text-white py-4">
      <div class="container">
        <div class="row justify-content-center align-items-center">
          <div class="col-md-8 text-center">
            <h1 class="display-4 fw-bold mb-4">Hospital Management System</h1>
            <p class="lead mb-4">
              A comprehensive solution for managing hospital operations efficiently.
              Schedule appointments, manage patient records, and track treatments.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features py-5 bg-light">
      <div class="container">
        <h2 class="text-center mb-5">Key Features</h2>
        <div class="row">
          <div v-for="feature in features" :key="feature.title" class="col-md-4 mb-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center">
                <h5 class="card-title">{{ feature.title }}</h5>
                <p class="card-text text-muted">{{ feature.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta py-2 mb-0 bg-light">
      <div class="container text-center">
        <h2 class="mb-3">Ready to Get Started?</h2>
        <p class="lead mb-4">Join the HMS platform and manage your hospital operations efficiently.</p>
        <div class="d-flex gap-3 justify-content-center">
          <RouterLink to="/login" class="btn btn-primary btn-md">Sign In</RouterLink>
          <RouterLink to="/register" class="btn btn-outline-primary btn-md">Create Account</RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%);
}

.hero h1 {
  font-size: 3rem;
}

.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15) !important;
}

.cta {
  padding-bottom: 50px !important;
}

.btn {
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  border-radius: 0.5rem;
}

</style>