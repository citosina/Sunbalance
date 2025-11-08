import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import SunCard from '../src/components/SunCard.vue';

const mockRecommendation = {
  profile_id: 1,
  status: 'good_now',
  recommended_minutes_min: 10,
  recommended_minutes_max: 15,
  warnings: ['Wear a hat'],
  suggested_windows: ['morning'],
  uv_index_now: 4.5,
  uv_trend: [
    { time: new Date().toISOString(), uv_index: 4.2 },
    { time: new Date().toISOString(), uv_index: 3.9 }
  ],
  data_quality: 'normal',
  timestamp: new Date().toISOString(),
  disclaimer: 'Test disclaimer'
};

describe('SunCard', () => {
  it('renders recommendation values', () => {
    const wrapper = mount(SunCard, {
      props: { recommendation: mockRecommendation }
    });
    expect(wrapper.text()).toContain('10–15 minutes');
    expect(wrapper.text()).toContain('Wear a hat');
  });
});
