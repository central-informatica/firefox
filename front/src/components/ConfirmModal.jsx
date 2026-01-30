import React from 'react';

export default function ConfirmModal({ open, title, description, confirmText = 'Confirmar', cancelText = 'Cancelar', onConfirm, onCancel, loading = false, variant = 'default' }) {
  if (!open) return null;

  const confirmButtonStyles = variant === 'danger'
    ? 'bg-xfire-red hover:bg-xfire-red/90'
    : 'bg-xfire-orange hover:bg-xfire-orange/90';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onCancel} />

      <div className="relative bg-dark-secondary rounded-modal shadow-2xl w-[90%] max-w-md p-6 mx-4 border border-neutral-900 animate-[fadeInUp_0.3s_ease-out]">
        <h3 className="text-lg font-semibold text-neutral-100 mb-2 font-montserrat">{title}</h3>
        <p className="text-sm text-neutral-400 mb-6">{description}</p>

        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2.5 bg-dark-tertiary hover:bg-neutral-800 text-neutral-300 rounded-button transition-colors border border-neutral-800"
            disabled={loading}
          >
            {cancelText}
          </button>

          <button
            onClick={onConfirm}
            className={`px-4 py-2.5 rounded-button text-white font-medium transition-all duration-200 ${loading ? 'opacity-70' : ''} ${confirmButtonStyles}`}
            disabled={loading}
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processando...
              </span>
            ) : confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
