import React from "react";
import {
  FiUsers, FiShield, FiActivity, FiTrendingUp,
  FiClock, FiCheckCircle, FiAlertCircle
} from "react-icons/fi";

const Dashboard = () => {
  const stats = [
    {
      label: "Total de Usuarios",
      value: "124",
      change: "+12%",
      positive: true,
      icon: <FiUsers className="text-status-monitorado" size={24} />
    },
    {
      label: "Certificados Ativos",
      value: "48",
      change: "+8%",
      positive: true,
      icon: <FiShield className="text-status-permitido" size={24} />
    },
    {
      label: "Acessos Hoje",
      value: "1,847",
      change: "+23%",
      positive: true,
      icon: <FiActivity className="text-xfire-orange" size={24} />
    },
    {
      label: "Taxa de Sucesso",
      value: "98.2%",
      change: "+2.1%",
      positive: true,
      icon: <FiTrendingUp className="text-status-expirando" size={24} />
    },
  ];

  const userAccessData = [
    { hour: "00h", value: 12 },
    { hour: "03h", value: 8 },
    { hour: "06h", value: 15 },
    { hour: "09h", value: 45 },
    { hour: "12h", value: 68 },
    { hour: "15h", value: 82 },
    { hour: "18h", value: 95 },
    { hour: "21h", value: 52 },
  ];

  const topCertificates = [
    { name: "Cert-Empresa-A", uses: 342, percentage: 85 },
    { name: "Cert-Fiscal-B", uses: 298, percentage: 72 },
    { name: "Cert-NF-Digital", uses: 245, percentage: 61 },
    { name: "Cert-SPED-C", uses: 187, percentage: 47 },
    { name: "Cert-API-Gateway", uses: 156, percentage: 39 },
  ];

  const recentActivities = [
    { user: "Joao Silva", cert: "Cert-Empresa-A", time: "14:32", status: "success" },
    { user: "Maria Santos", cert: "Cert-Fiscal-B", time: "14:28", status: "success" },
    { user: "Pedro Costa", cert: "Cert-NF-Digital", time: "14:15", status: "success" },
    { user: "Ana Paula", cert: "Cert-SPED-C", time: "14:10", status: "error" },
    { user: "Carlos Mendes", cert: "Cert-API-Gateway", time: "14:05", status: "success" },
    { user: "Julia Ferreira", cert: "Cert-Empresa-A", time: "13:58", status: "success" },
  ];

  const maxValue = Math.max(...userAccessData.map(d => d.value));

  return (
    <div className="space-y-6 w-full">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-100 mb-2 font-montserrat">Dashboard</h1>
        <p className="text-neutral-400">Visao geral do sistema de certificados digitais</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div
            key={index}
            className="bg-dark-secondary rounded-card p-6 hover:bg-dark-tertiary transition-all duration-300 border border-neutral-900"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-dark-tertiary rounded-xl">
                {stat.icon}
              </div>
              <span className={`text-sm font-semibold ${stat.positive ? 'text-status-permitido' : 'text-status-bloqueado'}`}>
                {stat.change}
              </span>
            </div>
            <h3 className="text-neutral-400 text-sm font-medium mb-1">{stat.label}</h3>
            <p className="text-3xl font-bold text-neutral-100">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Grafico de Acessos de Usuarios */}
        <div className="bg-dark-secondary rounded-card p-6 border border-neutral-900">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-neutral-100 font-montserrat">Acessos por Horario</h2>
              <p className="text-sm text-neutral-400 mt-1">Ultimas 24 horas</p>
            </div>
            <div className="p-2 bg-xfire-orange/10 rounded-lg">
              <FiActivity className="text-xfire-orange" size={20} />
            </div>
          </div>

          <div className="h-64 flex items-end justify-between gap-3">
            {userAccessData.map((data, index) => (
              <div key={index} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full flex flex-col justify-end h-full">
                  <div
                    className="w-full bg-gradient-to-t from-xfire-orange to-xfire-red rounded-t-lg hover:from-xfire-orange/80 hover:to-xfire-red/80 transition-all duration-300 relative group"
                    style={{ height: `${(data.value / maxValue) * 100}%` }}
                  >
                    <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-dark-tertiary text-neutral-100 text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap border border-neutral-800">
                      {data.value} acessos
                    </div>
                  </div>
                </div>
                <span className="text-xs text-neutral-500 font-medium">{data.hour}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Certificados Usados */}
        <div className="bg-dark-secondary rounded-card p-6 border border-neutral-900">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-neutral-100 font-montserrat">Certificados Mais Usados</h2>
              <p className="text-sm text-neutral-400 mt-1">Esta semana</p>
            </div>
            <div className="p-2 bg-status-monitorado/10 rounded-lg">
              <FiShield className="text-status-monitorado" size={20} />
            </div>
          </div>

          <div className="space-y-4">
            {topCertificates.map((cert, index) => (
              <div key={index} className="group">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-neutral-300 group-hover:text-xfire-orange transition-colors">
                    {cert.name}
                  </span>
                  <span className="text-sm font-bold text-neutral-100">{cert.uses}</span>
                </div>
                <div className="w-full bg-dark-tertiary rounded-full h-2.5 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-xfire-orange to-xfire-red h-2.5 rounded-full transition-all duration-500 group-hover:from-xfire-orange/80 group-hover:to-xfire-red/80"
                    style={{ width: `${cert.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Atividades Recentes */}
      <div className="bg-dark-secondary rounded-card p-6 border border-neutral-900">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-neutral-100 font-montserrat">Atividades Recentes</h2>
            <p className="text-sm text-neutral-400 mt-1">Uso de certificados em tempo real</p>
          </div>
          <div className="p-2 bg-xfire-red/10 rounded-lg">
            <FiClock className="text-xfire-red" size={20} />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-neutral-800">
                <th className="text-left py-3 px-4 text-sm font-semibold text-neutral-400">Usuario</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-neutral-400">Certificado</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-neutral-400">Horario</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-neutral-400">Status</th>
              </tr>
            </thead>
            <tbody>
              {recentActivities.map((activity, index) => (
                <tr
                  key={index}
                  className="border-b border-neutral-800/50 hover:bg-dark-tertiary/50 transition-colors"
                >
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-xfire-orange to-xfire-red rounded-full flex items-center justify-center text-white font-semibold text-sm">
                        {activity.user.split(' ').map(n => n[0]).join('')}
                      </div>
                      <span className="font-medium text-neutral-100">{activity.user}</span>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <span className="text-sm text-neutral-400">{activity.cert}</span>
                  </td>
                  <td className="py-4 px-4">
                    <span className="text-sm text-neutral-400 flex items-center gap-1">
                      <FiClock size={14} />
                      {activity.time}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    {activity.status === 'success' ? (
                      <span className="badge-permitido">
                        <FiCheckCircle size={14} />
                        Sucesso
                      </span>
                    ) : (
                      <span className="badge-bloqueado">
                        <FiAlertCircle size={14} />
                        Erro
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
