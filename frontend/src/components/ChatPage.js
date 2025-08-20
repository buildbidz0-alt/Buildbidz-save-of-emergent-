import React, { useState, useEffect, useContext, useRef } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { AuthContext } from '../App';
import { 
  Building2, ArrowLeft, Send, MessageCircle, Users, Clock, 
  CheckCircle, Phone, Mail
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
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchChats();
    if (jobId) {
      selectChatByJobId(jobId);
    }
  }, [jobId]);

  useEffect(() => {
    if (selectedChat) {
      fetchMessages();
      markChatAsRead();
      
      // Auto-refresh messages every 5 seconds
      const interval = setInterval(fetchMessages, 5000);
      return () => clearInterval(interval);
    }
  }, [selectedChat]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchChats = async () => {
    try {
      const response = await axios.get(`${API}/chats`);
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
      const response = await axios.get(`${API}/jobs/${selectedChat.job_id}/chat`);
      setMessages(response.data);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    }
  };

  const markChatAsRead = async () => {
    if (!selectedChat) return;
    
    try {
      await axios.post(`${API}/chats/${selectedChat.job_id}/mark-read`);
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
    if (!newMessage.trim() || !selectedChat || sending) return;

    setSending(true);
    try {
      await axios.post(`${API}/jobs/${selectedChat.job_id}/chat`, {
        message: newMessage.trim()
      });
      
      setNewMessage('');
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
                          className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
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
                          <p className="text-sm">{message.message}</p>
                          <p className="text-xs opacity-75 mt-1">
                            {formatTime(message.created_at)}
                          </p>
                        </div>
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>

              {/* Message Input */}
              <div className="p-4 border-t border-gray-700 glass">
                <form onSubmit={sendMessage} className="flex space-x-2">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type your message..."
                    className="flex-1 px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    disabled={sending}
                  />
                  <button
                    type="submit"
                    disabled={!newMessage.trim() || sending}
                    className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    {sending ? (
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    ) : (
                      <Send className="h-5 w-5" />
                    )}
                  </button>
                </form>
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