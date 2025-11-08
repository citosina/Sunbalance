import { createRouter, createWebHistory } from 'vue-router';

const TodayView = () => import('../views/TodayView.vue');
const OnboardingView = () => import('../views/OnboardingView.vue');
const ProfilesView = () => import('../views/ProfilesView.vue');
const SettingsView = () => import('../views/SettingsView.vue');

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/today' },
    { path: '/today', component: TodayView },
    { path: '/onboarding', component: OnboardingView },
    { path: '/profiles', component: ProfilesView },
    { path: '/settings', component: SettingsView }
  ]
});

export default router;
