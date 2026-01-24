import formatDate from "../../utils/date";

export default function CertificadoCard({ certificado, children }) {
  const {
    certificado_id,
    proprietario,
    nome_arquivo,
    emitido_por,
    data_inicio,
    valido_ate,
    cnpj,
  } = certificado;

  return (
    <div className="flex items-start justify-between gap-3">
      <div className="min-w-0 space-y-1">
        <p className="font-medium text-gray-800 truncate">
          {proprietario || nome_arquivo || `Certificado #${certificado_id}`}
        </p>

        {emitido_por && (
          <p className="text-sm text-gray-600">
            <strong>Emitido por:</strong> {emitido_por}
          </p>
        )}

        <div className="flex gap-4 text-xs text-gray-500">
          {data_inicio && (
            <span>
              <strong>Início:</strong> {data_inicio}
            </span>
          )}
          {valido_ate && (
            <span>
              <strong>Validade:</strong> {formatDate(valido_ate)}
            </span>
          )}
        </div>

        {cnpj && (
          <p className="text-xs text-gray-500 truncate">CNPJ: {cnpj}</p>
        )}
      </div>

      {/* 🔹 Slot de ações (botões, ícones, etc) */}
      {children && <div className="flex-shrink-0">{children}</div>}
    </div>
  );
}
