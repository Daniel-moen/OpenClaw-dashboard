import { describe, expect, it } from 'vitest';
import { formatBytes, formatNumber } from './format';

describe('formatNumber', () => {
  it('keeps integers tidy', () => {
    expect(formatNumber(42)).toBe('42');
  });
  it('appends unit', () => {
    expect(formatNumber(7, 'ms')).toBe('7 ms');
  });
  it('handles large numbers', () => {
    expect(formatNumber(1234567)).toMatch(/1[,.]234[,.]567/);
  });
});

describe('formatBytes', () => {
  it('handles bytes', () => {
    expect(formatBytes(512)).toBe('512 B');
  });
  it('handles MB', () => {
    expect(formatBytes(2 * 1024 * 1024)).toBe('2.0 MB');
  });
});
