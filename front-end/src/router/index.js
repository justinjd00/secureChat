import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Signin from '../views/SignIn.vue'
import Signup from '../views/SignUp.vue'
import Auth from '../views/Auth.vue'
import MainChat from '../components/MainChat.vue';

const routes = [
    // other routes
    {
        path: '/mainchat',
        name: 'MainChat',
        component: MainChat
    },
    {
        path: '/',
        name: 'Signin',
        component: Signin
    },
    {
        path: '/signup',
        name: 'Signup',
        component: Signup
    },
    {
        path: '/auth',
        name: 'Auth',
        component: Auth,
        meta: {
            requiresAuth: true
        }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Add navigation guard to handle routes that require authentication
router.beforeEach((to, from, next) => {
    const isAuthenticated = !!localStorage.getItem('token')  // Replace with your auth logic
    if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
        next({ name: 'Signin' })
    } else {
        next()
    }
})

export default router
