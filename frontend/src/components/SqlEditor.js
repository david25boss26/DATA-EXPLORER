import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Play, Save, RotateCcw, Download } from 'lucide-react';
import { executeQuery } from '../services/api';

const SqlEditor = ({ onQueryResult, onQueryError, availableTables = [] }) => {
  const [query, setQuery] = useState('');
  const [executing, setExecuting] = useState(false);
  const [queryHistory, setQueryHistory] = useState([]);

  const sampleQueries = [
    'SELECT * FROM table_name LIMIT 10',
    'SELECT COUNT(*) FROM table_name',
    'SELECT column1, column2 FROM table_name WHERE column1 > 100',
    'SELECT column1, AVG(column2) FROM table_name GROUP BY column1',
  ];

  const handleExecuteQuery = async () => {
    if (!query.trim()) return;

    setExecuting(true);
    try {
      const result = await executeQuery(query);
      
      if (result.success) {
        // Add to history
        setQueryHistory(prev => [
          { query: query, timestamp: new Date(), success: true },
          ...prev.slice(0, 9) // Keep last 10 queries
        ]);
        
        onQueryResult(result);
      } else {
        onQueryError(result.error);
      }
    } catch (error) {
      onQueryError(error.response?.data?.detail || error.message);
    } finally {
      setExecuting(false);
    }
  };

  const handleSaveQuery = () => {
    if (!query.trim()) return;
    
    const blob = new Blob([query], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `query_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.sql`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleLoadQuery = (sampleQuery) => {
    setQuery(sampleQuery);
  };

  const handleClearQuery = () => {
    setQuery('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleExecuteQuery();
    }
  };

  return (
    <div className="card">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-secondary-900 mb-2">
          SQL Query Editor
        </h2>
        <p className="text-secondary-600">
          Write and execute SQL queries to explore your data
        </p>
      </div>

      {/* Available Tables */}
      {availableTables.length > 0 && (
        <div className="mb-4 p-3 bg-secondary-50 rounded-lg">
          <h3 className="text-sm font-medium text-secondary-700 mb-2">
            Available Tables:
          </h3>
          <div className="flex flex-wrap gap-2">
            {availableTables.map((table) => (
              <span
                key={table.name}
                className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-primary-100 text-primary-800"
              >
                {table.name} ({table.row_count} rows)
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Sample Queries */}
      <div className="mb-4">
        <h3 className="text-sm font-medium text-secondary-700 mb-2">
          Sample Queries:
        </h3>
        <div className="flex flex-wrap gap-2">
          {sampleQueries.map((sampleQuery, index) => (
            <button
              key={index}
              onClick={() => handleLoadQuery(sampleQuery)}
              className="text-xs px-3 py-1 bg-secondary-200 hover:bg-secondary-300 text-secondary-700 rounded-md transition-colors duration-200"
            >
              {sampleQuery}
            </button>
          ))}
        </div>
      </div>

      {/* Query Editor */}
      <div className="mb-4">
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter your SQL query here...&#10;Example: SELECT * FROM table_name LIMIT 10&#10;Press Ctrl+Enter to execute"
            className="sql-editor w-full h-48 resize-none"
            disabled={executing}
          />
          
          {/* Line numbers */}
          <div className="absolute left-0 top-0 w-12 h-full bg-secondary-800 text-secondary-400 text-xs font-mono p-2 select-none">
            {query.split('\n').map((_, index) => (
              <div key={index} className="text-right">
                {index + 1}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-2 mb-4">
        <button
          onClick={handleExecuteQuery}
          disabled={executing || !query.trim()}
          className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {executing ? (
            <div className="loading-spinner w-4 h-4"></div>
          ) : (
            <Play className="w-4 h-4" />
          )}
          <span>{executing ? 'Executing...' : 'Execute Query'}</span>
        </button>

        <button
          onClick={handleSaveQuery}
          disabled={!query.trim()}
          className="btn-secondary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save className="w-4 h-4" />
          <span>Save Query</span>
        </button>

        <button
          onClick={handleClearQuery}
          disabled={!query.trim()}
          className="btn-secondary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Clear</span>
        </button>
      </div>

      {/* Query History */}
      {queryHistory.length > 0 && (
        <div className="border-t border-secondary-200 pt-4">
          <h3 className="text-sm font-medium text-secondary-700 mb-2">
            Recent Queries:
          </h3>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {queryHistory.map((item, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-secondary-50 rounded-md"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-mono text-secondary-900 truncate">
                    {item.query}
                  </p>
                  <p className="text-xs text-secondary-500">
                    {item.timestamp.toLocaleTimeString()}
                  </p>
                </div>
                <button
                  onClick={() => setQuery(item.query)}
                  className="ml-2 text-xs px-2 py-1 bg-primary-100 hover:bg-primary-200 text-primary-700 rounded transition-colors duration-200"
                >
                  Load
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Keyboard Shortcuts */}
      <div className="mt-4 text-xs text-secondary-500">
        <p>Keyboard shortcuts: Ctrl+Enter to execute query</p>
      </div>
    </div>
  );
};

export default SqlEditor; 