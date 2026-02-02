import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderWithProviders, screen, userEvent, waitFor, createMockAuth } from './test/utils/test-utils';
import Login from './login';

// Mock react-toastify
vi.mock('react-toastify', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

import { toast } from 'react-toastify';

describe('Login Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render email input', () => {
      renderWithProviders(<Login />);

      expect(screen.getByPlaceholderText('seu@email.com')).toBeInTheDocument();
    });

    it('should render password input', () => {
      renderWithProviders(<Login />);

      expect(screen.getByPlaceholderText('Sua senha')).toBeInTheDocument();
    });

    it('should render submit button', () => {
      renderWithProviders(<Login />);

      expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument();
    });

    it('should render registration link', () => {
      renderWithProviders(<Login />);

      expect(screen.getByText('Criar conta agora')).toBeInTheDocument();
    });

    it('should render branding text', () => {
      renderWithProviders(<Login />);

      expect(screen.getByText('XFireSecurity')).toBeInTheDocument();
    });
  });

  describe('Validation', () => {
    it('should show error toast when form is submitted empty', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Login />);

      await user.click(screen.getByRole('button', { name: /entrar/i }));

      expect(toast.error).toHaveBeenCalledWith('Preencha todos os campos!');
    });

    it('should show error toast when only email is filled', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Login />);

      await user.type(screen.getByPlaceholderText('seu@email.com'), 'test@example.com');
      await user.click(screen.getByRole('button', { name: /entrar/i }));

      expect(toast.error).toHaveBeenCalledWith('Preencha todos os campos!');
    });

    it('should show error toast when only password is filled', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Login />);

      await user.type(screen.getByPlaceholderText('Sua senha'), 'password123');
      await user.click(screen.getByRole('button', { name: /entrar/i }));

      expect(toast.error).toHaveBeenCalledWith('Preencha todos os campos!');
    });
  });

  describe('Submission', () => {
    it('should call login with email and password on submit', async () => {
      const user = userEvent.setup();
      const mockLogin = vi.fn().mockResolvedValue();
      const authValue = createMockAuth({ login: mockLogin });

      renderWithProviders(<Login />, { authValue });

      await user.type(screen.getByPlaceholderText('seu@email.com'), 'test@example.com');
      await user.type(screen.getByPlaceholderText('Sua senha'), 'password123');
      await user.click(screen.getByRole('button', { name: /entrar/i }));

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
      });
    });

    it('should show success toast on successful login', async () => {
      const user = userEvent.setup();
      const mockLogin = vi.fn().mockResolvedValue();
      const authValue = createMockAuth({ login: mockLogin });

      renderWithProviders(<Login />, { authValue });

      await user.type(screen.getByPlaceholderText('seu@email.com'), 'test@example.com');
      await user.type(screen.getByPlaceholderText('Sua senha'), 'password123');
      await user.click(screen.getByRole('button', { name: /entrar/i }));

      await waitFor(() => {
        expect(toast.success).toHaveBeenCalledWith('Login realizado com sucesso!');
      });
    });

    it('should show error toast on failed login', async () => {
      const user = userEvent.setup();
      const mockLogin = vi.fn().mockRejectedValue(new Error('Invalid credentials'));
      const authValue = createMockAuth({ login: mockLogin });

      renderWithProviders(<Login />, { authValue });

      await user.type(screen.getByPlaceholderText('seu@email.com'), 'test@example.com');
      await user.type(screen.getByPlaceholderText('Sua senha'), 'wrongpassword');
      await user.click(screen.getByRole('button', { name: /entrar/i }));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Credenciais invalidas.');
      });
    });
  });

  describe('Loading State', () => {
    it('should disable button while loading', async () => {
      const user = userEvent.setup();
      // Create a login that never resolves to keep loading state
      const mockLogin = vi.fn(() => new Promise(() => {}));
      const authValue = createMockAuth({ login: mockLogin });

      renderWithProviders(<Login />, { authValue });

      await user.type(screen.getByPlaceholderText('seu@email.com'), 'test@example.com');
      await user.type(screen.getByPlaceholderText('Sua senha'), 'password123');
      await user.click(screen.getByRole('button', { name: /entrar/i }));

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /entrando/i })).toBeDisabled();
      });
    });

    it('should show "Entrando..." text while loading', async () => {
      const user = userEvent.setup();
      const mockLogin = vi.fn(() => new Promise(() => {}));
      const authValue = createMockAuth({ login: mockLogin });

      renderWithProviders(<Login />, { authValue });

      await user.type(screen.getByPlaceholderText('seu@email.com'), 'test@example.com');
      await user.type(screen.getByPlaceholderText('Sua senha'), 'password123');
      await user.click(screen.getByRole('button', { name: /entrar/i }));

      await waitFor(() => {
        expect(screen.getByText('Entrando...')).toBeInTheDocument();
      });
    });

    it('should re-enable button after completion', async () => {
      const user = userEvent.setup();
      const mockLogin = vi.fn().mockResolvedValue();
      const authValue = createMockAuth({ login: mockLogin });

      renderWithProviders(<Login />, { authValue });

      await user.type(screen.getByPlaceholderText('seu@email.com'), 'test@example.com');
      await user.type(screen.getByPlaceholderText('Sua senha'), 'password123');
      await user.click(screen.getByRole('button', { name: /entrar/i }));

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /entrar/i })).not.toBeDisabled();
      });
    });
  });

  describe('Input Handling', () => {
    it('should update email state on input change', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Login />);

      const emailInput = screen.getByPlaceholderText('seu@email.com');
      await user.type(emailInput, 'user@test.com');

      expect(emailInput).toHaveValue('user@test.com');
    });

    it('should update password state on input change', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Login />);

      const passwordInput = screen.getByPlaceholderText('Sua senha');
      await user.type(passwordInput, 'secretpass');

      expect(passwordInput).toHaveValue('secretpass');
    });

    it('should have correct input types', () => {
      renderWithProviders(<Login />);

      expect(screen.getByPlaceholderText('seu@email.com')).toHaveAttribute('type', 'email');
      expect(screen.getByPlaceholderText('Sua senha')).toHaveAttribute('type', 'password');
    });
  });
});
