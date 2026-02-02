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
import SelectCustom from "../../components/Select/SelectEmpresa";
import Label from "../../components/Label/Label";

import { useAuth } from "../../auth/useAuth";
import { createCertificado } from "../../services/certificadosService";

export default function CertificadosForm() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const fileInputRef = useRef(null);

  // Support multiple files
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [empresaId, setEmpresaId] = useState(null);
  const [autoCreateEmpresa, setAutoCreateEmpresa] = useState(false);

  // Track uploads that failed specifically due to password or cnpj issues
  const [failedUploads, setFailedUploads] = useState([]); // [{ file, error, password, cnpj }]

  const isPasswordError = (msg = "") => /senha/i.test(msg);
  const isCnpjError = (msg = "") => /cnpj/i.test(msg);

  const retrySingle = async (index) => {
    const entry = failedUploads[index];
    if (!entry) return;
    setIsSubmitting(true);
    try {
      const data = new FormData();
      if (!autoCreateEmpresa && form.empresa_id) data.append("empresa_id", form.empresa_id);
      data.append("senha", entry.password || "");
      if (entry.cnpj) data.append("manual_cnpj", entry.cnpj);
      if (autoCreateEmpresa || entry.cnpj) data.append("auto_create_empresa", "true");
      data.append("arquivo", entry.file);
      await createCertificado(data);

      // remove from failedUploads
      setFailedUploads((prev) => prev.filter((_, i) => i !== index));
      toast.success(`Arquivo ${entry.file.name} enviado com sucesso!`);

      // if no more failed uploads and there were successes earlier, navigate
      if (files.length > 0 && failedUploads.length <= 1) {
        navigate("/certificados");
      }
    } catch (err) {
      const msg = err?.message || String(err);
      setFailedUploads((prev) => prev.map((f, i) => i === index ? { ...f, error: msg } : f));
      toast.error(`Falha: ${msg}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const retryAllFailed = async () => {
    if (!failedUploads.length) return;
    setIsSubmitting(true);
    const promises = failedUploads.map((entry) => {
      const data = new FormData();
      if (!autoCreateEmpresa && form.empresa_id) data.append("empresa_id", form.empresa_id);
      data.append("senha", entry.password || "");
      if (entry.cnpj) data.append("manual_cnpj", entry.cnpj);
      if (autoCreateEmpresa || entry.cnpj) data.append("auto_create_empresa", "true");
      data.append("arquivo", entry.file);
      return createCertificado(data);
    });

    const results = await Promise.allSettled(promises);
    const newFailed = [];
    results.forEach((r, i) => {
      if (r.status === "rejected") {
        newFailed.push({ ...failedUploads[i], error: (r.reason?.message || String(r.reason)) });
      }
    });

    setFailedUploads(newFailed);

    const successes = results.filter((r) => r.status === "fulfilled").length;
    if (successes) toast.success(`${successes} certificado(s) reenviados com sucesso!`);
    if (newFailed.length) toast.error(`${newFailed.length} falha(s) persistem.`);
    if (successes > 0 && newFailed.length === 0) navigate("/certificados");
    setIsSubmitting(false);
  };

  const [form, setForm] = useState({
    senha: "",
    empresa_id: null,
    proprietario: "",
    emitido_por: "",
    validade_inicio: "",
    valido_ate: "",
  });

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

    const dropped = Array.from(e.dataTransfer.files || []);
    const accepted = [];
    const rejected = [];

    dropped.forEach((f) => {
      const name = f.name.toLowerCase();
      if ((name.endsWith('.pfx') || name.endsWith('.p12')) && f.size <= 10 * 1024 * 1024) {
        accepted.push(f);
      } else {
        rejected.push(f.name);
      }
    });

    if (rejected.length) {
      toast.error(`Arquivos rejeitados: ${rejected.join(', ')} (somente .pfx/.p12 e <=10MB)`);
    }

    if (accepted.length) {
      setFiles((prev) => [...prev, ...accepted]);
    }
  };

  const handleFileSelect = (e) => {
    const selected = Array.from(e.target.files || []);
    const accepted = [];
    const rejected = [];

    selected.forEach((f) => {
      const name = f.name.toLowerCase();
      if ((name.endsWith('.pfx') || name.endsWith('.p12')) && f.size <= 10 * 1024 * 1024) {
        accepted.push(f);
      } else {
        rejected.push(f.name);
      }
    });

    if (rejected.length) {
      toast.error(`Arquivos rejeitados: ${rejected.join(', ')} (somente .pfx/.p12 e <=10MB)`);
    }

    if (accepted.length) {
      setFiles((prev) => [...prev, ...accepted]);
    }
  };

  const handleRemoveFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleEmpresaChange = (id) => {
    setEmpresaId(id);
    setForm((prev) => ({ ...prev, empresa_id: id }));
  }

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!files.length) {
      toast.error("Selecione pelo menos um arquivo PFX.");
      return;
    }

    if (!autoCreateEmpresa && !form.empresa_id) {
      toast.error("Selecione uma empresa ou marque 'Criar empresa automaticamente'.");
      return;
    }

    setIsSubmitting(true);

    try {
      const results = await Promise.allSettled(
        files.map((f) => {
          const data = new FormData();
          if (!autoCreateEmpresa && form.empresa_id) data.append("empresa_id", form.empresa_id);
          data.append("senha", form.senha || "");
          if (autoCreateEmpresa) data.append("auto_create_empresa", "true");
          data.append("arquivo", f);
          return createCertificado(data).then((res) => ({ status: 'fulfilled', res, file: f })).catch((err) => { throw { file: f, error: err } });
        })
      );

      // Normalize results
      const successes = [];
      const passwordFailures = [];
      const cnpjFailures = [];
      const otherFailures = [];

      results.forEach((r) => {
        if (r.status === "fulfilled") {
          // our mapping resolved to an object in .then, so res in value
          successes.push(r.value?.res || r.value);
        } else {
          const reason = r.reason || r.value;
          const errorMsg = reason?.error?.message || reason?.message || String(reason);
          const file = reason?.file || (r.value && r.value.file) || null;

          if (isPasswordError(errorMsg)) {
            passwordFailures.push({ file, error: errorMsg, password: "" });
          } else if (isCnpjError(errorMsg)) {
            cnpjFailures.push({ file, error: errorMsg, cnpj: "" });
          } else {
            otherFailures.push({ file, error: errorMsg });
          }
        }
      });

      if (successes.length) toast.success(`${successes.length} certificado(s) enviado(s) com sucesso!`);
      if (otherFailures.length) {
        console.error('Uploads com outros erros:', otherFailures);
        toast.error(`${otherFailures.length} falha(s) ao enviar certificados. Veja console para detalhes.`);
      }

      const mergedFailures = [...passwordFailures, ...cnpjFailures, ...otherFailures];

      if (mergedFailures.length) {
        setFailedUploads(mergedFailures);
        if (cnpjFailures.length) {
          toast.info("Alguns certificados exigem CNPJ para criar a empresa automaticamente. Informe o CNPJ por arquivo e tente novamente.");
        } else if (passwordFailures.length) {
          toast.info("Alguns certificados exigem senha. Informe as senhas abaixo para tentar novamente.");
        } else {
          toast.error(`${otherFailures.length} falha(s) ao enviar certificados. Veja console para detalhes.`);
        }
      } else if (successes.length > 0) {
        navigate("/certificados");
      }
    } catch (err) {
      toast.error(err.toString().split("Error: ")[1] || "Erro ao enviar certificados.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark-primary py-8 px-4 animate-fadeIn">
      <div className="max-w-3xl mx-auto">
        {/* Header com botão de voltar */}
        <div className="mb-6 flex items-center gap-4">
          <button
            onClick={() => navigate("/certificados")}
            className="p-2 hover:bg-dark-secondary rounded-lg transition-all duration-200 text-neutral-400 hover:text-xfire-orange hover:shadow-md group"
          >
            <FiArrowLeft size={24} className="group-hover:-translate-x-1 transition-transform duration-200" />
          </button>
          <div>
            <h1 className="text-3xl font-bold font-montserrat text-neutral-100 flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-xfire-orange to-xfire-red rounded-xl shadow-lg">
                <FiShield className="text-white" size={28} />
              </div>
              Novo Certificado Digital
            </h1>
            <p className="text-neutral-400 mt-1">Faça upload dos seus certificados .pfx de forma segura</p>
          </div>
        </div>

        {/* Form Card */}
        <div className="bg-dark-secondary rounded-card shadow-xl border border-neutral-900 overflow-hidden animate-slideUp">
          <form onSubmit={handleSubmit} className="p-8 space-y-6">
            {/* Empresa */}
            <div className="space-y-2">
              <Label className="flex items-center gap-2 text-sm font-semibold text-neutral-400">
                <FiBriefcase className="text-xfire-orange" size={18} />
                Empresa
              </Label>
              <SelectCustom
                  value={empresaId}
                  onChange={handleEmpresaChange}
                  isDisabled={autoCreateEmpresa}
              />

              <div className="flex items-center gap-3 mt-3">
                <label className="inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={autoCreateEmpresa}
                    onChange={(e) => {
                      const checked = e.target.checked;
                      setAutoCreateEmpresa(checked);
                      if (checked) {
                        // Clear selected company when opting to auto-create to avoid confusion
                        setEmpresaId(null);
                        setForm((prev) => ({ ...prev, empresa_id: null }));
                      }
                    }}
                    className="form-checkbox h-5 w-5 text-xfire-orange rounded bg-dark-tertiary border-neutral-700"
                  />
                  <span className="ml-2 text-sm text-neutral-400">Criar empresa automaticamente a partir do certificado se não existir</span>
                </label>
              </div>

              {autoCreateEmpresa && (
                <p className="text-sm text-neutral-500 mt-2">Ao marcar, não é necessário selecionar uma empresa — o sistema tentará criar ou encontrar automaticamente a empresa a partir do certificado.</p>
              )}

            </div>

            {/* Upload Area */}
            <div className="space-y-2">
              <Label className="flex items-center gap-2 text-sm font-semibold text-neutral-400">
                <FiUploadCloud className="text-xfire-orange" size={18} />
                Certificados Digitais (.pfx ou .p12)
              </Label>

              {files.length === 0 ? (
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
                      ? 'border-xfire-orange bg-xfire-orange/10 scale-105'
                      : 'border-neutral-700 hover:border-xfire-orange hover:bg-dark-tertiary'
                    }
                  `}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pfx,.p12"
                    multiple
                    onChange={handleFileSelect}
                    className="hidden"
                  />

                  <div className={`
                    transition-all duration-300
                    ${isDragging ? 'scale-110' : 'group-hover:scale-105'}
                  `}>
                    <div className="mx-auto w-16 h-16 bg-gradient-to-br from-xfire-orange to-xfire-red rounded-full flex items-center justify-center mb-4 group-hover:shadow-lg transition-shadow duration-300">
                      <FiUploadCloud className="text-white" size={32} />
                    </div>

                    <p className="text-lg font-semibold text-neutral-100 mb-2">
                      {isDragging ? 'Solte os arquivos aqui' : 'Arraste seus certificados ou clique para selecionar'}
                    </p>
                    <p className="text-sm text-neutral-500">
                      Formatos aceitos: .pfx, .p12 • Máx. 10MB por arquivo
                    </p>
                  </div>

                  {/* Animated border effect */}
                  <div className={`
                    absolute inset-0 rounded-xl transition-opacity duration-300
                    ${isDragging ? 'opacity-100' : 'opacity-0'}
                    bg-gradient-to-r from-xfire-orange/10 via-xfire-red/10 to-xfire-orange/10
                    animate-pulse
                  `}></div>
                </div>
              ) : (
                <div className="border-2 border-xfire-orange/50 bg-gradient-to-br from-xfire-orange/10 to-xfire-red/10 rounded-xl p-6 animate-slideUp">
                  <div className="space-y-4">
                    {files.map((f, idx) => (
                      <div key={f.name + f.size} className="flex items-start gap-4">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 bg-gradient-to-br from-xfire-orange to-xfire-red rounded-xl flex items-center justify-center shadow-lg">
                            <FiFile className="text-white" size={20} />
                          </div>
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex-1">
                              <p className="font-semibold text-neutral-100 truncate">{f.name}</p>
                              <p className="text-sm text-neutral-400 mt-1">{(f.size / 1024).toFixed(2)} KB</p>
                            </div>

                            <button
                              type="button"
                              onClick={() => handleRemoveFile(idx)}
                              className="flex-shrink-0 p-2 hover:bg-red-900/30 rounded-lg transition-all duration-200 text-red-400 group"
                              title="Remover arquivo"
                            >
                              <FiX size={20} className="group-hover:rotate-90 transition-transform duration-200" />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {failedUploads.length > 0 && (
                    <div className="mt-4 border-t border-neutral-700 pt-4">
                      <p className="text-sm font-medium text-red-400 mb-2">Alguns certificados exigem atenção:</p>
                      <div className="space-y-3">
                        {failedUploads.map((f, idx) => (
                          <div key={f.file.name + f.file.size} className="flex items-center gap-3">
                            <div className="flex-1">
                              <p className="text-sm font-semibold text-neutral-100">{f.file.name}</p>
                              <p className="text-xs text-red-400">{f.error}</p>
                            </div>

                            {/* CNPJ input shown when error indicates CNPJ is required */}
                            {isCnpjError(f.error) && (
                              <input
                                type="text"
                                placeholder="CNPJ (somente dígitos)"
                                value={f.cnpj}
                                onChange={(e) => setFailedUploads((prev) => prev.map((p, i) => i === idx ? { ...p, cnpj: e.target.value } : p))}
                                className="px-3 py-2 border border-neutral-700 bg-dark-tertiary text-neutral-100 rounded-lg"
                              />
                            )}

                            {/* Password input shown when error indicates password is required */}
                            {isPasswordError(f.error) && (
                              <input
                                type="password"
                                placeholder="Senha do certificado"
                                value={f.password}
                                onChange={(e) => setFailedUploads((prev) => prev.map((p, i) => i === idx ? { ...p, password: e.target.value } : p))}
                                className="px-3 py-2 border border-neutral-700 bg-dark-tertiary text-neutral-100 rounded-lg"
                              />
                            )}

                            <button
                              type="button"
                              onClick={() => retrySingle(idx)}
                              disabled={isSubmitting}
                              className="px-3 py-2 bg-xfire-orange text-white rounded-lg"
                            >
                              Tentar
                            </button>
                          </div>
                        ))}

                        <div className="flex gap-2">
                          <button type="button" onClick={retryAllFailed} disabled={isSubmitting} className="px-4 py-2 bg-xfire-orange text-white rounded-lg">Tentar todos</button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Senha */}
            <div className="space-y-2">
              <Label className="flex items-center gap-2 text-sm font-semibold text-neutral-400">
                <FiLock className="text-xfire-orange" size={18} />
                Senha padrão (opcional)
              </Label>
              <Input
                name="senha"
                type="password"
                placeholder="Senha padrão para todos os arquivos (opcional)"
                value={form.senha}
                onChange={(e) => setForm({ ...form, senha: e.target.value })}
                className="transition-all duration-200 focus:ring-2 focus:ring-xfire-orange"
              />
              <p className="text-xs text-neutral-500 flex items-center gap-1.5">
                <FiAlertCircle size={12} />
                Senha padrão será usada para todos os arquivos; se falhar, você será solicitado a informar senha por arquivo
              </p>
            </div>

            {/* Info Banner */}
            <div className="bg-gradient-to-r from-blue-900/20 to-indigo-900/20 border border-blue-800/50 rounded-card p-4">
              <div className="flex gap-3">
                <FiAlertCircle className="text-blue-400 flex-shrink-0 mt-0.5" size={20} />
                <div>
                  <p className="text-sm font-medium text-blue-300 mb-1">Informações importantes:</p>
                  <ul className="text-sm text-blue-400 space-y-1">
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
                className="flex-1 px-6 py-3 bg-dark-tertiary hover:bg-neutral-800 text-neutral-100 font-semibold rounded-xl transition-all duration-200 hover:shadow-md"
                disabled={isSubmitting}
              >
                Cancelar
              </button>

              <button
                type="submit"
                disabled={!files.length || isSubmitting}
                className={`
                  flex-1 px-6 py-3 font-semibold rounded-xl transition-all duration-300 transform
                  flex items-center justify-center gap-2
                  ${!files.length || isSubmitting
                    ? 'bg-neutral-700 text-neutral-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 hover:-translate-y-0.5 active:translate-y-0'
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
                    Enviar Certificados
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
