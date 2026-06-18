import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldAlert, FileText, Activity, Search, RefreshCw } from 'lucide-react';
import api from '../lib/api';

const Navbar = () => {
  const location = useLocation();

  const navItems = [
    { name: 'Upload', path: '/', icon: <FileText size={18} /> },
    { name: 'Q&A', path: '/qa', icon: <Search size={18} /> },
    { name: 'Risks', path: '/risks', icon: <Activity size={18} /> },
  ];

  const handleReset = async () => {
    try {
        await api.post('/reset');
        window.location.reload();
    } catch (error) {
        console.error('Error resetting system:', error);
    }
  };

  return (
    <nav className="glass-card sticky top-0 z-50 border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-20">
          <div className="flex w-full">
            <div className="flex-shrink-0 flex items-center group cursor-pointer">
              <div className="p-2 bg-gradient-to-tr from-brand-500 to-indigo-500 rounded-xl shadow-lg group-hover:shadow-brand-500/30 transition-all duration-300">
                <ShieldAlert className="h-7 w-7 text-white" />
              </div>
              <span className="ml-3 font-extrabold text-2xl text-white tracking-tight">
                Verico
              </span>
            </div>
            <div className="hidden sm:ml-auto sm:flex sm:space-x-2 items-center">
              {navItems.map((item) => (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`${
                    location.pathname === item.path
                      ? 'bg-white/10 shadow-sm text-white border border-white/10'
                      : 'text-gray-400 hover:bg-white/5 hover:text-gray-200'
                  } inline-flex items-center px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ease-out hover:scale-105`}
                >
                  <span className={`${location.pathname === item.path ? 'text-brand-400' : 'text-gray-500'} mr-2 transition-colors`}>{item.icon}</span>
                  {item.name}
                </Link>
              ))}
              <button
                onClick={handleReset}
                className="ml-4 inline-flex items-center px-4 py-2.5 rounded-xl text-sm font-bold bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 transition-all duration-300 ease-out hover:scale-105"
                title="Reset System"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Reset System
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
