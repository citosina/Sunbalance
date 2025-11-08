<template>
  <div class="today-view">
    <ProfileSelector
      :profiles="profileStore.profiles"
      v-model="selectedProfileId"
    />

    <section v-if="loading" class="card loading">Loading today’s plan…</section>
    <section v-else-if="error" class="card error">{{ error }}</section>

    <SunCard :recommendation="currentRecommendation" />

    <UVPreview v-if="currentRecommendation" :trend="currentRecommendation.uv_trend" />

    <div class="actions">
      <button class="secondary" type="button" @click="refresh">Refresh data</button>
      <RouterLink class="link" to="/onboarding">Update preferences</RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { RouterLink } from 'vue-router';
import ProfileSelector from '../components/ProfileSelector.vue';
import SunCard from '../components/SunCard.vue';
import UVPreview from '../components/UVPreview.vue';
import { useProfileStore } from '../stores/profiles';
import { useRecommendationStore } from '../stores/recommendation';

const profileStore = useProfileStore();
const recommendationStore = useRecommendationStore();

const selectedProfileId = ref<number | null>(null);
const error = computed(() => profileStore.error || recommendationStore.error);
const loading = computed(() => profileStore.status === 'loading' || recommendationStore.status === 'loading');

const currentRecommendation = computed(() => {
  if (!selectedProfileId.value) return null;
  return recommendationStore.items[selectedProfileId.value] ?? null;
});

async function loadInitial() {
  if (!profileStore.profiles.length) {
    await profileStore.fetchAll();
  }
  if (!selectedProfileId.value && profileStore.currentProfile) {
    selectedProfileId.value = profileStore.currentProfile.id;
  }
  if (selectedProfileId.value) {
    await recommendationStore.fetchForProfile(selectedProfileId.value);
  }
}

onMounted(() => {
  loadInitial();
});

watch(selectedProfileId, async (id) => {
  if (!id) return;
  profileStore.selectProfile(id);
  await recommendationStore.fetchForProfile(id);
});

async function refresh() {
  if (selectedProfileId.value) {
    await recommendationStore.fetchForProfile(selectedProfileId.value);
  }
}
</script>

<style scoped>
.today-view {
  display: grid;
  gap: 1.25rem;
  max-width: 720px;
  margin: 0 auto;
}

.loading {
  text-align: center;
}

.error {
  background: rgba(248, 113, 113, 0.15);
  color: #b91c1c;
  border: 1px solid rgba(185, 28, 28, 0.2);
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.secondary {
  border-radius: 999px;
  border: none;
  padding: 0.75rem 1.2rem;
  font-weight: 600;
  background: rgba(14, 165, 233, 0.15);
  color: #0369a1;
  cursor: pointer;
}

.link {
  color: #0284c7;
}
</style>
