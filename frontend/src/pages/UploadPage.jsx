import React, { useState } from 'react';
import api from '../lib/api';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';

const UploadPage = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
    setError(null);
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploading(true);
    setError(null);
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResults(response.data);
      setFiles([]);
    } catch (error) {
      console.error('Upload failed:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Upload failed. Please try again.';
      setError(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-16 px-4 sm:px-6 lg:px-8 animate-fade-in-up">
      <div className="glass-card rounded-3xl overflow-hidden">
        <div className="p-10">
          <div className="text-center mb-10">
            <div className="inline-flex items-center justify-center p-3 bg-brand-500/20 rounded-full mb-4">
              <Upload className="text-brand-400" size={36} />
            </div>
            <h2 className="text-4xl font-extrabold text-white tracking-tight">
              Analyze Documents
            </h2>
            <p className="mt-4 text-lg text-gray-400 max-w-2xl mx-auto">
              Securely upload your contracts, policies, or SOPs for intelligent AI analysis, semantic search, and automated risk detection.
            </p>
          </div>

          <div className="relative border-2 border-dashed border-gray-600 rounded-2xl p-16 text-center hover:bg-white/5 hover:border-brand-500 transition-all duration-300 group">
            <input
              type="file"
              multiple
              accept=".pdf"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              id="file-upload"
            />
            <div className="flex flex-col items-center pointer-events-none">
              <div className="p-4 bg-white/10 shadow-sm rounded-full mb-4 group-hover:scale-110 group-hover:shadow-md transition-transform duration-300">
                <Upload className="h-12 w-12 text-brand-400" />
              </div>
              <span className="text-xl font-semibold text-gray-200">Drop PDFs here or click to browse</span>
              <span className="text-sm text-gray-500 mt-2">Maximum file size 50MB</span>
            </div>
          </div>

          {error && (
            <div className="mt-6 p-4 bg-red-500/20 border border-red-500/50 rounded-xl flex items-start animate-fade-in-up">
              <AlertCircle className="text-red-400 mr-3 mt-0.5 flex-shrink-0" size={20} />
              <div>
                <h4 className="text-red-300 font-semibold">Upload Error</h4>
                <p className="text-red-200/80 text-sm mt-1">{error}</p>
              </div>
            </div>
          )}

          {files.length > 0 && (
            <div className="mt-10 animate-fade-in-up">
              <h3 className="text-lg font-bold text-gray-200 mb-4">Selected Files</h3>
              <ul className="space-y-3">
                {files.map((file, idx) => (
                  <li key={idx} className="flex items-center p-4 bg-white/5 rounded-xl shadow-sm border border-white/10 hover:border-brand-500/50 transition-colors">
                    <div className="p-2 bg-brand-500/20 rounded-lg mr-4">
                      <FileText className="text-brand-400" size={24} />
                    </div>
                    <span className="text-sm font-semibold text-gray-300 flex-1">{file.name}</span>
                    <span className="text-xs font-medium bg-white/10 text-gray-400 px-3 py-1 rounded-full">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </span>
                  </li>
                ))}
              </ul>

              <div className="mt-8 flex justify-end">
                <button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="inline-flex items-center px-8 py-4 text-lg font-bold rounded-xl shadow-lg text-white bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500 disabled:opacity-50 hover:scale-105 transition-all duration-300"
                >
                  {uploading ? (
                    <><span className="animate-spin mr-3 border-2 border-white border-t-transparent rounded-full w-5 h-5"></span> Processing...</>
                  ) : (
                    'Run AI Analysis'
                  )}
                </button>
              </div>
            </div>
          )}

          {results.length > 0 && (
            <div className="mt-10 pt-8 border-t border-gray-700 animate-fade-in-up">
              <h3 className="text-lg font-bold text-gray-200 mb-4 flex items-center">
                <CheckCircle className="text-green-400 mr-2" /> Analysis Complete
              </h3>
              <ul className="space-y-3">
                {results.map((result, idx) => (
                  <li key={idx} className="flex items-center p-4 bg-green-900/20 rounded-xl border border-green-500/30">
                    <CheckCircle className="text-green-400 mr-4" size={24} />
                    <div>
                      <p className="text-sm font-bold text-gray-200">{result.filename}</p>
                      <p className="text-xs font-semibold text-green-400 mt-1 uppercase tracking-wide">Status: {result.status}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
