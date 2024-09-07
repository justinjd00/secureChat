import { createRouter, createWebHashHistory } from 'vue-router';
const routes = [
    {
        path: '/login',
        name: 'Auth',
        component: () => import('@/views/Auth.vue')
    },
    {
        path: '/',
        component: () => import('@/views/Home.vue'),
        meta: {
            requiresAuth: true
        },
        children: [
            {
                path: '',
                name: 'Welcome',
                component: () => import('@/components/Welcome.vue')
            },
        ]
    },

];

const router = createRouter({
    history: createWebHashHistory(import.meta.env.BASE_URL),
    routes
});