import { createRouter, createWebHistory } from 'vue-router'
import HomePage from './components/HomePage.vue'
import LoginPage from './components/LoginPage.vue'
import DashboardPage from './components/DashboardPage.vue'
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
        component: DashboardPage,
        meta: { requiresAuth: true }
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
    } else if (to.meta.requiresAdmin && user) {
        const userData = JSON.parse(user)
        if (userData.role !== 'admin') {
            // Redirect to dashboard if admin is required but user is not admin
            next('/dashboard')
        } else {
            next()
        }
    } else {
        next()
    }
})

export default router
