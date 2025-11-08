<template>
  <div class="profiles-view">
    <h2>Profiles</h2>
    <p class="intro">Manage the people you plan for. Keep details up to date for conservative recommendations.</p>

    <section v-if="profileStore.userProfile" class="card">
      <h3>Household defaults</h3>
      <div class="grid">
        <label>
          Latitude
          <input type="number" v-model.number="household.latitude" step="0.0001" />
        </label>
        <label>
          Longitude
          <input type="number" v-model.number="household.longitude" step="0.0001" />
        </label>
        <label>
          Altitude (m)
          <input type="number" v-model.number="household.altitude" />
        </label>
        <label>
          Default skin type
          <select v-model="household.skin">
            <option v-for="type in skinTypes" :key="type.value" :value="type.value">{{ type.label }}</option>
          </select>
        </label>
      </div>
      <button class="primary" type="button" @click="saveHousehold">Save defaults</button>
    </section>

    <section class="card" v-for="profile in profileStore.profiles" :key="profile.id">
      <header class="header">
        <h3>{{ profile.name }}</h3>
        <span class="badge" v-if="profile.is_primary">Primary</span>
      </header>
      <div class="grid">
        <label>
          Name
          <input v-model="profileDrafts[profile.id].name" />
        </label>
        <label>
          Skin type
          <select v-model="profileDrafts[profile.id].skin_type">
            <option v-for="type in skinTypes" :key="type.value" :value="type.value">{{ type.label }}</option>
          </select>
        </label>
        <label>
          Sunscreen SPF
          <input type="number" v-model.number="profileDrafts[profile.id].sunscreen_spf" />
        </label>
        <label>
          Clothing exposed fraction (0-1)
          <input type="number" min="0" max="1" step="0.05" v-model.number="profileDrafts[profile.id].exposed_fraction" />
        </label>
      </div>
      <button class="primary" type="button" @click="saveProfile(profile.id)">Save changes</button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue';
import apiClient, { extractErrorMessage } from '../lib/api';
import { useProfileStore } from '../stores/profiles';

const profileStore = useProfileStore();

const skinTypes = [
  { value: 'I', label: 'Type I' },
  { value: 'II', label: 'Type II' },
  { value: 'III', label: 'Type III' },
  { value: 'IV', label: 'Type IV' },
  { value: 'V', label: 'Type V' },
  { value: 'VI', label: 'Type VI' }
];

const household = reactive({
  latitude: 19.4326,
  longitude: -99.1332,
  altitude: 2250,
  skin: 'III'
});

const profileDrafts: Record<number, { name: string; skin_type: string; sunscreen_spf: number | null; exposed_fraction: number }>
  = reactive({});

function syncDrafts() {
  for (const profile of profileStore.profiles) {
    profileDrafts[profile.id] = {
      name: profile.name,
      skin_type: profile.skin_type,
      sunscreen_spf: profile.sunscreen_spf,
      exposed_fraction: Number(profile.clothing_preferences?.exposed_fraction ?? 0.35)
    };
  }
}

onMounted(async () => {
  await profileStore.fetchAll();
  if (profileStore.userProfile) {
    household.latitude = profileStore.userProfile.default_latitude ?? household.latitude;
    household.longitude = profileStore.userProfile.default_longitude ?? household.longitude;
    household.altitude = profileStore.userProfile.default_altitude_m;
    household.skin = profileStore.userProfile.default_skin_type;
  }
  syncDrafts();
});

async function saveHousehold() {
  try {
    await apiClient.patch('/profiles/user/', {
      default_latitude: household.latitude,
      default_longitude: household.longitude,
      default_altitude_m: household.altitude,
      default_skin_type: household.skin
    });
  } catch (error) {
    alert(extractErrorMessage(error));
  }
}

async function saveProfile(id: number) {
  const draft = profileDrafts[id];
  if (!draft) return;
  try {
    await apiClient.patch(`/profiles/items/${id}/`, {
      name: draft.name,
      skin_type: draft.skin_type,
      sunscreen_spf: draft.sunscreen_spf,
      clothing_preferences: { exposed_fraction: draft.exposed_fraction }
    });
    await profileStore.fetchAll();
    syncDrafts();
  } catch (error) {
    alert(extractErrorMessage(error));
  }
}
</script>

<style scoped>
.profiles-view {
  max-width: 800px;
  margin: 0 auto;
  display: grid;
  gap: 1.5rem;
}

.intro {
  color: #475569;
}

.grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

label {
  display: grid;
  gap: 0.35rem;
}

input,
select {
  padding: 0.65rem 0.75rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(148, 163, 184, 0.6);
}

.primary {
  margin-top: 0.75rem;
  border: none;
  border-radius: 999px;
  padding: 0.65rem 1.3rem;
  background: #0ea5e9;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 999px;
  background: rgba(14, 165, 233, 0.18);
  color: #0c4a6e;
  font-size: 0.75rem;
  text-transform: uppercase;
}
</style>
