import React, { useState, useEffect, useContext, useRef } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { AuthContext } from '../App';
import { 
  Building2, ArrowLeft, Send, MessageCircle, Users, Clock, 
  CheckCircle, Phone, Mail, Paperclip, X, Download, FileText,
  Image, Trash2
} from 'lucide-react';
import axios from 'axios';

const ChatPage = () => {
  const { user, API } = useContext(AuthContext);
  const [searchParams] = useSearchParams();
  const jobId = searchParams.get('job_id');
  
  const [chats, setChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchChats();
    if (jobId) {
      selectChatByJobId(jobId);
    }
    
    // Auto-refresh chat list every 10 seconds
    const chatListInterval = setInterval(fetchChats, 10000);
    return () => clearInterval(chatListInterval);
  }, [jobId]);

  useEffect(() => {
    if (selectedChat) {
      fetchMessages();
      markChatAsRead();
      
      // Auto-refresh messages every 2 seconds for real-time feel
      const interval = setInterval(fetchMessages, 2000);
      return () => clearInterval(interval);
    }
  }, [selectedChat]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchChats = async () => {
    try {
      const response = await axios.get(`${API}/chats`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setChats(response.data);
    } catch (error) {
      console.error('Failed to fetch chats:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectChatByJobId = (jobId) => {
    const chat = chats.find(c => c.job_id === jobId);
    if (chat) {
      setSelectedChat(chat);
    }
  };

  const fetchMessages = async () => {
    if (!selectedChat) return;
    
    try {
      const response = await axios.get(`${API}/jobs/${selectedChat.job_id}/chat`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setMessages(response.data);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    }
  };

  const markChatAsRead = async () => {
    if (!selectedChat) return;
    
    try {
      await axios.post(`${API}/chats/${selectedChat.job_id}/mark-read`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      // Update local chat data
      setChats(chats.map(chat => 
        chat.job_id === selectedChat.job_id 
          ? { ...chat, unread_count: 0 }
          : chat
      ));
    } catch (error) {
      console.error('Failed to mark chat as read:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if ((!newMessage.trim() && selectedFiles.length === 0) || !selectedChat || sending) return;

    setSending(true);
    try {
      if (selectedFiles.length > 0) {
        // Send message with files using FormData
        const formData = new FormData();
        formData.append('message', newMessage.trim() || 'File attachment');
        
        selectedFiles.forEach((file) => {
          formData.append('files', file);
        });

        await axios.post(`${API}/jobs/${selectedChat.job_id}/chat/with-files`, formData, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            // Don't set Content-Type for FormData, let browser set it with boundary
          }
        });
      } else {
        // Send text-only message
        await axios.post(`${API}/jobs/${selectedChat.job_id}/chat`, {
          message: newMessage.trim()
        });
      }
      
      setNewMessage('');
      setSelectedFiles([]);
      setShowFileUpload(false);
      // Immediately refresh messages after sending
      await fetchMessages();
      fetchChats(); // Refresh chat list to update last message
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    const validFiles = [];
    
    for (const file of files) {
      // Validate file type (PDF and JPG only)
      const fileExtension = file.name.split('.').pop().toLowerCase();
      if (!['pdf', 'jpg', 'jpeg'].includes(fileExtension)) {
        alert(`File "${file.name}" is not supported. Only PDF and JPG files are allowed.`);
        continue;
      }
      
      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        alert(`File "${file.name}" is too large. Maximum size is 10MB.`);
        continue;
      }
      
      validFiles.push(file);
    }
    
    setSelectedFiles([...selectedFiles, ...validFiles]);
    if (validFiles.length > 0) {
      setShowFileUpload(true);
    }
  };

  const removeFile = (index) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);
    if (newFiles.length === 0) {
      setShowFileUpload(false);
    }
  };

  const deleteMessage = async (messageId) => {
    if (!window.confirm('Are you sure you want to delete this message? This action cannot be undone.')) {
      return;
    }

    try {
      await axios.delete(`${API}/messages/${messageId}`);
      // Refresh messages after deletion
      await fetchMessages();
      fetchChats(); // Refresh chat list
    } catch (error) {
      console.error('Failed to delete message:', error);
      alert('Failed to delete message. Please try again.');
    }
  };

  const downloadFile = async (fileId, filename) => {
    try {
      const response = await axios.get(`${API}/download/chat/${fileId}`, {
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
      console.error('Failed to download file:', error);
      alert('Failed to download file. Please try again.');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (filename) => {
    const extension = filename.split('.').pop().toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif'].includes(extension)) {
      return <Image className="h-4 w-4" />;
    } else if (extension === 'pdf') {
      return <FileText className="h-4 w-4" />;
    }
    return <FileText className="h-4 w-4" />;
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Navigation */}
      <nav className="glass border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link to="/dashboard" className="flex items-center text-gray-400 hover:text-white mr-8">
                <ArrowLeft className="h-5 w-5 mr-2" />
                Dashboard
              </Link>
              <div className="flex items-center space-x-3">
                <MessageCircle className="h-8 w-8 text-orange-500" />
                <span className="text-xl font-bold text-white">Messages</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="flex h-screen">
        {/* Chat List Sidebar */}
        <div className="w-1/3 border-r border-gray-700 glass">
          <div className="p-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">Active Chats</h2>
          </div>
          
          <div className="overflow-y-auto h-full">
            {chats.length === 0 ? (
              <div className="p-8 text-center">
                <MessageCircle className="h-16 w-16 text-gray-500 mx-auto mb-4" />
                <p className="text-gray-400">No active chats</p>
                <p className="text-sm text-gray-500 mt-2">
                  Chats become available after a job is awarded
                </p>
              </div>
            ) : (
              chats.map((chat) => (
                <div
                  key={chat.job_id}
                  onClick={() => setSelectedChat(chat)}
                  className={`p-4 border-b border-gray-700 cursor-pointer hover:bg-gray-800 ${
                    selectedChat?.job_id === chat.job_id ? 'bg-gray-800 border-l-4 border-orange-500' : ''
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-white truncate">{chat.job_title}</h3>
                    {chat.unread_count > 0 && (
                      <span className="bg-orange-500 text-white text-xs rounded-full px-2 py-1 min-w-[20px] text-center">
                        {chat.unread_count}
                      </span>
                    )}
                  </div>
                  
                  {chat.last_message && (
                    <p className="text-sm text-gray-400 truncate mb-1">
                      {chat.last_message}
                    </p>
                  )}
                  
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{chat.message_count} messages</span>
                    {chat.last_message_at && (
                      <span>{formatTime(chat.last_message_at)}</span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {selectedChat ? (
            <>
              {/* Chat Header */}
              <div className="p-4 border-b border-gray-700 glass">
                <h2 className="text-lg font-semibold text-white mb-1">
                  {selectedChat.job_title}
                </h2>
                <div className="flex items-center text-sm text-gray-400">
                  <MessageCircle className="h-4 w-4 mr-1" />
                  <span>{selectedChat.message_count} messages</span>
                </div>
              </div>

              {/* Messages Area */}
              <div className="flex-1 p-4 overflow-y-auto bg-gray-900">
                {messages.length === 0 ? (
                  <div className="text-center py-8">
                    <MessageCircle className="h-16 w-16 text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-400">No messages yet</p>
                    <p className="text-sm text-gray-500">Start the conversation!</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${
                          message.sender_id === user.id ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        <div
                          className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg relative group ${
                            message.sender_id === user.id
                              ? 'bg-orange-600 text-white'
                              : 'bg-gray-700 text-white'
                          }`}
                        >
                          {message.sender_id !== user.id && message.sender_info && (
                            <div className="text-xs opacity-75 mb-1">
                              {message.sender_info.company_name} ({message.sender_info.role})
                            </div>
                          )}
                          
                          {/* Message text */}
                          {message.message && (
                            <p className="text-sm mb-2">{message.message}</p>
                          )}
                          
                          {/* File attachments */}
                          {message.file_attachments && message.file_attachments.length > 0 && (
                            <div className="space-y-2 mb-2">
                              {message.file_attachments.map((file, index) => (
                                <div
                                  key={index}
                                  className="flex items-center space-x-2 p-2 bg-black bg-opacity-20 rounded border"
                                >
                                  {getFileIcon(file.filename)}
                                  <div className="flex-1 min-w-0">
                                    <p className="text-xs font-medium truncate">
                                      {file.filename}
                                    </p>
                                    <p className="text-xs opacity-75">
                                      {formatFileSize(file.size)}
                                    </p>
                                  </div>
                                  <button
                                    onClick={() => downloadFile(file.id, file.filename)}
                                    className="text-white hover:text-orange-300 transition-colors"
                                  >
                                    <Download className="h-4 w-4" />
                                  </button>
                                </div>
                              ))}
                            </div>
                          )}
                          
                          <div className="flex items-center justify-between">
                            <p className="text-xs opacity-75">
                              {formatTime(message.created_at)}
                            </p>
                            
                            {/* Delete button for own messages */}
                            {message.sender_id === user.id && (
                              <button
                                onClick={() => deleteMessage(message.id)}
                                className="opacity-0 group-hover:opacity-100 ml-2 text-red-300 hover:text-red-200 transition-all"
                                title="Delete message"
                              >
                                <Trash2 className="h-3 w-3" />
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>

              {/* Message Input */}
              <div className="p-4 border-t border-gray-700 glass">
                {/* File Upload Area */}
                {showFileUpload && (
                  <div className="mb-4 p-3 bg-gray-800 rounded-lg border border-gray-600">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-white">Selected Files</span>
                      <button
                        onClick={() => {
                          setSelectedFiles([]);
                          setShowFileUpload(false);
                        }}
                        className="text-gray-400 hover:text-white"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                    <div className="space-y-2">
                      {selectedFiles.map((file, index) => (
                        <div key={index} className="flex items-center space-x-2 p-2 bg-gray-700 rounded">
                          {getFileIcon(file.name)}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate">{file.name}</p>
                            <p className="text-xs text-gray-400">{formatFileSize(file.size)}</p>
                          </div>
                          <button
                            onClick={() => removeFile(index)}
                            className="text-red-400 hover:text-red-300"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <form onSubmit={sendMessage} className="flex space-x-2">
                  <div className="flex-1 flex space-x-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder={selectedFiles.length > 0 ? "Add a message (optional)..." : "Type your message..."}
                      className="flex-1 px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      disabled={sending}
                    />
                    
                    {/* File upload button */}
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileSelect}
                      multiple
                      accept=".pdf,.jpg,.jpeg"
                      className="hidden"
                    />
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg transition-colors"
                      disabled={sending}
                      title="Attach files (PDF, JPG only)"
                    >
                      <Paperclip className="h-5 w-5" />
                    </button>
                  </div>
                  
                  <button
                    type="submit"
                    disabled={(!newMessage.trim() && selectedFiles.length === 0) || sending}
                    className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    {sending ? (
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    ) : (
                      <Send className="h-5 w-5" />
                    )}
                  </button>
                </form>

                {/* File upload instructions */}
                <div className="mt-2 text-xs text-gray-500">
                  <p>📎 You can attach PDF and JPG files (max 10MB each)</p>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center bg-gray-900">
              <div className="text-center">
                <MessageCircle className="h-20 w-20 text-gray-500 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">Select a chat</h3>
                <p className="text-gray-400">Choose a conversation from the sidebar to start messaging</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatPage;