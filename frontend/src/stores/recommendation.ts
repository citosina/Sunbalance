import { defineStore } from 'pinia';
import apiClient, { extractErrorMessage } from '../lib/api';

export interface RecommendationPayload {
  profile_id: number;
  status: string;
  recommended_minutes_min: number;
  recommended_minutes_max: number;
  warnings: string[];
  suggested_windows?: string[];
  uv_index_now: number;
  uv_trend: { time: string; uv_index: number }[];
  data_quality: string;
  timestamp: string;
  disclaimer: string;
}

interface RecommendationState {
  items: Record<number, RecommendationPayload>;
  status: 'idle' | 'loading' | 'error';
  error: string | null;
}

export const useRecommendationStore = defineStore('recommendation', {
  state: (): RecommendationState => ({
    items: {},
    status: 'idle',
    error: null
  }),
  actions: {
    async fetchForProfile(profileId: number) {
      this.status = 'loading';
      this.error = null;
      try {
        const response = await apiClient.get('/recommendation/today/', {
          params: { profile_id: profileId }
        });
        this.items[profileId] = response.data;
        this.status = 'idle';
      } catch (error) {
        this.status = 'error';
        this.error = extractErrorMessage(error);
      }
    }
  }
});
