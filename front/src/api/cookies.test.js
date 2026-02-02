import { describe, it, expect, beforeEach } from 'vitest';
import { getCookie } from './cookies';

describe('getCookie', () => {
  beforeEach(() => {
    // Clear cookies before each test
    document.cookie.split(';').forEach(cookie => {
      const name = cookie.split('=')[0].trim();
      document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
    });
  });

  it('should return null when cookie does not exist', () => {
    const result = getCookie('nonexistent');
    expect(result).toBeNull();
  });

  it('should return the value when cookie exists', () => {
    document.cookie = 'test_cookie=test_value';
    const result = getCookie('test_cookie');
    expect(result).toBe('test_value');
  });

  it('should handle URL-encoded values', () => {
    document.cookie = 'encoded_cookie=' + encodeURIComponent('hello world');
    const result = getCookie('encoded_cookie');
    expect(result).toBe('hello world');
  });

  it('should handle multiple cookies', () => {
    document.cookie = 'first=one';
    document.cookie = 'second=two';
    document.cookie = 'third=three';

    expect(getCookie('first')).toBe('one');
    expect(getCookie('second')).toBe('two');
    expect(getCookie('third')).toBe('three');
  });

  it('should handle special characters in values', () => {
    const specialValue = 'a=b&c=d';
    document.cookie = 'special=' + encodeURIComponent(specialValue);
    const result = getCookie('special');
    expect(result).toBe(specialValue);
  });

  it('should not match partial cookie names', () => {
    document.cookie = 'csrf_token=abc123';
    document.cookie = 'old_csrf_token=xyz789';

    expect(getCookie('csrf_token')).toBe('abc123');
    expect(getCookie('token')).toBeNull();
  });
});
