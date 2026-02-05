import { useState, useRef, useEffect } from "react";
import { FiChevronLeft, FiChevronRight, FiCalendar } from "react-icons/fi";

const MESES = [
  "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
];

const DIAS_SEMANA = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sab"];

export default function DatePicker({ value, onChange, placeholder = "Selecione uma data" }) {
  const [isOpen, setIsOpen] = useState(false);
  const [viewDate, setViewDate] = useState(() => {
    if (value) {
      const [year, month] = value.split("-");
      return { year: parseInt(year), month: parseInt(month) - 1 };
    }
    const now = new Date();
    return { year: now.getFullYear(), month: now.getMonth() };
  });
  const containerRef = useRef(null);

  // Fechar ao clicar fora
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Atualizar viewDate quando value mudar
  useEffect(() => {
    if (value) {
      const [year, month] = value.split("-");
      setViewDate({ year: parseInt(year), month: parseInt(month) - 1 });
    }
  }, [value]);

  const getDaysInMonth = (year, month) => {
    return new Date(year, month + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (year, month) => {
    return new Date(year, month, 1).getDay();
  };

  const handlePrevMonth = () => {
    setViewDate((prev) => {
      if (prev.month === 0) {
        return { year: prev.year - 1, month: 11 };
      }
      return { ...prev, month: prev.month - 1 };
    });
  };

  const handleNextMonth = () => {
    setViewDate((prev) => {
      if (prev.month === 11) {
        return { year: prev.year + 1, month: 0 };
      }
      return { ...prev, month: prev.month + 1 };
    });
  };

  const handleSelectDay = (day) => {
    const month = String(viewDate.month + 1).padStart(2, "0");
    const dayStr = String(day).padStart(2, "0");
    const dateStr = `${viewDate.year}-${month}-${dayStr}`;
    onChange(dateStr);
    setIsOpen(false);
  };

  const formatDisplayDate = (dateStr) => {
    if (!dateStr) return "";
    const [year, month, day] = dateStr.split("-");
    return `${day}/${month}/${year}`;
  };

  const isSelectedDay = (day) => {
    if (!value) return false;
    const [year, month, dayVal] = value.split("-");
    return (
      parseInt(year) === viewDate.year &&
      parseInt(month) - 1 === viewDate.month &&
      parseInt(dayVal) === day
    );
  };

  const isToday = (day) => {
    const today = new Date();
    return (
      today.getFullYear() === viewDate.year &&
      today.getMonth() === viewDate.month &&
      today.getDate() === day
    );
  };

  const renderCalendar = () => {
    const daysInMonth = getDaysInMonth(viewDate.year, viewDate.month);
    const firstDay = getFirstDayOfMonth(viewDate.year, viewDate.month);
    const days = [];

    // Dias vazios antes do primeiro dia do mes
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="w-9 h-9" />);
    }

    // Dias do mes
    for (let day = 1; day <= daysInMonth; day++) {
      const selected = isSelectedDay(day);
      const today = isToday(day);

      days.push(
        <button
          key={day}
          type="button"
          onClick={() => handleSelectDay(day)}
          className={`
            w-9 h-9 rounded-lg text-sm font-medium transition-all duration-200
            flex items-center justify-center cursor-pointer
            ${selected
              ? "bg-gradient-to-r from-orange-500 to-orange-600 text-white shadow-lg shadow-orange-500/30"
              : today
                ? "bg-orange-500/20 text-orange-400 hover:bg-orange-500/30"
                : "text-neutral-300 hover:bg-dark-tertiary hover:text-white"
            }
          `}
        >
          {day}
        </button>
      );
    }

    return days;
  };

  return (
    <div ref={containerRef} className="relative">
      {/* Input que abre o calendario */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 w-full px-4 py-3 bg-dark-tertiary border border-neutral-800 rounded-xl text-neutral-100 cursor-pointer hover:border-neutral-700 transition-colors duration-200"
      >
        <FiCalendar className="text-neutral-500" size={18} />
        <span className={value ? "text-neutral-100" : "text-neutral-500"}>
          {value ? formatDisplayDate(value) : placeholder}
        </span>
      </div>

      {/* Calendario dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 p-4 bg-dark-secondary border border-neutral-800 rounded-xl shadow-2xl z-50 animate-[fadeIn_0.2s_ease-out]">
          {/* Header do calendario */}
          <div className="flex items-center justify-between mb-4">
            <button
              type="button"
              onClick={handlePrevMonth}
              className="p-2 hover:bg-dark-tertiary rounded-lg transition-colors duration-200 text-neutral-400 hover:text-white cursor-pointer"
            >
              <FiChevronLeft size={18} />
            </button>

            <span className="font-semibold text-neutral-100">
              {MESES[viewDate.month]} {viewDate.year}
            </span>

            <button
              type="button"
              onClick={handleNextMonth}
              className="p-2 hover:bg-dark-tertiary rounded-lg transition-colors duration-200 text-neutral-400 hover:text-white cursor-pointer"
            >
              <FiChevronRight size={18} />
            </button>
          </div>

          {/* Dias da semana */}
          <div className="grid grid-cols-7 gap-1 mb-2">
            {DIAS_SEMANA.map((dia) => (
              <div
                key={dia}
                className="w-9 h-9 flex items-center justify-center text-xs font-medium text-neutral-500"
              >
                {dia}
              </div>
            ))}
          </div>

          {/* Grid de dias */}
          <div className="grid grid-cols-7 gap-1">
            {renderCalendar()}
          </div>

          {/* Botao Hoje */}
          <div className="mt-3 pt-3 border-t border-neutral-800">
            <button
              type="button"
              onClick={() => {
                const today = new Date();
                const year = today.getFullYear();
                const month = String(today.getMonth() + 1).padStart(2, "0");
                const day = String(today.getDate()).padStart(2, "0");
                onChange(`${year}-${month}-${day}`);
                setIsOpen(false);
              }}
              className="w-full py-2 text-sm font-medium text-orange-400 hover:text-orange-300 hover:bg-orange-500/10 rounded-lg transition-colors duration-200 cursor-pointer"
            >
              Hoje
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
