<template>
  <div class="app-shell">
    <header class="app-header">
      <h1>SunBalance</h1>
      <p class="tagline">Your friendly sun &amp; vitamin D co-pilot</p>
    </header>
    <main>
      <RouterView />
    </main>
    <DisclaimerBanner />
  </div>
</template>

<script setup lang="ts">
import DisclaimerBanner from './components/DisclaimerBanner.vue';
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #fef9c3 0%, #fff 40%);
}

.app-header {
  padding: 1.25rem 1.5rem 0.5rem;
  text-align: center;
}

.tagline {
  margin-top: 0.25rem;
  font-size: 0.95rem;
  color: #555;
}

main {
  flex: 1;
  padding: 1rem;
}
</style>
