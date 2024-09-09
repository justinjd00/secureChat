import {createRouter, createWebHashHistory} from 'vue-router';
const routes = [
    {
        path: '/',
        component: () => import('../views/Home.vue'),
        meta: {
            requiresAuth: true
        },
        children: [
            {
                path: '',
                name: 'Welcome',
                component: () => import('../components/Welcome.vue')
            },
        ]
    },

];

const router = createRouter({
    history: createWebHashHistory(import.meta.env.BASE_URL),
    routes
});

export default router