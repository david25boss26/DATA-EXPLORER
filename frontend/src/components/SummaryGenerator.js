import React, { useState } from 'react';
import { Brain, Sparkles, BarChart3, TrendingUp, RefreshCw } from 'lucide-react';
import { generateSummary } from '../services/api';

const SummaryGenerator = ({ availableTables = [] }) => {
  const [selectedTable, setSelectedTable] = useState('');
  const [summaryType, setSummaryType] = useState('overview');
  const [sampleSize, setSampleSize] = useState(100);
  const [generating, setGenerating] = useState(false);
  const [summary, setSummary] = useState('');
  const [error, setError] = useState('');

  const summaryTypes = [
    {
      id: 'overview',
      name: 'General Summary',
      description: 'Comprehensive overview of the dataset',
      icon: Brain,
      color: 'text-blue-600'
    },
    {
      id: 'statistical',
      name: 'Statistical Analysis',
      description: 'Quantitative insights and patterns',
      icon: BarChart3,
      color: 'text-green-600'
    },
    {
      id: 'insights',
      name: 'Business Insights',
      description: 'Actionable business recommendations',
      icon: TrendingUp,
      color: 'text-purple-600'
    }
  ];

  const handleGenerateSummary = async () => {
    if (!selectedTable) {
      setError('Please select a table to analyze');
      return;
    }

    setGenerating(true);
    setError('');
    setSummary('');

    try {
      const result = await generateSummary(selectedTable, sampleSize, summaryType, 'mock');
      
      if (result.success) {
        setSummary(result.summary);
      } else {
        setError(result.error || 'Failed to generate summary');
      }
    } catch (error) {
      setError(error.response?.data?.detail || error.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleRefresh = () => {
    setSummary('');
    setError('');
  };

  const formatSummary = (text) => {
    // Split by double newlines to identify paragraphs
    const paragraphs = text.split('\n\n');
    
    return paragraphs.map((paragraph, index) => (
      <p key={index} className="mb-4 leading-relaxed">
        {paragraph.trim()}
      </p>
    ));
  };

  return (
    <div className="card">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-secondary-900 mb-2">
          AI-Powered Data Summary
        </h2>
        <p className="text-secondary-600">
          Generate intelligent insights and summaries of your data using local LLM
        </p>
      </div>

      {/* Configuration */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {/* Table Selection */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            Select Table
          </label>
          <select
            value={selectedTable}
            onChange={(e) => setSelectedTable(e.target.value)}
            className="input-field"
            disabled={generating}
          >
            <option value="">Choose a table...</option>
            {availableTables.map((table) => (
              <option key={table.name} value={table.name}>
                {table.name} ({table.row_count} rows)
              </option>
            ))}
          </select>
        </div>

        {/* Summary Type */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            Summary Type
          </label>
          <select
            value={summaryType}
            onChange={(e) => setSummaryType(e.target.value)}
            className="input-field"
            disabled={generating}
          >
            {summaryTypes.map((type) => (
              <option key={type.id} value={type.id}>
                {type.name}
              </option>
            ))}
          </select>
        </div>

        {/* Sample Size */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            Sample Size
          </label>
          <select
            value={sampleSize}
            onChange={(e) => setSampleSize(Number(e.target.value))}
            className="input-field"
            disabled={generating}
          >
            <option value={50}>50 rows</option>
            <option value={100}>100 rows</option>
            <option value={200}>200 rows</option>
            <option value={500}>500 rows</option>
          </select>
        </div>
      </div>

      {/* Summary Type Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {summaryTypes.map((type) => (
          <div
            key={type.id}
            className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
              summaryType === type.id
                ? 'border-primary-500 bg-primary-50'
                : 'border-secondary-200 hover:border-secondary-300'
            }`}
            onClick={() => setSummaryType(type.id)}
          >
            <div className="flex items-center space-x-3">
              <type.icon className={`w-6 h-6 ${type.color}`} />
              <div>
                <h3 className="font-medium text-secondary-900">{type.name}</h3>
                <p className="text-sm text-secondary-600">{type.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3 mb-6">
        <button
          onClick={handleGenerateSummary}
          disabled={generating || !selectedTable}
          className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {generating ? (
            <div className="loading-spinner w-4 h-4"></div>
          ) : (
            <Sparkles className="w-4 h-4" />
          )}
          <span>{generating ? 'Generating...' : 'Generate Summary'}</span>
        </button>

        <button
          onClick={handleRefresh}
          disabled={generating}
          className="btn-secondary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Clear</span>
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            <p className="text-red-800 font-medium">Error</p>
          </div>
          <p className="text-red-700 mt-1">{error}</p>
        </div>
      )}

      {/* Summary Display */}
      {summary && (
        <div className="summary-card">
          <div className="flex items-center space-x-2 mb-4">
            <Brain className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-secondary-900">
              AI-Generated Summary
            </h3>
          </div>
          
          <div className="prose prose-sm max-w-none">
            <div className="text-secondary-800 whitespace-pre-wrap">
              {formatSummary(summary)}
            </div>
          </div>
          
          <div className="mt-4 pt-4 border-t border-primary-200">
            <div className="flex items-center justify-between text-sm text-secondary-600">
              <span>
                Generated using {summaryTypes.find(t => t.id === summaryType)?.name}
              </span>
              <span>
                Sample size: {sampleSize} rows
              </span>
            </div>
          </div>
        </div>
      )}

      {/* No Data State */}
      {!summary && !error && !generating && (
        <div className="text-center py-12">
          <Brain className="w-16 h-16 text-secondary-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-secondary-900 mb-2">
            Ready to Generate Insights
          </h3>
          <p className="text-secondary-600 max-w-md mx-auto">
            Select a table and choose your preferred summary type to get started with AI-powered data analysis.
          </p>
        </div>
      )}
    </div>
  );
};

export default SummaryGenerator; 