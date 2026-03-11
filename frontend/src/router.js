import { createRouter, createWebHistory } from 'vue-router'
import HomePage from './components/HomePage.vue'
import LoginPage from './components/LoginPage.vue'
import DoctorDashboardPage from './components/DoctorDashboardPage.vue'
import PatientDashboardPage from './components/PatientDashboardPage.vue'
import RegisterPage from './components/RegisterPage.vue'
import AdminPage from './components/AdminPage.vue'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: HomePage,
    },
    {
        path: '/login',
        name: 'Login',
        component: LoginPage,
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        redirect: (to) => {
            const user = localStorage.getItem('user')
            if (!user) return '/login'
            
            const userData = JSON.parse(user)
            if (userData.role === 'doctor') return '/doctor/dashboard'
            if (userData.role === 'admin') return '/admin'
            return '/patient/dashboard'
        },
        meta: { requiresAuth: true }
    },
    {
        path: '/doctor/dashboard',
        name: 'DoctorDashboard',
        component: DoctorDashboardPage,
        meta: { requiresAuth: true, requiresRole: 'doctor' }
    },
    {
        path: '/patient/dashboard',
        name: 'PatientDashboard',
        component: PatientDashboardPage,
        meta: { requiresAuth: true, requiresRole: 'patient' }
    },
    {
        path: '/register',
        name: 'Register',
        component: RegisterPage,
    },
    {
        path: '/admin',
        name: 'Admin',
        component: AdminPage,
        meta: { requiresAuth: true, requiresAdmin: true }
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

// Navigation guards
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    const user = localStorage.getItem('user')

    if (to.meta.requiresAuth && !token) {
        // Redirect to login if auth is required but user is not logged in
        next('/login')
    } else if (to.meta.requiresRole && user) {
        const userData = JSON.parse(user)
        if (userData.role !== to.meta.requiresRole) {
            // Redirect to appropriate dashboard based on role
            if (userData.role === 'doctor') {
                next('/doctor/dashboard')
            } else if (userData.role === 'admin') {
                next('/admin')
            } else {
                next('/patient/dashboard')
            }
        } else {
            next()
        }
    } else if (to.meta.requiresAdmin && user) {
        const userData = JSON.parse(user)
        if (userData.role !== 'admin') {
            // Redirect to appropriate dashboard based on role
            if (userData.role === 'doctor') {
                next('/doctor/dashboard')
            } else {
                next('/patient/dashboard')
            }
        } else {
            next()
        }
    } else {
        next()
    }
})

export default router
