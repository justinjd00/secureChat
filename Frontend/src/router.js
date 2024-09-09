import { createRouter, createWebHistory } from 'vue-router';
import SignIn from './components/SignIn.vue';
import SignUp from './components/SignUp.vue';

const routes = [
  { path: '/', name: 'SignIn', component: SignIn },
  { path: '/signup', name: 'SignUp', component: SignUp }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
