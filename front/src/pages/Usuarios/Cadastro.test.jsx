import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderWithProviders, screen, userEvent, waitFor, createMockAuth } from '../../test/utils/test-utils';
import Cadastro from './Cadastro';

// Mock react-toastify
vi.mock('react-toastify', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

// Mock react-imask
vi.mock('react-imask', () => ({
  IMaskInput: ({ mask, value, onAccept, placeholder, className, ...props }) => (
    <input
      data-testid={`imask-${placeholder?.replace(/[^a-zA-Z0-9]/g, '')}`}
      value={value}
      onChange={(e) => {
        // Simulate mask formatting
        let newValue = e.target.value;
        if (mask === '00.000.000/0000-00') {
          // CNPJ mask simulation
          const digits = newValue.replace(/\D/g, '').slice(0, 14);
          if (digits.length <= 2) newValue = digits;
          else if (digits.length <= 5) newValue = `${digits.slice(0, 2)}.${digits.slice(2)}`;
          else if (digits.length <= 8) newValue = `${digits.slice(0, 2)}.${digits.slice(2, 5)}.${digits.slice(5)}`;
          else if (digits.length <= 12) newValue = `${digits.slice(0, 2)}.${digits.slice(2, 5)}.${digits.slice(5, 8)}/${digits.slice(8)}`;
          else newValue = `${digits.slice(0, 2)}.${digits.slice(2, 5)}.${digits.slice(5, 8)}/${digits.slice(8, 12)}-${digits.slice(12)}`;
        } else if (mask === '00000-000') {
          // CEP mask simulation
          const digits = newValue.replace(/\D/g, '').slice(0, 8);
          if (digits.length <= 5) newValue = digits;
          else newValue = `${digits.slice(0, 5)}-${digits.slice(5)}`;
        }
        onAccept?.(newValue);
      }}
      placeholder={placeholder}
      className={className}
      {...props}
    />
  ),
}));

import { toast } from 'react-toastify';

// Helper to get the step navigation back button (not the "Voltar para login" link)
const getBackButton = () => {
  const buttons = screen.getAllByRole('button', { name: /voltar/i });
  // The step back button has "Voltar" text only, not "Voltar para login"
  return buttons.find(btn => btn.textContent?.trim() === 'Voltar');
};

describe('Cadastro Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render step 1 (Dados da Empresa) by default', () => {
      renderWithProviders(<Cadastro />);

      expect(screen.getByPlaceholderText('Nome da empresa')).toBeInTheDocument();
    });

    it('should show progress indicators for 4 steps', () => {
      renderWithProviders(<Cadastro />);

      expect(screen.getByText('Dados da Empresa')).toBeInTheDocument();
      expect(screen.getByText('Endereco')).toBeInTheDocument();
      expect(screen.getByText('Administrador')).toBeInTheDocument();
      expect(screen.getByText('Senha')).toBeInTheDocument();
    });

    it('should display organization name and CNPJ inputs on step 1', () => {
      renderWithProviders(<Cadastro />);

      expect(screen.getByPlaceholderText('Nome da empresa')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('00.000.000/0000-00')).toBeInTheDocument();
    });

    it('should render header with title and description', () => {
      renderWithProviders(<Cadastro />);

      expect(screen.getByText('Criar sua conta')).toBeInTheDocument();
      expect(screen.getByText(/Preencha seus dados em 4 etapas simples/)).toBeInTheDocument();
    });

    it('should render login link', () => {
      renderWithProviders(<Cadastro />);

      expect(screen.getByText('Voltar para login')).toBeInTheDocument();
    });
  });

  describe('Step Navigation', () => {
    it('should advance from step 1 to step 2 with valid data', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await user.type(screen.getByPlaceholderText('Nome da empresa'), 'Empresa Teste LTDA');
      await user.type(screen.getByPlaceholderText('00.000.000/0000-00'), '12345678000190');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Endereco completo')).toBeInTheDocument();
      });
    });

    it('should advance from step 2 to step 3 with valid data', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      // Fill step 1
      await user.type(screen.getByPlaceholderText('Nome da empresa'), 'Empresa Teste LTDA');
      await user.type(screen.getByPlaceholderText('00.000.000/0000-00'), '12345678000190');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      // Fill step 2
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Endereco completo')).toBeInTheDocument();
      });

      await user.type(screen.getByPlaceholderText('Endereco completo'), 'Rua das Flores, 123');
      await user.type(screen.getByPlaceholderText('Cidade'), 'Sao Paulo');
      await user.selectOptions(screen.getByRole('combobox'), 'SP');
      await user.type(screen.getByPlaceholderText('00000-000'), '01234567');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Primeiro nome')).toBeInTheDocument();
      });
    }, 10000);

    it('should advance from step 3 to step 4 with valid data', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      // Fill step 1
      await user.type(screen.getByPlaceholderText('Nome da empresa'), 'Empresa Teste LTDA');
      await user.type(screen.getByPlaceholderText('00.000.000/0000-00'), '12345678000190');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      // Fill step 2
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Endereco completo')).toBeInTheDocument();
      });
      await user.type(screen.getByPlaceholderText('Endereco completo'), 'Rua das Flores, 123');
      await user.type(screen.getByPlaceholderText('Cidade'), 'Sao Paulo');
      await user.selectOptions(screen.getByRole('combobox'), 'SP');
      await user.type(screen.getByPlaceholderText('00000-000'), '01234567');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      // Fill step 3
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Primeiro nome')).toBeInTheDocument();
      });
      await user.type(screen.getByPlaceholderText('Primeiro nome'), 'Joao');
      await user.type(screen.getByPlaceholderText('Sobrenome'), 'Silva');
      await user.type(screen.getByPlaceholderText('seu@email.com'), 'joao@empresa.com');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Crie uma senha forte')).toBeInTheDocument();
      });
    }, 15000);

    it('should go back from step 2 to step 1', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      // Go to step 2
      await user.type(screen.getByPlaceholderText('Nome da empresa'), 'Empresa Teste');
      await user.type(screen.getByPlaceholderText('00.000.000/0000-00'), '12345678000190');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Endereco completo')).toBeInTheDocument();
      });

      // Go back to step 1 - use the step navigation button, not the login link
      const backButton = getBackButton();
      expect(backButton).toBeTruthy();
      await user.click(backButton);

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Nome da empresa')).toBeInTheDocument();
      });
    });

    it('should go back from step 3 to step 2', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      // Go to step 3
      await user.type(screen.getByPlaceholderText('Nome da empresa'), 'Empresa Teste');
      await user.type(screen.getByPlaceholderText('00.000.000/0000-00'), '12345678000190');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Endereco completo')).toBeInTheDocument();
      });
      await user.type(screen.getByPlaceholderText('Endereco completo'), 'Rua das Flores, 123');
      await user.type(screen.getByPlaceholderText('Cidade'), 'Sao Paulo');
      await user.selectOptions(screen.getByRole('combobox'), 'SP');
      await user.type(screen.getByPlaceholderText('00000-000'), '01234567');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Primeiro nome')).toBeInTheDocument();
      });

      // Go back to step 2
      const backButton = getBackButton();
      expect(backButton).toBeTruthy();
      await user.click(backButton);

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Endereco completo')).toBeInTheDocument();
      });
    });

    it('should go back from step 4 to step 3', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      // Navigate to step 4
      await user.type(screen.getByPlaceholderText('Nome da empresa'), 'Empresa Teste');
      await user.type(screen.getByPlaceholderText('00.000.000/0000-00'), '12345678000190');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Endereco completo')).toBeInTheDocument();
      });
      await user.type(screen.getByPlaceholderText('Endereco completo'), 'Rua das Flores, 123');
      await user.type(screen.getByPlaceholderText('Cidade'), 'Sao Paulo');
      await user.selectOptions(screen.getByRole('combobox'), 'SP');
      await user.type(screen.getByPlaceholderText('00000-000'), '01234567');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Primeiro nome')).toBeInTheDocument();
      });
      await user.type(screen.getByPlaceholderText('Primeiro nome'), 'Joao');
      await user.type(screen.getByPlaceholderText('Sobrenome'), 'Silva');
      await user.type(screen.getByPlaceholderText('seu@email.com'), 'joao@empresa.com');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Crie uma senha forte')).toBeInTheDocument();
      });

      // Go back to step 3
      const backButton = getBackButton();
      expect(backButton).toBeTruthy();
      await user.click(backButton);

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Primeiro nome')).toBeInTheDocument();
      });
    });
  });

  describe('Step 1 Validation', () => {
    it('should show error when organization name is empty and CNPJ is filled', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      // Fill CNPJ but not organization name, then try to submit
      // Note: HTML5 validation will trigger first, so we test toast.error being called
      // after filling required fields but with invalid data per our validation rules
      await user.type(screen.getByPlaceholderText('Nome da empresa'), ' ');
      await user.clear(screen.getByPlaceholderText('Nome da empresa'));
      await user.type(screen.getByPlaceholderText('Nome da empresa'), '   '); // whitespace only
      await user.type(screen.getByPlaceholderText('00.000.000/0000-00'), '12345678000190');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Digite o nome da empresa!');
      });
    });

    it('should show error when CNPJ has less than 14 digits', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await user.type(screen.getByPlaceholderText('Nome da empresa'), 'Empresa Teste');
      await user.type(screen.getByPlaceholderText('00.000.000/0000-00'), '123456');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('CNPJ deve ter 14 digitos!');
      });
    });
  });

  describe('Step 2 Validation', () => {
    async function goToStep2(user) {
      await user.type(screen.getByPlaceholderText('Nome da empresa'), 'Empresa Teste');
      await user.type(screen.getByPlaceholderText('00.000.000/0000-00'), '12345678000190');
      await user.click(screen.getByRole('button', { name: /proximo/i }));
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Endereco completo')).toBeInTheDocument();
      });
    }

    it('should show error when address street is too short', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await goToStep2(user);
      await user.type(screen.getByPlaceholderText('Endereco completo'), 'ab');
      await user.type(screen.getByPlaceholderText('Cidade'), 'Sao Paulo');
      await user.selectOptions(screen.getByRole('combobox'), 'SP');
      await user.type(screen.getByPlaceholderText('00000-000'), '01234567');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Digite o endereco completo (minimo 3 caracteres)!');
      });
    });

    it('should show error when city is too short', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await goToStep2(user);
      await user.type(screen.getByPlaceholderText('Endereco completo'), 'Rua das Flores, 123');
      await user.type(screen.getByPlaceholderText('Cidade'), 'S');
      await user.selectOptions(screen.getByRole('combobox'), 'SP');
      await user.type(screen.getByPlaceholderText('00000-000'), '01234567');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Digite a cidade (minimo 2 caracteres)!');
      });
    });

    it('should require state selection (form has required attribute on select)', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await goToStep2(user);

      // Verify the select element has required attribute
      const stateSelect = screen.getByRole('combobox');
      expect(stateSelect).toHaveAttribute('required');

      // Verify default value is empty
      expect(stateSelect).toHaveValue('');
    }, 10000);

    it('should show error when CEP has less than 8 digits', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await goToStep2(user);
      await user.type(screen.getByPlaceholderText('Endereco completo'), 'Rua das Flores, 123');
      await user.type(screen.getByPlaceholderText('Cidade'), 'Sao Paulo');
      await user.selectOptions(screen.getByRole('combobox'), 'SP');
      await user.type(screen.getByPlaceholderText('00000-000'), '01234');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('CEP deve ter 8 digitos!');
      });
    });

    it('should have country field defaulting to Brasil', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await goToStep2(user);

      const countryInput = screen.getByDisplayValue('Brasil');
      expect(countryInput).toBeInTheDocument();
      expect(countryInput).toHaveAttribute('readOnly');
    });
  });

  describe('Step 3 Validation', () => {
    async function goToStep3(user) {
      await user.type(screen.getByPlaceholderText('Nome da empresa'), 'Empresa Teste');
      await user.type(screen.getByPlaceholderText('00.000.000/0000-00'), '12345678000190');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Endereco completo')).toBeInTheDocument();
      });
      await user.type(screen.getByPlaceholderText('Endereco completo'), 'Rua das Flores, 123');
      await user.type(screen.getByPlaceholderText('Cidade'), 'Sao Paulo');
      await user.selectOptions(screen.getByRole('combobox'), 'SP');
      await user.type(screen.getByPlaceholderText('00000-000'), '01234567');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Primeiro nome')).toBeInTheDocument();
      });
    }

    it('should have first name input with required attribute', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await goToStep3(user);

      const firstNameInput = screen.getByPlaceholderText('Primeiro nome');
      expect(firstNameInput).toHaveAttribute('required');
    }, 15000);

    it('should have last name input with required attribute', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await goToStep3(user);

      const lastNameInput = screen.getByPlaceholderText('Sobrenome');
      expect(lastNameInput).toHaveAttribute('required');
    }, 15000);

    it('should have email input with type email and required attribute', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await goToStep3(user);

      // Verify the email input has type email (validates format) and required
      const emailInput = screen.getByPlaceholderText('seu@email.com');
      expect(emailInput).toHaveAttribute('required');
      expect(emailInput).toHaveAttribute('type', 'email');
    }, 15000);

    it('should allow valid email and advance to next step', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await goToStep3(user);
      await user.type(screen.getByPlaceholderText('Primeiro nome'), 'Joao');
      await user.type(screen.getByPlaceholderText('Sobrenome'), 'Silva');
      await user.type(screen.getByPlaceholderText('seu@email.com'), 'joao@empresa.com');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      // Should advance to step 4
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Crie uma senha forte')).toBeInTheDocument();
      });
    }, 20000);
  });

  describe('Step 4 Validation', () => {
    async function goToStep4(user) {
      await user.type(screen.getByPlaceholderText('Nome da empresa'), 'Empresa Teste');
      await user.type(screen.getByPlaceholderText('00.000.000/0000-00'), '12345678000190');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Endereco completo')).toBeInTheDocument();
      });
      await user.type(screen.getByPlaceholderText('Endereco completo'), 'Rua das Flores, 123');
      await user.type(screen.getByPlaceholderText('Cidade'), 'Sao Paulo');
      await user.selectOptions(screen.getByRole('combobox'), 'SP');
      await user.type(screen.getByPlaceholderText('00000-000'), '01234567');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Primeiro nome')).toBeInTheDocument();
      });
      await user.type(screen.getByPlaceholderText('Primeiro nome'), 'Joao');
      await user.type(screen.getByPlaceholderText('Sobrenome'), 'Silva');
      await user.type(screen.getByPlaceholderText('seu@email.com'), 'joao@empresa.com');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Crie uma senha forte')).toBeInTheDocument();
      });
    }

    it('should require password fields (form has required attributes)', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await goToStep4(user);

      // Verify the password inputs have required attributes
      const passwordInput = screen.getByPlaceholderText('Crie uma senha forte');
      const confirmInput = screen.getByPlaceholderText('Confirme sua senha');

      expect(passwordInput).toHaveAttribute('required');
      expect(confirmInput).toHaveAttribute('required');
      expect(passwordInput).toHaveAttribute('type', 'password');
      expect(confirmInput).toHaveAttribute('type', 'password');
    }, 20000);

    it('should show error when passwords do not match', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await goToStep4(user);
      await user.type(screen.getByPlaceholderText('Crie uma senha forte'), 'senha123');
      await user.type(screen.getByPlaceholderText('Confirme sua senha'), 'senha456');
      await user.click(screen.getByRole('button', { name: /criar conta/i }));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('As senhas nao coincidem!');
      });
    }, 20000);

    it('should show error when password is less than 6 characters', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await goToStep4(user);
      await user.type(screen.getByPlaceholderText('Crie uma senha forte'), '12345');
      await user.type(screen.getByPlaceholderText('Confirme sua senha'), '12345');
      await user.click(screen.getByRole('button', { name: /criar conta/i }));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('A senha deve ter pelo menos 6 caracteres!');
      });
    }, 20000);

    it('should show password strength indicator when password is typed', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await goToStep4(user);
      await user.type(screen.getByPlaceholderText('Crie uma senha forte'), '123');

      expect(screen.getByText('Fraca')).toBeInTheDocument();
    }, 20000);

    it('should show medium strength for password with 6-9 characters', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await goToStep4(user);
      await user.type(screen.getByPlaceholderText('Crie uma senha forte'), 'senha12');

      expect(screen.getByText('Media')).toBeInTheDocument();
    }, 20000);

    it('should show strong strength for password with 10+ characters', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      await goToStep4(user);
      await user.type(screen.getByPlaceholderText('Crie uma senha forte'), 'senhaforte123');

      expect(screen.getByText('Forte')).toBeInTheDocument();
    }, 20000);
  });

  describe('Form Submission', () => {
    async function fillAllSteps(user) {
      // Step 1
      await user.type(screen.getByPlaceholderText('Nome da empresa'), 'Empresa Teste LTDA');
      await user.type(screen.getByPlaceholderText('00.000.000/0000-00'), '12345678000190');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      // Step 2
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Endereco completo')).toBeInTheDocument();
      });
      await user.type(screen.getByPlaceholderText('Endereco completo'), 'Rua das Flores, 123');
      await user.type(screen.getByPlaceholderText('Cidade'), 'Sao Paulo');
      await user.selectOptions(screen.getByRole('combobox'), 'SP');
      await user.type(screen.getByPlaceholderText('00000-000'), '01234567');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      // Step 3
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Primeiro nome')).toBeInTheDocument();
      });
      await user.type(screen.getByPlaceholderText('Primeiro nome'), 'Joao');
      await user.type(screen.getByPlaceholderText('Sobrenome'), 'Silva');
      await user.type(screen.getByPlaceholderText('seu@email.com'), 'joao@empresa.com');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      // Step 4
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Crie uma senha forte')).toBeInTheDocument();
      });
      await user.type(screen.getByPlaceholderText('Crie uma senha forte'), 'senha123');
      await user.type(screen.getByPlaceholderText('Confirme sua senha'), 'senha123');
    }

    it('should call register with correct payload on successful submission', async () => {
      const user = userEvent.setup();
      const mockRegister = vi.fn().mockResolvedValue({});
      const authValue = createMockAuth({ register: mockRegister });

      renderWithProviders(<Cadastro />, { authValue });

      await fillAllSteps(user);
      await user.click(screen.getByRole('button', { name: /criar conta/i }));

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
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
        });
      });
    }, 25000);

    it('should show success toast on successful registration', async () => {
      const user = userEvent.setup();
      const mockRegister = vi.fn().mockResolvedValue({});
      const authValue = createMockAuth({ register: mockRegister });

      renderWithProviders(<Cadastro />, { authValue });

      await fillAllSteps(user);
      await user.click(screen.getByRole('button', { name: /criar conta/i }));

      await waitFor(() => {
        expect(toast.success).toHaveBeenCalledWith('Cadastro realizado com sucesso! Faca login para continuar.');
      });
    }, 25000);

    it('should show error toast on registration failure', async () => {
      const user = userEvent.setup();
      const mockRegister = vi.fn().mockRejectedValue(new Error('CNPJ ja cadastrado'));
      const authValue = createMockAuth({ register: mockRegister });

      renderWithProviders(<Cadastro />, { authValue });

      await fillAllSteps(user);
      await user.click(screen.getByRole('button', { name: /criar conta/i }));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('CNPJ ja cadastrado');
      });
    }, 25000);

    it('should show generic error toast when registration fails without message', async () => {
      const user = userEvent.setup();
      const mockRegister = vi.fn().mockRejectedValue(new Error());
      const authValue = createMockAuth({ register: mockRegister });

      renderWithProviders(<Cadastro />, { authValue });

      await fillAllSteps(user);
      await user.click(screen.getByRole('button', { name: /criar conta/i }));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Erro ao cadastrar');
      });
    }, 25000);

    it('should disable submit button while loading', async () => {
      const user = userEvent.setup();
      const mockRegister = vi.fn(() => new Promise(() => {})); // Never resolves
      const authValue = createMockAuth({ register: mockRegister });

      renderWithProviders(<Cadastro />, { authValue });

      await fillAllSteps(user);
      await user.click(screen.getByRole('button', { name: /criar conta/i }));

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /criando conta/i })).toBeDisabled();
      });
    }, 25000);

    it('should show "Criando conta..." text while loading', async () => {
      const user = userEvent.setup();
      const mockRegister = vi.fn(() => new Promise(() => {})); // Never resolves
      const authValue = createMockAuth({ register: mockRegister });

      renderWithProviders(<Cadastro />, { authValue });

      await fillAllSteps(user);
      await user.click(screen.getByRole('button', { name: /criar conta/i }));

      await waitFor(() => {
        expect(screen.getByText('Criando conta...')).toBeInTheDocument();
      });
    }, 25000);
  });

  describe('Input Handling', () => {
    it('should update organization name on input', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      const input = screen.getByPlaceholderText('Nome da empresa');
      await user.type(input, 'Minha Empresa');

      expect(input).toHaveValue('Minha Empresa');
    });

    it('should format CNPJ with mask on input', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      const cnpjInput = screen.getByPlaceholderText('00.000.000/0000-00');
      await user.type(cnpjInput, '12345678000190');

      expect(cnpjInput).toHaveValue('12.345.678/0001-90');
    });

    it('should format CEP with mask on input', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      // Go to step 2 first
      await user.type(screen.getByPlaceholderText('Nome da empresa'), 'Empresa Teste');
      await user.type(screen.getByPlaceholderText('00.000.000/0000-00'), '12345678000190');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('00000-000')).toBeInTheDocument();
      });

      const cepInput = screen.getByPlaceholderText('00000-000');
      await user.type(cepInput, '01234567');

      expect(cepInput).toHaveValue('01234-567');
    });

    it('should update all text fields correctly', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      // Step 1 - Organization name
      const orgInput = screen.getByPlaceholderText('Nome da empresa');
      await user.type(orgInput, 'Empresa ABC');
      expect(orgInput).toHaveValue('Empresa ABC');

      // Go to step 2
      await user.type(screen.getByPlaceholderText('00.000.000/0000-00'), '12345678000190');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Endereco completo')).toBeInTheDocument();
      });

      // Step 2 - Address fields
      const streetInput = screen.getByPlaceholderText('Endereco completo');
      await user.type(streetInput, 'Rua Teste, 100');
      expect(streetInput).toHaveValue('Rua Teste, 100');

      const cityInput = screen.getByPlaceholderText('Cidade');
      await user.type(cityInput, 'Rio de Janeiro');
      expect(cityInput).toHaveValue('Rio de Janeiro');

      // Go to step 3
      await user.selectOptions(screen.getByRole('combobox'), 'RJ');
      await user.type(screen.getByPlaceholderText('00000-000'), '20000000');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Primeiro nome')).toBeInTheDocument();
      });

      // Step 3 - Admin fields
      const firstNameInput = screen.getByPlaceholderText('Primeiro nome');
      await user.type(firstNameInput, 'Maria');
      expect(firstNameInput).toHaveValue('Maria');

      const lastNameInput = screen.getByPlaceholderText('Sobrenome');
      await user.type(lastNameInput, 'Santos');
      expect(lastNameInput).toHaveValue('Santos');

      const emailInput = screen.getByPlaceholderText('seu@email.com');
      await user.type(emailInput, 'maria@teste.com');
      expect(emailInput).toHaveValue('maria@teste.com');
    }, 15000);
  });

  describe('Step 4 Submit Button', () => {
    it('should show "Criar conta" button on step 4', async () => {
      const user = userEvent.setup();
      renderWithProviders(<Cadastro />);

      // Navigate to step 4
      await user.type(screen.getByPlaceholderText('Nome da empresa'), 'Empresa Teste');
      await user.type(screen.getByPlaceholderText('00.000.000/0000-00'), '12345678000190');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Endereco completo')).toBeInTheDocument();
      });
      await user.type(screen.getByPlaceholderText('Endereco completo'), 'Rua das Flores, 123');
      await user.type(screen.getByPlaceholderText('Cidade'), 'Sao Paulo');
      await user.selectOptions(screen.getByRole('combobox'), 'SP');
      await user.type(screen.getByPlaceholderText('00000-000'), '01234567');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Primeiro nome')).toBeInTheDocument();
      });
      await user.type(screen.getByPlaceholderText('Primeiro nome'), 'Joao');
      await user.type(screen.getByPlaceholderText('Sobrenome'), 'Silva');
      await user.type(screen.getByPlaceholderText('seu@email.com'), 'joao@empresa.com');
      await user.click(screen.getByRole('button', { name: /proximo/i }));

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /criar conta/i })).toBeInTheDocument();
      });
    }, 20000);
  });
});
