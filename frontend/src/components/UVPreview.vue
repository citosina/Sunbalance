<template>
  <div class="uv-preview" v-if="props.trend.length">
    <h3>{{ props.title }}</h3>
    <ul>
      <li v-for="point in props.trend" :key="point.time">
        <span>{{ formatTime(point.time) }}</span>
        <strong>{{ point.uv_index.toFixed(1) }}</strong>
      </li>
    </ul>
  </div>
  <p v-else class="empty">No forecast available right now.</p>
</template>

<script setup lang="ts">
interface TrendPoint {
  time: string;
  uv_index: number;
}

interface Props {
  trend: TrendPoint[];
  title?: string;
}

const props = withDefaults(defineProps<Props>(), {
  title: 'UV in the next hours'
});

function formatTime(time: string) {
  return new Date(time).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}
</script>

<style scoped>
.uv-preview {
  padding: 1rem;
  border-radius: 1rem;
  background: rgba(15, 118, 110, 0.08);
}

.uv-preview ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.4rem;
}

.uv-preview li {
  display: flex;
  justify-content: space-between;
}

.empty {
  color: #6b7280;
  text-align: center;
}
</style>
