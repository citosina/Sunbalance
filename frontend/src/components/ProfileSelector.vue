<template>
  <div class="profile-selector" v-if="profiles.length">
    <label class="selector-label" for="profile-select">Who are we planning for?</label>
    <div class="selector-options">
      <button
        v-for="profile in profiles"
        :key="profile.id"
        type="button"
        class="selector-option"
        :class="{ active: profile.id === modelValue }"
        @click="$emit('update:modelValue', profile.id)"
      >
        {{ profile.name }}
        <small v-if="profile.is_primary" class="tag">You</small>
      </button>
    </div>
  </div>
  <p v-else class="empty-state">Create a profile to get started.</p>
</template>

<script setup lang="ts">
import type { SunProfile } from '../stores/profiles';

interface Props {
  profiles: SunProfile[];
  modelValue: number | null;
}

defineProps<Props>();

defineEmits<{ (e: 'update:modelValue', value: number): void }>();
</script>

<style scoped>
.profile-selector {
  margin-bottom: 1.5rem;
}

.selector-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.selector-options {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
}

.selector-option {
  padding: 0.75rem 1rem;
  border-radius: 9999px;
  border: 1px solid rgba(2, 132, 199, 0.2);
  background: rgba(191, 219, 254, 0.5);
  color: #0c4a6e;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 110px;
}

.selector-option.active {
  background: #0ea5e9;
  color: #fff;
  border-color: #0284c7;
}

.tag {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  margin-top: 0.35rem;
  letter-spacing: 0.05em;
}

.empty-state {
  text-align: center;
  color: #64748b;
}
</style>
