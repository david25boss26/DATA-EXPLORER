import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, FileSpreadsheet, FileJson } from 'lucide-react';
import { uploadFile } from '../services/api';

const FileUpload = ({ onUploadSuccess, onUploadError }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setUploadProgress(0);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 100);

      const result = await uploadFile(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      setTimeout(() => {
        setUploading(false);
        setUploadProgress(0);
        onUploadSuccess(result);
      }, 500);

    } catch (error) {
      setUploading(false);
      setUploadProgress(0);
      onUploadError(error.response?.data?.detail || error.message);
    }
  }, [onUploadSuccess, onUploadError]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    multiple: false,
  });

  const getFileIcon = (fileName) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'csv':
        return <FileSpreadsheet className="w-8 h-8 text-green-600" />;
      case 'json':
        return <FileJson className="w-8 h-8 text-yellow-600" />;
      case 'pdf':
        return <FileText className="w-8 h-8 text-red-600" />;
      case 'xlsx':
      case 'xls':
        return <FileSpreadsheet className="w-8 h-8 text-blue-600" />;
      default:
        return <FileText className="w-8 h-8 text-gray-600" />;
    }
  };

  return (
    <div className="card">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-secondary-900 mb-2">
          Upload Data File
        </h2>
        <p className="text-secondary-600">
          Upload CSV, JSON, PDF, or Excel files to analyze with AI-powered insights
        </p>
      </div>

      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${
          uploading ? 'pointer-events-none opacity-50' : ''
        }`}
      >
        <input {...getInputProps()} />
        
        {uploading ? (
          <div className="space-y-4">
            <div className="loading-spinner mx-auto"></div>
            <div className="text-secondary-600">
              <p className="font-medium">Uploading file...</p>
              <div className="w-full bg-secondary-200 rounded-full h-2 mt-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <p className="text-sm mt-1">{uploadProgress}%</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <Upload className="w-12 h-12 text-secondary-400 mx-auto" />
            <div>
              <p className="text-lg font-medium text-secondary-900">
                {isDragActive ? 'Drop the file here' : 'Drag & drop a file here'}
              </p>
              <p className="text-secondary-600 mt-1">or click to browse</p>
            </div>
            
            <div className="flex flex-wrap justify-center gap-4 mt-4">
              <div className="flex items-center space-x-2 text-sm text-secondary-600">
                <FileSpreadsheet className="w-4 h-4" />
                <span>CSV</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-secondary-600">
                <FileJson className="w-4 h-4" />
                <span>JSON</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-secondary-600">
                <FileText className="w-4 h-4" />
                <span>PDF</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-secondary-600">
                <FileSpreadsheet className="w-4 h-4" />
                <span>Excel</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 text-sm text-secondary-600">
        <p>Supported formats: CSV, JSON, PDF, Excel (.xlsx, .xls)</p>
        <p>Maximum file size: 100MB</p>
      </div>
    </div>
  );
};

export default FileUpload; 