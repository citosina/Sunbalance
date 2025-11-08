<template>
  <div class="onboarding">
    <h2>Quick setup</h2>
    <p class="intro">Tell us a bit about your family so we can tailor today’s plan.</p>

    <div class="steps">
      <span v-for="(label, index) in stepLabels" :key="label" :class="{ active: index === step }">{{ label }}</span>
    </div>

    <form @submit.prevent="nextStep">
      <section v-if="step === 0" class="card">
        <h3>Where are you usually based?</h3>
        <label>
          Latitude
          <input type="number" v-model.number="form.latitude" step="0.0001" required />
        </label>
        <label>
          Longitude
          <input type="number" v-model.number="form.longitude" step="0.0001" required />
        </label>
        <label>
          Altitude (meters)
          <input type="number" v-model.number="form.altitude" />
        </label>
        <p class="hint">Tip: Mexico City is 19.4326, -99.1332 at ~2250 m.</p>
      </section>

      <section v-else-if="step === 1" class="card">
        <h3>Choose a skin type</h3>
        <div class="skin-grid">
          <label v-for="type in skinTypes" :key="type.value">
            <input type="radio" name="skin" :value="type.value" v-model="form.skinType" />
            <strong>{{ type.label }}</strong>
            <span>{{ type.description }}</span>
          </label>
        </div>
      </section>

      <section v-else-if="step === 2" class="card">
        <h3>Who should we plan for?</h3>
        <div class="profile-block">
          <h4>Your details</h4>
          <label>
            Display name
            <input v-model="form.self.name" required />
          </label>
          <label>
            Preferred clothing exposure (0-1)
            <input type="number" v-model.number="form.self.exposed_fraction" step="0.05" min="0" max="1" />
          </label>
        </div>

        <div class="profile-block">
          <h4>Family members</h4>
          <div v-for="(child, index) in form.children" :key="index" class="dependent">
            <input v-model="child.name" placeholder="Name" />
            <select v-model="child.age_group">
              <option value="child">Child</option>
              <option value="toddler">Toddler</option>
            </select>
            <select v-model="child.skin_type">
              <option v-for="type in skinTypes" :key="type.value" :value="type.value">{{ type.label }}</option>
            </select>
            <button type="button" class="link" @click="removeChild(index)">Remove</button>
          </div>
          <button type="button" class="secondary" @click="addChild">+ Add family member</button>
        </div>
      </section>

      <section v-else class="card">
        <h3>Preferred outdoor times</h3>
        <div class="checkbox-grid">
          <label v-for="window in timeWindows" :key="window.value">
            <input type="checkbox" :value="window.value" v-model="form.timeWindows" />
            {{ window.label }}
          </label>
        </div>
        <label>
          Sunscreen SPF (optional)
          <input type="number" v-model.number="form.self.sunscreen" min="10" step="5" />
        </label>
      </section>

      <div class="actions">
        <button type="button" class="secondary" v-if="step > 0" @click="step--">Back</button>
        <button v-if="step < stepLabels.length - 1" type="submit" class="primary">Next</button>
        <button v-else type="button" class="primary" @click="completeOnboarding" :disabled="isSaving">
          {{ isSaving ? 'Saving…' : 'Save &amp; view plan' }}
        </button>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">Preferences saved! Redirecting…</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import apiClient, { extractErrorMessage } from '../lib/api';
import { useProfileStore } from '../stores/profiles';

const router = useRouter();
const profileStore = useProfileStore();

const step = ref(0);
const stepLabels = ['Location', 'Skin type', 'Family', 'Habits'];
const isSaving = ref(false);
const error = ref<string | null>(null);
const success = ref(false);

const skinTypes = [
  { value: 'I', label: 'Type I', description: 'Very fair, burns easily' },
  { value: 'II', label: 'Type II', description: 'Fair, usually burns' },
  { value: 'III', label: 'Type III', description: 'Medium, sometimes burns' },
  { value: 'IV', label: 'Type IV', description: 'Olive, rarely burns' },
  { value: 'V', label: 'Type V', description: 'Brown, minimally burns' },
  { value: 'VI', label: 'Type VI', description: 'Dark brown, deeply pigmented' }
];

const timeWindows = [
  { value: 'morning', label: 'Morning (7–10am)' },
  { value: 'lunch', label: 'Lunch (11am–1pm)' },
  { value: 'afternoon', label: 'Afternoon (2–5pm)' },
  { value: 'evening', label: 'Evening (5–7pm)' }
];

const form = reactive({
  latitude: 19.4326,
  longitude: -99.1332,
  altitude: 2250,
  skinType: 'III',
  timeWindows: ['morning', 'afternoon'] as string[],
  self: {
    id: 0,
    name: 'You',
    exposed_fraction: 0.35,
    sunscreen: 30
  },
  children: [] as Array<{ name: string; age_group: 'child' | 'toddler'; skin_type: string }>
});

const primaryProfile = computed(() => profileStore.profiles.find((profile) => profile.is_primary));

onMounted(async () => {
  await profileStore.fetchAll();
  const primary = primaryProfile.value;
  if (primary) {
    form.self.id = primary.id;
    form.self.name = primary.name;
    const exposed = Number(primary.clothing_preferences?.exposed_fraction ?? 0.35);
    form.self.exposed_fraction = Number.isFinite(exposed) ? exposed : 0.35;
    form.timeWindows = [...primary.preferred_time_windows];
  }
  if (profileStore.userProfile) {
    form.latitude = profileStore.userProfile.default_latitude ?? form.latitude;
    form.longitude = profileStore.userProfile.default_longitude ?? form.longitude;
    form.altitude = profileStore.userProfile.default_altitude_m ?? form.altitude;
    form.skinType = profileStore.userProfile.default_skin_type;
    form.timeWindows = profileStore.userProfile.preferred_time_windows;
  }
});

function addChild() {
  form.children.push({ name: '', age_group: 'child', skin_type: form.skinType });
}

function removeChild(index: number) {
  form.children.splice(index, 1);
}

function nextStep() {
  if (step.value < stepLabels.length - 1) {
    step.value += 1;
  }
}

async function completeOnboarding() {
  try {
    isSaving.value = true;
    error.value = null;
    await apiClient.patch('/profiles/user/', {
      default_latitude: form.latitude,
      default_longitude: form.longitude,
      default_altitude_m: form.altitude,
      default_skin_type: form.skinType,
      preferred_time_windows: form.timeWindows
    });

    if (form.self.id) {
      await apiClient.patch(`/profiles/items/${form.self.id}/`, {
        name: form.self.name,
        skin_type: form.skinType,
        clothing_preferences: { exposed_fraction: form.self.exposed_fraction },
        sunscreen_spf: form.self.sunscreen,
        preferred_time_windows: form.timeWindows
      });
    }

    for (const child of form.children.filter((entry) => entry.name.trim().length)) {
      await apiClient.post('/profiles/items/', {
        name: child.name,
        relationship: child.age_group === 'child' ? 'child' : 'toddler',
        age_group: child.age_group,
        skin_type: child.skin_type,
        preferred_time_windows: form.timeWindows,
        clothing_preferences: { exposed_fraction: 0.25, hats: true },
        hats: true,
        sunscreen_spf: 30
      });
    }

    await profileStore.fetchAll();
    success.value = true;
    setTimeout(() => router.push('/today'), 900);
  } catch (err) {
    error.value = extractErrorMessage(err);
  } finally {
    isSaving.value = false;
  }
}
</script>

<style scoped>
.onboarding {
  max-width: 720px;
  margin: 0 auto;
  display: grid;
  gap: 1rem;
}

.intro {
  color: #475569;
}

.steps {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.steps span {
  padding: 0.4rem 0.6rem;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.3);
}

.steps span.active {
  background: #0ea5e9;
  color: #fff;
}

form {
  display: grid;
  gap: 1rem;
}

label {
  display: grid;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
}

input,
select {
  padding: 0.65rem 0.75rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(148, 163, 184, 0.6);
}

.skin-grid {
  display: grid;
  gap: 0.5rem;
}

.skin-grid label {
  border: 1px solid rgba(71, 85, 105, 0.25);
  border-radius: 0.75rem;
  padding: 0.75rem;
}

.profile-block {
  margin-bottom: 1rem;
}

.dependent {
  display: grid;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 0.75rem;
}

.actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.primary,
.secondary {
  border-radius: 999px;
  border: none;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  cursor: pointer;
}

.primary {
  background: #0ea5e9;
  color: #fff;
}

.secondary {
  background: rgba(14, 165, 233, 0.12);
  color: #0369a1;
}

.link {
  border: none;
  background: none;
  color: #dc2626;
  text-align: left;
  padding: 0;
  cursor: pointer;
}

.hint {
  font-size: 0.8rem;
  color: #6b7280;
}

.error {
  color: #dc2626;
}

.success {
  color: #047857;
}
</style>
