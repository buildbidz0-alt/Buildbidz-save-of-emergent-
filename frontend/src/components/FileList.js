import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../App';
import { 
  FileText, Download, Eye, Image, FileIcon, 
  Paperclip, Calendar, User
} from 'lucide-react';
import axios from 'axios';

const FileList = ({ fileType, itemId, title = "Attachments", showUploader = false }) => {
  const { API } = useContext(AuthContext);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (itemId) {
      fetchFiles();
    }
  }, [itemId]);

  const fetchFiles = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/files/${fileType}/${itemId}`);
      setFiles(response.data);
    } catch (error) {
      console.error('Failed to fetch files:', error);
      setError('Failed to load attachments');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (fileId, filename) => {
    try {
      const response = await axios.get(`${API}/download/${fileType}/${fileId}`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download file');
    }
  };

  const getFileIcon = (contentType, filename) => {
    if (contentType.startsWith('image/')) {
      return <Image className="h-5 w-5 text-blue-400" />;
    } else if (contentType === 'application/pdf') {
      return <FileText className="h-5 w-5 text-red-400" />;
    } else if (contentType.includes('document') || contentType.includes('word')) {
      return <FileIcon className="h-5 w-5 text-blue-600" />;
    } else if (contentType.includes('sheet') || contentType.includes('excel')) {
      return <FileIcon className="h-5 w-5 text-green-600" />;
    } else {
      return <Paperclip className="h-5 w-5 text-gray-400" />;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-gray-300 flex items-center">
          <Paperclip className="h-4 w-4 mr-2" />
          {title}
        </h4>
        <div className="flex items-center justify-center py-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-orange-500"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-gray-300 flex items-center">
          <Paperclip className="h-4 w-4 mr-2" />
          {title}
        </h4>
        <div className="text-sm text-red-400">{error}</div>
      </div>
    );
  }

  if (files.length === 0) {
    return (
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-gray-300 flex items-center">
          <Paperclip className="h-4 w-4 mr-2" />
          {title}
        </h4>
        <div className="text-sm text-gray-500">No attachments</div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-gray-300 flex items-center">
        <Paperclip className="h-4 w-4 mr-2" />
        {title} ({files.length})
      </h4>
      
      <div className="space-y-2">
        {files.map((file) => (
          <div key={file.id} className="bg-gray-700 rounded-lg p-3 hover:bg-gray-600 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3 flex-1 min-w-0">
                {getFileIcon(file.content_type, file.filename)}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">
                    {file.filename}
                  </p>
                  <div className="flex items-center space-x-4 text-xs text-gray-400">
                    <span>{formatFileSize(file.size)}</span>
                    <span className="flex items-center">
                      <Calendar className="h-3 w-3 mr-1" />
                      {formatDate(file.uploaded_at)}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleDownload(file.id, file.filename)}
                  className="text-orange-400 hover:text-orange-300 p-1 rounded"
                  title="Download file"
                >
                  <Download className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FileList;