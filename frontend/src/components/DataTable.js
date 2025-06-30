import React, { useState, useMemo } from 'react';
import { Download, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

const DataTable = ({ data, columns, rowCount }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  const pageSizeOptions = [10, 25, 50, 100];

  // Calculate pagination
  const totalPages = Math.ceil(data.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const currentData = data.slice(startIndex, endIndex);

  // Sorting function
  const sortedData = useMemo(() => {
    if (!sortConfig.key) return currentData;

    return [...currentData].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      if (typeof aValue === 'string') {
        return sortConfig.direction === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
    });
  }, [currentData, sortConfig]);

  const handleSort = (column) => {
    setSortConfig(prev => ({
      key: column,
      direction: prev.key === column && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const handlePageChange = (page) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const handleExportCSV = () => {
    if (!data.length) return;

    const headers = columns.join(',');
    const csvContent = [
      headers,
      ...data.map(row => 
        columns.map(col => {
          const value = row[col];
          // Escape commas and quotes in CSV
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return value;
        }).join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `data_export_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatCellValue = (value) => {
    if (value === null || value === undefined) {
      return <span className="text-secondary-400 italic">null</span>;
    }
    
    if (typeof value === 'boolean') {
      return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          value ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {value ? 'true' : 'false'}
        </span>
      );
    }
    
    if (typeof value === 'number') {
      return <span className="font-mono">{value.toLocaleString()}</span>;
    }
    
    if (typeof value === 'string' && value.length > 50) {
      return (
        <div className="max-w-xs">
          <span className="truncate block" title={value}>
            {value.substring(0, 50)}...
          </span>
        </div>
      );
    }
    
    return <span>{String(value)}</span>;
  };

  if (!data || data.length === 0) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <p className="text-secondary-600">No data to display</p>
          <p className="text-sm text-secondary-500 mt-1">
            Execute a query to see results here
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-semibold text-secondary-900">
            Query Results
          </h2>
          <p className="text-secondary-600">
            {rowCount} rows, {columns.length} columns
          </p>
        </div>
        
        <button
          onClick={handleExportCSV}
          className="btn-secondary flex items-center space-x-2"
        >
          <Download className="w-4 h-4" />
          <span>Export CSV</span>
        </button>
      </div>

      {/* Table */}
      <div className="table-container">
        <table className="table">
          <thead className="table-header">
            <tr>
              {columns.map((column) => (
                <th
                  key={column}
                  className="table-header-cell cursor-pointer hover:bg-secondary-100"
                  onClick={() => handleSort(column)}
                >
                  <div className="flex items-center space-x-1">
                    <span>{column}</span>
                    {sortConfig.key === column && (
                      <span className="text-primary-600">
                        {sortConfig.direction === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="table-body">
            {sortedData.map((row, rowIndex) => (
              <tr key={rowIndex} className="table-row">
                {columns.map((column) => (
                  <td key={column} className="table-cell">
                    {formatCellValue(row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-secondary-600">
              Showing {startIndex + 1} to {Math.min(endIndex, data.length)} of {data.length} results
            </span>
            
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="text-sm border border-secondary-300 rounded px-2 py-1"
            >
              {pageSizeOptions.map(size => (
                <option key={size} value={size}>
                  {size} per page
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-1">
            <button
              onClick={() => handlePageChange(1)}
              disabled={currentPage === 1}
              className="p-1 rounded hover:bg-secondary-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronsLeft className="w-4 h-4" />
            </button>
            
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="p-1 rounded hover:bg-secondary-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            
            <span className="px-3 py-1 text-sm text-secondary-700">
              Page {currentPage} of {totalPages}
            </span>
            
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="p-1 rounded hover:bg-secondary-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
            
            <button
              onClick={() => handlePageChange(totalPages)}
              disabled={currentPage === totalPages}
              className="p-1 rounded hover:bg-secondary-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronsRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataTable; 