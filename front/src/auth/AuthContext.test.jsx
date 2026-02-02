import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider, AuthContext } from './AuthContext';
import { useContext } from 'react';

// Mock the api module
vi.mock('../api/api', () => ({
  apiFetchWithToken: vi.fn(),
}));

// Mock the auth api module
vi.mock('../api/auth/auth', () => ({
  loginWeb: vi.fn(),
  getMe: vi.fn(),
  logout: vi.fn(),
}));

import { apiFetchWithToken } from '../api/api';
import { getMe } from '../api/auth/auth';

// Test component to access AuthContext
function TestConsumer({ onContext }) {
  const context = useContext(AuthContext);
  onContext(context);
  return <div data-testid="test-consumer">Consumer</div>;
}

function renderWithRouter(ui) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe('AuthContext - register function', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Default mock for getMe (called on mount)
    getMe.mockResolvedValue({ ok: false });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should call apiFetchWithToken with correct endpoint', async () => {
    let authContext;
    apiFetchWithToken.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 1 }),
    });

    renderWithRouter(
      <AuthProvider>
        <TestConsumer onContext={(ctx) => (authContext = ctx)} />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(authContext).toBeDefined();
    });

    await authContext.register({
      organization_name: 'Empresa Teste',
      cnpj: '12345678000190',
      address_street: 'Rua Teste',
      address_city: 'Sao Paulo',
      address_state: 'SP',
      address_country: 'Brasil',
      address_postal_code: '01234567',
      admin_email: 'admin@teste.com',
      admin_password: 'senha123',
      admin_first_name: 'Admin',
      admin_last_name: 'User',
    });

    expect(apiFetchWithToken).toHaveBeenCalledWith('/auth/register', expect.objectContaining({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    }));
  });

  it('should send all required fields in request body', async () => {
    let authContext;
    apiFetchWithToken.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 1 }),
    });

    renderWithRouter(
      <AuthProvider>
        <TestConsumer onContext={(ctx) => (authContext = ctx)} />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(authContext).toBeDefined();
    });

    const payload = {
      organization_name: 'Empresa Teste LTDA',
      cnpj: '12345678000190',
      address_street: 'Rua das Flores, 123',
      address_city: 'Sao Paulo',
      address_state: 'SP',
      address_country: 'Brasil',
      address_postal_code: '01234567',
      admin_email: 'joao@empresa.com',
      admin_password: 'senha123',
      admin_first_name: 'Joao',
      admin_last_name: 'Silva',
    };

    await authContext.register(payload);

    expect(apiFetchWithToken).toHaveBeenCalledWith('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  });

  it('should return response on success', async () => {
    let authContext;
    const expectedResponse = { id: 1, organization_id: 1 };
    apiFetchWithToken.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(expectedResponse),
    });

    renderWithRouter(
      <AuthProvider>
        <TestConsumer onContext={(ctx) => (authContext = ctx)} />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(authContext).toBeDefined();
    });

    const result = await authContext.register({
      organization_name: 'Empresa',
      cnpj: '12345678000190',
      address_street: 'Rua',
      address_city: 'Cidade',
      address_state: 'SP',
      address_country: 'Brasil',
      address_postal_code: '12345678',
      admin_email: 'admin@test.com',
      admin_password: 'password',
      admin_first_name: 'Admin',
      admin_last_name: 'User',
    });

    expect(result).toEqual(expectedResponse);
  });

  it('should throw error with message on failure', async () => {
    let authContext;
    apiFetchWithToken.mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ detail: 'CNPJ ja cadastrado' }),
    });

    renderWithRouter(
      <AuthProvider>
        <TestConsumer onContext={(ctx) => (authContext = ctx)} />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(authContext).toBeDefined();
    });

    await expect(
      authContext.register({
        organization_name: 'Empresa',
        cnpj: '12345678000190',
        address_street: 'Rua',
        address_city: 'Cidade',
        address_state: 'SP',
        address_country: 'Brasil',
        address_postal_code: '12345678',
        admin_email: 'admin@test.com',
        admin_password: 'password',
        admin_first_name: 'Admin',
        admin_last_name: 'User',
      })
    ).rejects.toThrow('CNPJ ja cadastrado');
  });

  it('should throw default error when response has no detail', async () => {
    let authContext;
    apiFetchWithToken.mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({}),
    });

    renderWithRouter(
      <AuthProvider>
        <TestConsumer onContext={(ctx) => (authContext = ctx)} />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(authContext).toBeDefined();
    });

    await expect(
      authContext.register({
        organization_name: 'Empresa',
        cnpj: '12345678000190',
        address_street: 'Rua',
        address_city: 'Cidade',
        address_state: 'SP',
        address_country: 'Brasil',
        address_postal_code: '12345678',
        admin_email: 'admin@test.com',
        admin_password: 'password',
        admin_first_name: 'Admin',
        admin_last_name: 'User',
      })
    ).rejects.toThrow('Erro ao cadastrar usuario');
  });

  it('should handle validation errors from backend (array format)', async () => {
    let authContext;
    apiFetchWithToken.mockResolvedValue({
      ok: false,
      json: () =>
        Promise.resolve({
          detail: [{ loc: ['body', 'admin_email'], msg: 'Email invalido', type: 'value_error' }],
        }),
    });

    renderWithRouter(
      <AuthProvider>
        <TestConsumer onContext={(ctx) => (authContext = ctx)} />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(authContext).toBeDefined();
    });

    await expect(
      authContext.register({
        organization_name: 'Empresa',
        cnpj: '12345678000190',
        address_street: 'Rua',
        address_city: 'Cidade',
        address_state: 'SP',
        address_country: 'Brasil',
        address_postal_code: '12345678',
        admin_email: 'invalid',
        admin_password: 'password',
        admin_first_name: 'Admin',
        admin_last_name: 'User',
      })
    ).rejects.toThrow('Email invalido');
  });

  it('should handle JSON parse error gracefully', async () => {
    let authContext;
    apiFetchWithToken.mockResolvedValue({
      ok: false,
      json: () => Promise.reject(new Error('Invalid JSON')),
    });

    renderWithRouter(
      <AuthProvider>
        <TestConsumer onContext={(ctx) => (authContext = ctx)} />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(authContext).toBeDefined();
    });

    await expect(
      authContext.register({
        organization_name: 'Empresa',
        cnpj: '12345678000190',
        address_street: 'Rua',
        address_city: 'Cidade',
        address_state: 'SP',
        address_country: 'Brasil',
        address_postal_code: '12345678',
        admin_email: 'admin@test.com',
        admin_password: 'password',
        admin_first_name: 'Admin',
        admin_last_name: 'User',
      })
    ).rejects.toThrow('Erro ao cadastrar usuario');
  });
});
