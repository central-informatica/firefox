import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import {
  FiUploadCloud,
  FiLock,
  FiBriefcase,
  FiFile,
  FiX,
  FiCheck,
  FiArrowLeft,
  FiShield,
  FiAlertCircle
} from "react-icons/fi";

import Input from "../../components/Input/Input";
import SelectCustom from "../../components/Select/Select";
import Label from "../../components/Label/Label";

import { useAuth } from "../../auth/useAuth";
import { getEmpresasDoUsuario } from "../../services/empresasService";
import { createCertificado } from "../../services/certificadosService";

export default function CertificadosForm() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const fileInputRef = useRef(null);

  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [form, setForm] = useState({
    senha: "",
    empresa_id: null,
    proprietario: "",
    emitido_por: "",
    validade_inicio: "",
    valido_ate: "",
  });

  const [empresas, setEmpresas] = useState([]);
  const [empresaSelecionada, setEmpresaSelecionada] = useState(null);

  useEffect(() => {
    if (!user) return;

    getEmpresasDoUsuario(user.id).then((lista) => {
      const opcoes = lista.map((e) => ({
        value: e.empresa_id,
        label: e.razao_social,
      }));

      setEmpresas(opcoes);

      if (opcoes.length > 0) {
        setEmpresaSelecionada(opcoes[0]);
        setForm((f) => ({ ...f, empresa_id: opcoes[0].value }));
      }
    });
  }, [user]);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      const selectedFile = files[0];
      if (selectedFile.name.endsWith('.pfx') || selectedFile.name.endsWith('.p12')) {
        setFile(selectedFile);
      } else {
        toast.error("Por favor, selecione um arquivo .pfx ou .p12");
      }
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      toast.error("Selecione um arquivo PFX.");
      return;
    }

    if (!form.empresa_id) {
      toast.error("Selecione uma empresa.");
      return;
    }

    setIsSubmitting(true);

    const data = new FormData();
    data.append("empresa_id", form.empresa_id);
    data.append("senha", form.senha || "");
    data.append("arquivo", file);

    try {
      await createCertificado(data);
      toast.success("Certificado enviado com sucesso!");
      navigate("/certificados");
    } catch (err) {
      console.error(err);
      toast.error("Erro ao enviar certificado.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4 animate-fadeIn">
      <div className="max-w-3xl mx-auto">
        {/* Header com botão de voltar */}
        <div className="mb-6 flex items-center gap-4">
          <button
            onClick={() => navigate("/certificados")}
            className="p-2 hover:bg-white rounded-lg transition-all duration-200 text-gray-600 hover:text-emerald-600 hover:shadow-md group"
          >
            <FiArrowLeft size={24} className="group-hover:-translate-x-1 transition-transform duration-200" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl shadow-lg">
                <FiShield className="text-white" size={28} />
              </div>
              Novo Certificado Digital
            </h1>
            <p className="text-gray-600 mt-1">Faça upload do seu certificado .pfx de forma segura</p>
          </div>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden animate-slideUp">
          <form onSubmit={handleSubmit} className="p-8 space-y-6">
            {/* Empresa */}
            <div className="space-y-2">
              <Label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                <FiBriefcase className="text-emerald-600" size={18} />
                Empresa
              </Label>
              <SelectCustom
                options={empresas}
                value={empresaSelecionada}
                onChange={(opt) => {
                  setEmpresaSelecionada(opt);
                  setForm((f) => ({ ...f, empresa_id: opt.value }));
                }}
              />
            </div>

            {/* Upload Area */}
            <div className="space-y-2">
              <Label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                <FiUploadCloud className="text-emerald-600" size={18} />
                Certificado Digital (.pfx ou .p12)
              </Label>

              {!file ? (
                <div
                  onDragEnter={handleDragEnter}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`
                    relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
                    transition-all duration-300 group
                    ${isDragging
                      ? 'border-emerald-500 bg-emerald-50 scale-105'
                      : 'border-gray-300 hover:border-emerald-400 hover:bg-emerald-50/50'
                    }
                  `}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pfx,.p12"
                    onChange={handleFileSelect}
                    className="hidden"
                  />

                  <div className={`
                    transition-all duration-300
                    ${isDragging ? 'scale-110' : 'group-hover:scale-105'}
                  `}>
                    <div className="mx-auto w-16 h-16 bg-gradient-to-br from-emerald-100 to-emerald-200 rounded-full flex items-center justify-center mb-4 group-hover:shadow-lg transition-shadow duration-300">
                      <FiUploadCloud className="text-emerald-600" size={32} />
                    </div>

                    <p className="text-lg font-semibold text-gray-700 mb-2">
                      {isDragging ? 'Solte o arquivo aqui' : 'Arraste seu certificado ou clique para selecionar'}
                    </p>
                    <p className="text-sm text-gray-500">
                      Formatos aceitos: .pfx, .p12 • Máx. 10MB
                    </p>
                  </div>

                  {/* Animated border effect */}
                  <div className={`
                    absolute inset-0 rounded-xl transition-opacity duration-300
                    ${isDragging ? 'opacity-100' : 'opacity-0'}
                    bg-gradient-to-r from-emerald-500/10 via-emerald-600/10 to-emerald-500/10
                    animate-pulse
                  `}></div>
                </div>
              ) : (
                <div className="border-2 border-emerald-200 bg-gradient-to-br from-emerald-50 to-emerald-100/50 rounded-xl p-6 animate-slideUp">
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">
                      <div className="w-14 h-14 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg">
                        <FiFile className="text-white" size={24} />
                      </div>
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <p className="font-semibold text-gray-800 truncate">{file.name}</p>
                          <p className="text-sm text-gray-600 mt-1">
                            {(file.size / 1024).toFixed(2)} KB
                          </p>
                        </div>

                        <button
                          type="button"
                          onClick={handleRemoveFile}
                          className="flex-shrink-0 p-2 hover:bg-red-100 rounded-lg transition-all duration-200 text-red-600 group"
                          title="Remover arquivo"
                        >
                          <FiX size={20} className="group-hover:rotate-90 transition-transform duration-200" />
                        </button>
                      </div>

                      <div className="mt-3 flex items-center gap-2">
                        <div className="flex-1 h-2 bg-emerald-200 rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-full w-full animate-slideInLeft"></div>
                        </div>
                        <FiCheck className="text-emerald-600 flex-shrink-0" size={16} />
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Senha */}
            <div className="space-y-2">
              <Label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                <FiLock className="text-emerald-600" size={18} />
                Senha do Certificado
              </Label>
              <Input
                name="senha"
                type="password"
                placeholder="Digite a senha do certificado (se houver)"
                value={form.senha}
                onChange={(e) => setForm({ ...form, senha: e.target.value })}
                className="transition-all duration-200 focus:ring-2 focus:ring-emerald-500"
              />
              <p className="text-xs text-gray-500 flex items-center gap-1.5">
                <FiAlertCircle size={12} />
                A senha será criptografada e armazenada de forma segura
              </p>
            </div>

            {/* Info Banner */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4">
              <div className="flex gap-3">
                <FiAlertCircle className="text-blue-600 flex-shrink-0 mt-0.5" size={20} />
                <div>
                  <p className="text-sm font-medium text-blue-900 mb-1">Informações importantes:</p>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• O certificado será criptografado com AES-256-GCM</li>
                    <li>• Apenas membros autorizados poderão acessar</li>
                    <li>• Mantenha a senha em local seguro</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Botões */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={() => navigate("/certificados")}
                className="flex-1 px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl transition-all duration-200 hover:shadow-md"
                disabled={isSubmitting}
              >
                Cancelar
              </button>

              <button
                type="submit"
                disabled={!file || isSubmitting}
                className={`
                  flex-1 px-6 py-3 font-semibold rounded-xl transition-all duration-300 transform
                  flex items-center justify-center gap-2
                  ${!file || isSubmitting
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 hover:-translate-y-0.5 active:translate-y-0'
                  }
                `}
              >
                {isSubmitting ? (
                  <>
                    <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Enviando...
                  </>
                ) : (
                  <>
                    <FiUploadCloud size={20} />
                    Enviar Certificado
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
