import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';
import { AlertTriangle, ShieldCheck, Activity } from 'lucide-react';

const Dashboard = () => {
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRisks = async () => {
      try {
        const response = await axios.get('http://localhost:8000/risks');
        setRisks(response.data);
      } catch (error) {
        console.error('Failed to fetch risks', error);
      } finally {
        setLoading(false);
      }
    };
    fetchRisks();
  }, []);

  const highRisksCount = risks.filter(r => r.severity === 'high').length;
  const mediumRisksCount = risks.filter(r => r.severity === 'medium').length;

  // Prepare data for Pie Chart (Severity Distribution)
  const severityData = [
    { name: 'High Risk', value: highRisksCount, color: '#ef4444' }, // red-500
    { name: 'Medium Risk', value: mediumRisksCount, color: '#f59e0b' }, // amber-500
  ].filter(d => d.value > 0);

  // Prepare data for Bar Chart (Risk Types)
  const typeCounts = risks.reduce((acc, risk) => {
    acc[risk.risk_type] = (acc[risk.risk_type] || 0) + 1;
    return acc;
  }, {});
  const typeData = Object.keys(typeCounts).map(key => ({
    name: key,
    count: typeCounts[key]
  }));

  if (loading) {
    return <div className="flex justify-center items-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;
  }

  return (
    <div className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8 animate-fade-in-up">
      <div className="mb-10 flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-extrabold text-white tracking-tight">Risk Intelligence</h1>
          <p className="text-lg text-gray-400 mt-2 font-medium">Comprehensive overview of detected risks across all analyzed documents.</p>
        </div>
        <button onClick={() => window.location.reload()} className="p-3 bg-white/10 rounded-xl shadow-sm border border-white/10 hover:bg-white/20 text-brand-400 hover:text-brand-300 hover:scale-105 transition-all duration-300">
          <Activity size={24} />
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
        <div className="glass-card rounded-3xl p-8 flex items-center relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-red-500/20 rounded-full blur-2xl group-hover:bg-red-500/40 transition-all duration-500"></div>
          <div className="p-5 bg-gradient-to-br from-red-500 to-red-700 text-white rounded-2xl shadow-lg shadow-red-500/30 mr-6 transform group-hover:scale-110 transition-transform duration-300">
            <AlertTriangle size={36} strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-1">Critical Risks</p>
            <p className="text-4xl font-black text-white">{highRisksCount}</p>
          </div>
        </div>
        
        <div className="glass-card rounded-3xl p-8 flex items-center relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-amber-500/20 rounded-full blur-2xl group-hover:bg-amber-500/40 transition-all duration-500"></div>
          <div className="p-5 bg-gradient-to-br from-amber-500 to-amber-700 text-white rounded-2xl shadow-lg shadow-amber-500/30 mr-6 transform group-hover:scale-110 transition-transform duration-300">
            <Activity size={36} strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-1">Medium Risks</p>
            <p className="text-4xl font-black text-white">{mediumRisksCount}</p>
          </div>
        </div>

        <div className="glass-card rounded-3xl p-8 flex items-center relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-brand-500/20 rounded-full blur-2xl group-hover:bg-brand-500/40 transition-all duration-500"></div>
          <div className="p-5 bg-gradient-to-br from-brand-500 to-brand-700 text-white rounded-2xl shadow-lg shadow-brand-500/30 mr-6 transform group-hover:scale-110 transition-transform duration-300">
            <ShieldCheck size={36} strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-1">Total Flags</p>
            <p className="text-4xl font-black text-white">{risks.length}</p>
          </div>
        </div>
      </div>

      {/* Charts Area */}
      {risks.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          <div className="glass-card rounded-3xl p-8 shadow-xl">
            <h3 className="text-xl font-bold text-white mb-8 text-center">Severity Distribution</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={80}
                    outerRadius={120}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    stroke="none"
                  >
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value) => [`${value} Risks`, 'Count']}
                    contentStyle={{ backgroundColor: '#0f172a', color: '#fff', borderRadius: '16px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)', padding: '12px 20px', fontWeight: 'bold' }}
                    itemStyle={{ color: '#fff' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-card rounded-3xl p-8 shadow-xl">
            <h3 className="text-xl font-bold text-white mb-8 text-center">Flags by Category</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={typeData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontWeight: 600 }} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontWeight: 600 }} allowDecimals={false} dx={-10} />
                  <Tooltip
                    cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
                    contentStyle={{ backgroundColor: '#0f172a', color: '#fff', borderRadius: '16px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)', fontWeight: 'bold' }}
                  />
                  <Bar dataKey="count" fill="url(#colorUv)" radius={[8, 8, 0, 0]} barSize={50}>
                    {typeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#3b82f6' : '#6366f1'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ) : (
        <div className="glass-card rounded-3xl p-16 text-center border-dashed border-2 border-brand-500/30">
          <div className="inline-flex items-center justify-center p-6 bg-brand-900/30 rounded-full mb-6">
            <ShieldCheck className="h-20 w-20 text-brand-400" />
          </div>
          <h3 className="text-3xl font-extrabold text-white">Zero Risks Detected</h3>
          <p className="text-xl text-gray-400 mt-4 max-w-lg mx-auto">Your repository of analyzed documents is currently clean. Upload more documents to generate risk insights.</p>
        </div>
      )}

      {/* Detailed Risk List */}
      {risks.length > 0 && (
        <div className="glass-card rounded-3xl overflow-hidden shadow-xl">
          <div className="px-8 py-6 border-b border-gray-700/50 bg-white/5">
            <h3 className="text-xl font-extrabold text-white flex items-center">
              <AlertTriangle className="mr-3 text-brand-400" size={24} />
              Detailed Audit Log
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-700/50">
              <thead className="bg-white/5">
                <tr>
                  <th scope="col" className="px-8 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">Severity</th>
                  <th scope="col" className="px-8 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">Risk Type</th>
                  <th scope="col" className="px-8 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">Source Document</th>
                  <th scope="col" className="px-8 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">Flagged Excerpt</th>
                </tr>
              </thead>
              <tbody className="bg-transparent divide-y divide-gray-700/50">
                {risks.map((risk, idx) => (
                  <tr key={idx} className="hover:bg-white/5 transition-colors duration-200">
                    <td className="px-8 py-5 whitespace-nowrap">
                      <span className={`inline-flex items-center px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest shadow-sm
                        ${risk.severity === 'high' ? 'bg-red-900/50 text-red-400 border border-red-500/30' : 'bg-amber-900/50 text-amber-400 border border-amber-500/30'}`}>
                        {risk.severity}
                      </span>
                    </td>
                    <td className="px-8 py-5 whitespace-nowrap text-sm font-extrabold text-gray-200 capitalize">
                      {risk.risk_type.replace('_', ' ')}
                    </td>
                    <td className="px-8 py-5 whitespace-nowrap text-sm font-semibold text-gray-400">
                      {risk.source} <span className="text-brand-400 ml-1">(Pg {risk.page})</span>
                    </td>
                    <td className="px-8 py-5 text-sm text-gray-400 max-w-md truncate font-medium" title={risk.text}>
                      {risk.text}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
