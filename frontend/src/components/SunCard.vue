<template>
  <section class="card sun-card" v-if="recommendation">
    <header>
      <p class="status" :class="recommendation.status">{{ statusLabel }}</p>
      <h2>{{ minutesRange }}</h2>
      <p class="subtitle">Recommended safe exposure window</p>
    </header>

    <div class="uv-current">
      <span class="uv-label">Current UV</span>
      <strong>{{ recommendation.uv_index_now?.toFixed(1) ?? '—' }}</strong>
      <span class="quality" :class="recommendation.data_quality">{{ qualityLabel }}</span>
    </div>

    <div class="uv-trend" v-if="recommendation.uv_trend?.length">
      <h3>Next few hours</h3>
      <ul>
        <li v-for="point in recommendation.uv_trend" :key="point.time">
          <span>{{ formatHour(point.time) }}</span>
          <span class="value">{{ point.uv_index.toFixed(1) }}</span>
        </li>
      </ul>
    </div>

    <ul class="warnings" v-if="recommendation.warnings.length">
      <li v-for="warning in recommendation.warnings" :key="warning">⚠️ {{ warning }}</li>
    </ul>

    <div v-if="recommendation.suggested_windows?.length" class="suggested">
      Suggested time windows: {{ recommendation.suggested_windows.join(', ') }}
    </div>

    <p class="disclaimer">{{ recommendation.disclaimer }}</p>
  </section>
  <section class="card empty" v-else>
    <p>Select a profile to view today's plan.</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { RecommendationPayload } from '../stores/recommendation';

interface Props {
  recommendation: RecommendationPayload | null;
}

const props = defineProps<Props>();

const statusCopy: Record<string, string> = {
  good_now: 'Great time to go outside',
  caution_now: 'High UV – keep it short',
  avoid_now: 'Too harsh right now',
  low_uv: 'Gentle sun available'
};

const qualityCopy: Record<string, string> = {
  normal: 'Live data',
  degraded: 'Fallback mode',
  unknown: 'Status unknown'
};

const statusLabel = computed(() => statusCopy[props.recommendation?.status ?? ''] ?? 'Sun update');
const minutesRange = computed(() => {
  if (!props.recommendation) return '—';
  return `${props.recommendation.recommended_minutes_min}–${props.recommendation.recommended_minutes_max} minutes`;
});
const qualityLabel = computed(() => qualityCopy[props.recommendation?.data_quality ?? 'unknown']);

function formatHour(timestamp: string) {
  const date = new Date(timestamp);
  return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}
</script>

<style scoped>
.sun-card {
  display: grid;
  gap: 1rem;
}

header {
  text-align: center;
}

.status {
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.5rem;
}

.status.good_now {
  color: #047857;
}

.status.caution_now {
  color: #f97316;
}

.status.avoid_now {
  color: #dc2626;
}

.uv-current {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  justify-content: center;
}

.uv-label {
  font-weight: 600;
}

.quality {
  font-size: 0.8rem;
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  background: rgba(14, 165, 233, 0.15);
  color: #0369a1;
}

.quality.degraded {
  background: rgba(249, 115, 22, 0.15);
  color: #c2410c;
}

.uv-trend ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.35rem;
}

.uv-trend li {
  display: flex;
  justify-content: space-between;
  padding: 0.6rem 0.75rem;
  border-radius: 0.75rem;
  background: rgba(15, 118, 110, 0.08);
}

.uv-trend .value {
  font-weight: 600;
}

.warnings {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.4rem;
  font-size: 0.9rem;
}

.suggested {
  background: rgba(250, 204, 21, 0.15);
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
}

.disclaimer {
  font-size: 0.75rem;
  color: #64748b;
  text-align: center;
}

.empty {
  text-align: center;
  color: #475569;
}
</style>
