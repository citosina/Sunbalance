import { defineStore } from 'pinia';
import apiClient, { extractErrorMessage } from '../lib/api';

export interface SunProfile {
  id: number;
  name: string;
  relationship: string;
  age_group: string;
  skin_type: string;
  preferred_time_windows: string[];
  clothing_preferences: Record<string, unknown>;
  sunscreen_spf: number | null;
  hats: boolean;
  location_latitude: number | null;
  location_longitude: number | null;
  altitude_m: number;
  is_primary: boolean;
}

export interface UserProfile {
  id: number;
  default_latitude: number | null;
  default_longitude: number | null;
  default_altitude_m: number;
  default_skin_type: string;
  preferred_time_windows: string[];
}

interface ProfileState {
  profiles: SunProfile[];
  selectedProfileId: number | null;
  userProfile: UserProfile | null;
  status: 'idle' | 'loading' | 'error';
  error: string | null;
}

export const useProfileStore = defineStore('profiles', {
  state: (): ProfileState => ({
    profiles: [],
    selectedProfileId: null,
    userProfile: null,
    status: 'idle',
    error: null
  }),
  getters: {
    currentProfile(state): SunProfile | null {
      return state.profiles.find((profile) => profile.id === state.selectedProfileId) ?? null;
    }
  },
  actions: {
    async fetchAll() {
      this.status = 'loading';
      this.error = null;
      try {
        const [userProfileResponse, profileResponse] = await Promise.all([
          apiClient.get('/profiles/user/'),
          apiClient.get('/profiles/items/')
        ]);
        this.userProfile = userProfileResponse.data;
        this.profiles = profileResponse.data;
        if (!this.selectedProfileId && this.profiles.length > 0) {
          const primary = this.profiles.find((profile) => profile.is_primary) ?? this.profiles[0];
          this.selectedProfileId = primary.id;
        }
        this.status = 'idle';
      } catch (error) {
        this.status = 'error';
        this.error = extractErrorMessage(error);
      }
    },
    selectProfile(id: number) {
      this.selectedProfileId = id;
    }
  }
});
