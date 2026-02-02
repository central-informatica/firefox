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
    <div className="flex items-start justify-between gap-3 bg-dark-secondary p-4 rounded-card border border-neutral-900">
      <div className="min-w-0 space-y-1">
        <p className="font-medium text-neutral-100 truncate">
          {proprietario || nome_arquivo || `Certificado #${certificado_id}`}
        </p>

        {emitido_por && (
          <p className="text-sm text-neutral-400">
            <strong className="text-neutral-300">Emitido por:</strong> {emitido_por}
          </p>
        )}

        <div className="flex gap-4 text-xs text-neutral-500">
          {data_inicio && (
            <span>
              <strong className="text-neutral-400">Inicio:</strong> {data_inicio}
            </span>
          )}
          {valido_ate && (
            <span>
              <strong className="text-neutral-400">Validade:</strong> {formatDate(valido_ate)}
            </span>
          )}
        </div>

        {cnpj && (
          <p className="text-xs text-neutral-500 truncate">CNPJ: {cnpj}</p>
        )}
      </div>

      {children && <div className="flex-shrink-0">{children}</div>}
    </div>
  );
}
