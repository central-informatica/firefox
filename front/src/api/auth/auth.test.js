import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { loginWeb, getMe, logout } from './auth';

// Mock the api module
vi.mock('../api', () => ({
  apiFetch: vi.fn(),
  apiFetchWithToken: vi.fn(),
}));

import { apiFetch, apiFetchWithToken } from '../api';

describe('loginWeb', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should call apiFetch with correct parameters', async () => {
    apiFetch.mockResolvedValue({ ok: true });

    await loginWeb('test@example.com', 'password123');

    expect(apiFetch).toHaveBeenCalledWith('/auth/login/web', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email: 'test@example.com', password: 'password123' }),
    });
  });

  it('should return the response from apiFetch', async () => {
    const mockResponse = { ok: true, status: 200 };
    apiFetch.mockResolvedValue(mockResponse);

    const result = await loginWeb('test@example.com', 'password123');

    expect(result).toBe(mockResponse);
  });

  it('should handle network errors', async () => {
    const networkError = new Error('Network error');
    apiFetch.mockRejectedValue(networkError);

    await expect(loginWeb('test@example.com', 'password')).rejects.toThrow('Network error');
  });
});

describe('getMe', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call apiFetchWithToken with GET method', async () => {
    apiFetchWithToken.mockResolvedValue({ ok: true });

    await getMe();

    expect(apiFetchWithToken).toHaveBeenCalledWith('/auth/me', {
      method: 'GET',
    });
  });

  it('should return the response from apiFetchWithToken', async () => {
    const mockResponse = { ok: true, json: () => Promise.resolve({ id: 1 }) };
    apiFetchWithToken.mockResolvedValue(mockResponse);

    const result = await getMe();

    expect(result).toBe(mockResponse);
  });
});

describe('logout', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call apiFetchWithToken with POST method', async () => {
    apiFetchWithToken.mockResolvedValue({ ok: true });

    await logout();

    expect(apiFetchWithToken).toHaveBeenCalledWith('/auth/logout', {
      method: 'POST',
    });
  });
});
