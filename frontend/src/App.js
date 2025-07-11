import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Upload, 
  Search, 
  Brain, 
  Globe, 
  Settings,
  AlertCircle,
  CheckCircle,
  MessageCircle
} from 'lucide-react';
import FileUpload from './components/FileUpload';
import SqlEditor from './components/SqlEditor';
import DataTable from './components/DataTable';
import SummaryGenerator from './components/SummaryGenerator';
import ChatBot from './components/ChatBot';
import { getTables, fetchPublicData, healthCheck } from './services/api';

const App = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [tables, setTables] = useState([]);
  const [queryResult, setQueryResult] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [plotData, setPlotData] = useState([]);
  const [filterColumn, setFilterColumn] = useState('');
  const [filterType, setFilterType] = useState('');

  const tabs = [
    { id: 'upload', name: 'Upload Data', icon: Upload },
    { id: 'query', name: 'SQL Query', icon: Search },
    { id: 'summary', name: 'AI Summary', icon: Brain },
    { id: 'public', name: 'Public Data', icon: Globe },
    { id: 'chat', name: 'Chat with Data Explorer', icon: MessageCircle },
  ]; 

  useEffect(() => {
    checkBackendHealth();
    loadTables();
  }, []);

  const checkBackendHealth = async () => {
    try {
      await healthCheck();
      setBackendStatus('connected');
    } catch (error) {
      setBackendStatus('disconnected');
      console.error('Backend connection failed:', error);
    }
  };

  const loadTables = async () => {
    try {
      const result = await getTables();
      setTables(result.tables || []);
    } catch (error) {
      console.error('Failed to load tables:', error);
    }
  };

  const handleUploadSuccess = (result) => {
    setSuccess(`Successfully uploaded ${result.table_name} with ${result.row_count} rows`);
    setError('');
    loadTables(); // Refresh tables list
    setPlotData(result.plot_data || []);
    setTimeout(() => setSuccess(''), 5000);
  };

  const handleUploadError = (errorMessage) => {
    setError(errorMessage);
    setSuccess('');
    setTimeout(() => setError(''), 5000);
  };

  const handleQueryResult = (result) => {
    setQueryResult(result);
    setError('');
  };

  const handleQueryError = (errorMessage) => {
    setError(errorMessage);
    setQueryResult(null);
    setTimeout(() => setError(''), 5000);
  };

  const handlePublicDataFetch = async (source, params = {}) => {
    setLoading(true);
    try {
      const result = await fetchPublicData(source, params);
      if (result.success) {
        setSuccess(`Successfully fetched ${result.table_name} with ${result.row_count} rows`);
        loadTables(); // Refresh tables list
      } else {
        setError(result.error || 'Failed to fetch public data');
      }
    } catch (error) {
      setError(error.response?.data?.detail || error.message);
    } finally {
      setLoading(false);
      setTimeout(() => setSuccess(''), 5000);
      setTimeout(() => setError(''), 5000);
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'upload':
        return (
          <>
            <FileUpload
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
            />
            {/* Graphical Analysis Area */}
            {plotData.length > 0 && (
              <div className="mt-8 card">
                <h2 className="text-xl font-semibold text-secondary-900 mb-4">Graphical Analysis</h2>
                {/* Filter UI */}
                <div className="flex flex-wrap gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Filter by Column</label>
                    <select
                      className="form-select"
                      value={filterColumn}
                      onChange={e => setFilterColumn(e.target.value)}
                    >
                      <option value="">All</option>
                      {[...new Set(plotData.map(p => p.column))].map(col => (
                        <option key={col} value={col}>{col}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Filter by Graph Type</label>
                    <select
                      className="form-select"
                      value={filterType}
                      onChange={e => setFilterType(e.target.value)}
                    >
                      <option value="">All</option>
                      {[...new Set(plotData.map(p => p.type))].map(type => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>
                  <button
                    className="btn-secondary self-end"
                    onClick={() => { setFilterColumn(''); setFilterType(''); }}
                  >
                    Reset Filters
                  </button>
                </div>
                <button
                  className="mb-4 btn-primary"
                  onClick={() => {
                    plotData.forEach(plot => {
                      const link = document.createElement('a');
                      link.href = plot.url;
                      link.download = plot.url.split('/').pop();
                      document.body.appendChild(link);
                      link.click();
                      document.body.removeChild(link);
                    });
                  }}
                >
                  Download All Graphs
                </button>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {plotData
                    .filter(plot =>
                      (!filterColumn || plot.column === filterColumn) &&
                      (!filterType || plot.type === filterType)
                    )
                    .map((plot, idx) => (
                      <div key={idx} className="flex flex-col items-center">
                        <img src={plot.url} alt={`Graph ${idx + 1}`} className="w-full max-w-xs rounded shadow" />
                        <span className="mt-2 text-sm text-secondary-700">{plot.column} - {plot.type}</span>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </>
        );
      
      case 'query':
        return (
          <div className="space-y-6">
            <SqlEditor
              onQueryResult={handleQueryResult}
              onQueryError={handleQueryError}
              availableTables={tables}
            />
            {queryResult && (
              <DataTable
                data={queryResult.data}
                columns={queryResult.columns}
                rowCount={queryResult.row_count}
              />
            )}
          </div>
        );
      
      case 'summary':
        return (
          <SummaryGenerator availableTables={tables} />
        );
      
      case 'public':
        return (
          <div className="card">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-secondary-900 mb-2">
                Public Data Sources
              </h2>
              <p className="text-secondary-600">
                Fetch data from free public APIs for analysis
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 border border-secondary-200 rounded-lg">
                <h3 className="font-medium text-secondary-900 mb-2">COVID-19 Data</h3>
                <p className="text-sm text-secondary-600 mb-3">
                  Global COVID-19 statistics by country
                </p>
                <button
                  onClick={() => handlePublicDataFetch('covid')}
                  disabled={loading}
                  className="btn-primary w-full disabled:opacity-50"
                >
                  {loading ? 'Fetching...' : 'Fetch COVID Data'}
                </button>
              </div>

              <div className="p-4 border border-secondary-200 rounded-lg">
                <h3 className="font-medium text-secondary-900 mb-2">Weather Data</h3>
                <p className="text-sm text-secondary-600 mb-3">
                  Current weather information
                </p>
                <button
                  onClick={() => handlePublicDataFetch('weather', { city: 'London' })}
                  disabled={loading}
                  className="btn-primary w-full disabled:opacity-50"
                >
                  {loading ? 'Fetching...' : 'Fetch Weather Data'}
                </button>
              </div>

              <div className="p-4 border border-secondary-200 rounded-lg">
                <h3 className="font-medium text-secondary-900 mb-2">Stock Data</h3>
                <p className="text-sm text-secondary-600 mb-3">
                  Stock market information
                </p>
                <button
                  onClick={() => handlePublicDataFetch('stocks', { symbol: 'AAPL' })}
                  disabled={loading}
                  className="btn-primary w-full disabled:opacity-50"
                >
                  {loading ? 'Fetching...' : 'Fetch Stock Data'}
                </button>
              </div>
            </div>
          </div>
        );
      
      case 'chat':
        return <ChatBot />;
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-secondary-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <Database className="w-8 h-8 text-primary-600" />
              <div>
                <h1 className="text-xl font-bold text-secondary-900">
                  Data Explorer & LLM Dashboard
                </h1>
                <p className="text-sm text-secondary-600">
                  Upload, query, and analyze data with AI-powered insights
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                {backendStatus === 'connected' ? (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                ) : backendStatus === 'disconnected' ? (
                  <AlertCircle className="w-4 h-4 text-red-600" />
                ) : (
                  <div className="loading-spinner w-4 h-4"></div>
                )}
                <span className="text-sm text-secondary-600">
                  Backend: {backendStatus}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-secondary-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status Messages */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <p className="text-red-800 font-medium">Error</p>
            </div>
            <p className="text-red-700 mt-1">{error}</p>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <p className="text-green-800 font-medium">Success</p>
            </div>
            <p className="text-green-700 mt-1">{success}</p>
          </div>
        )}

        {/* Tab Content */}
        {renderTabContent()}

        {/* Tables Overview */}
        {tables.length > 0 && (
          <div className="mt-8 card">
            <h2 className="text-lg font-semibold text-secondary-900 mb-4">
              Available Tables ({tables.length})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {tables.map((table) => (
                <div
                  key={table.name}
                  className="p-4 border border-secondary-200 rounded-lg hover:border-secondary-300 transition-colors duration-200"
                >
                  <h3 className="font-medium text-secondary-900 mb-1">
                    {table.name}
                  </h3>
                  <p className="text-sm text-secondary-600">
                    {table.row_count} rows • {table.columns.length} columns
                  </p>
                  <div className="mt-2">
                    <p className="text-xs text-secondary-500">
                      Columns: {table.columns.slice(0, 3).join(', ')}
                      {table.columns.length > 3 && '...'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-secondary-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-secondary-600">
            <p>
              Data Explorer & LLM Dashboard - Built with React, FastAPI, and DuckDB
            </p>
            <p className="mt-1">
              Powered by local LLM for privacy-focused data analysis
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App; 