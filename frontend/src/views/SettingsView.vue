<template>
  <div class="settings-view">
    <h2>Settings</h2>
    <p class="intro">Manage account access and refresh tokens.</p>

    <section class="card">
      <h3>Authentication</h3>
      <p>Logged in: <strong>{{ auth.isAuthenticated ? 'Yes' : 'No' }}</strong></p>
      <button class="danger" type="button" @click="logout">Log out</button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const router = useRouter();

function logout() {
  auth.logout();
  router.push('/onboarding');
}
</script>

<style scoped>
.settings-view {
  max-width: 640px;
  margin: 0 auto;
  display: grid;
  gap: 1.5rem;
}

.intro {
  color: #475569;
}

.danger {
  border: none;
  border-radius: 0.75rem;
  padding: 0.75rem 1.5rem;
  background: rgba(220, 38, 38, 0.15);
  color: #b91c1c;
  font-weight: 600;
  cursor: pointer;
}
</style>
