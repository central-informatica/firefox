import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiFetch, apiFetchWithToken } from './api';

describe('apiFetch', () => {
  beforeEach(() => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({}),
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should make request to correct URL with API base', async () => {
    await apiFetch('/test/endpoint');

    expect(fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/test/endpoint',
      expect.any(Object)
    );
  });

  it('should include credentials in request', async () => {
    await apiFetch('/test');

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({ credentials: 'include' })
    );
  });

  it('should merge custom headers', async () => {
    await apiFetch('/test', {
      headers: { 'X-Custom-Header': 'custom-value' },
    });

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: { 'X-Custom-Header': 'custom-value' },
      })
    );
  });

  it('should pass method and body options', async () => {
    await apiFetch('/test', {
      method: 'POST',
      body: JSON.stringify({ data: 'test' }),
    });

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ data: 'test' }),
      })
    );
  });
});

describe('apiFetchWithToken', () => {
  let consoleWarnSpy;

  beforeEach(() => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({}),
      })
    );
    consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    // Clear cookies
    document.cookie.split(';').forEach(cookie => {
      const name = cookie.split('=')[0].trim();
      document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should include CSRF token header when token exists', async () => {
    document.cookie = 'csrf_token=test-csrf-123';

    await apiFetchWithToken('/protected');

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          'X-CSRF-Token': 'test-csrf-123',
        }),
      })
    );
  });

  it('should set Content-Type to application/json for non-FormData requests', async () => {
    document.cookie = 'csrf_token=test-token';

    await apiFetchWithToken('/protected', {
      method: 'POST',
      body: JSON.stringify({ key: 'value' }),
    });

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      })
    );
  });

  it('should not set Content-Type for FormData requests', async () => {
    document.cookie = 'csrf_token=test-token';
    const formData = new FormData();
    formData.append('file', new Blob(['test']));

    await apiFetchWithToken('/upload', {
      method: 'POST',
      body: formData,
    });

    const callArgs = fetch.mock.calls[0][1];
    expect(callArgs.headers['Content-Type']).toBeUndefined();
  });

  it('should warn when CSRF token is missing', async () => {
    await apiFetchWithToken('/protected');

    expect(consoleWarnSpy).toHaveBeenCalledWith(
      'CSRF token not found. User may not be authenticated.'
    );
  });

  it('should include credentials in request', async () => {
    document.cookie = 'csrf_token=test-token';

    await apiFetchWithToken('/protected');

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({ credentials: 'include' })
    );
  });

  it('should merge custom headers with CSRF and Content-Type', async () => {
    document.cookie = 'csrf_token=test-token';

    await apiFetchWithToken('/protected', {
      headers: { 'X-Custom': 'value' },
    });

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          'X-CSRF-Token': 'test-token',
          'Content-Type': 'application/json',
          'X-Custom': 'value',
        }),
      })
    );
  });
});
