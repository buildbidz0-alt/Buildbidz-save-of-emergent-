import React, { useState, useEffect, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import { 
  Building2, LogOut, Plus, TrendingUp, DollarSign, Briefcase,
  Users, Award, Menu, X, Search, Calendar, MapPin, Clock, Phone, Mail,
  Upload, FileText
} from 'lucide-react';
import axios from 'axios';
import FileList from './FileList';

const SalesmanDashboard = () => {
  const { user, logout, API } = useContext(AuthContext);
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [myBids, setMyBids] = useState([]);
  const [awardedProjects, setAwardedProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('jobs');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showBidModal, setShowBidModal] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);

  const [newBid, setNewBid] = useState({
    price_quote: '',
    delivery_estimate: '',
    notes: '',
    company_name: '',
    company_contact_phone: '',
    company_email: '',
    company_gst_number: '',
    company_address: ''
  });

  const [bidFiles, setBidFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchJobs();
    fetchMyBids();
    fetchAwardedProjects();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API}/jobs`);
      setJobs(response.data);
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMyBids = async () => {
    try {
      // For salesman, we need to get bids they've submitted
      const response = await axios.get(`${API}/bids/my`);
      setMyBids(response.data);
    } catch (error) {
      console.error('Failed to fetch my bids:', error);
    }
  };

  const fetchAwardedProjects = async () => {
    try {
      // Get awarded bids for salesman
      const response = await axios.get(`${API}/bids/my`);
      const awardedBids = response.data.filter(bid => bid.status === 'awarded');
      setAwardedProjects(awardedBids);
    } catch (error) {
      console.error('Failed to fetch awarded projects:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleSubmitBid = async (e) => {
    e.preventDefault();
    if (!selectedJob) return;

    setLoading(true);
    try {
      // First submit the bid
      const bidResponse = await axios.post(`${API}/jobs/${selectedJob.id}/salesman-bids`, {
        ...newBid,
        price_quote: parseFloat(newBid.price_quote)
      });
      
      const createdBid = bidResponse.data;
      
      // Upload files if any are selected
      if (bidFiles.length > 0) {
        setUploading(true);
        const formData = new FormData();
        bidFiles.forEach((file) => {
          formData.append('files', file);
        });
        
        try {
          await axios.post(`${API}/upload/bid/${createdBid.id}`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });
        } catch (fileError) {
          console.error('File upload failed:', fileError);
          // Don't fail bid creation if file upload fails
          alert('Bid submitted successfully, but file upload failed. You can upload files later.');
        }
      }
      
      setShowBidModal(false);
      setSelectedJob(null);
      setNewBid({
        price_quote: '',
        delivery_estimate: '',
        notes: '',
        company_name: '',
        company_contact_phone: '',
        company_email: '',
        company_gst_number: '',
        company_address: ''
      });
      setBidFiles([]);
      fetchMyBids();
      alert('Bid submitted successfully!');
    } catch (error) {
      alert('Failed to submit bid: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setLoading(false);
      setUploading(false);
    }
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    const validFiles = files.filter(file => {
      const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 
                         'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                         'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         'text/plain'];
      const maxSize = 10 * 1024 * 1024; // 10MB
      
      if (!validTypes.includes(file.type)) {
        alert(`File ${file.name} is not a supported type`);
        return false;
      }
      if (file.size > maxSize) {
        alert(`File ${file.name} is too large (max 10MB)`);
        return false;
      }
      return true;
    });
    
    setBidFiles(prevFiles => [...prevFiles, ...validFiles]);
  };

  const removeFile = (index) => {
    setBidFiles(prevFiles => prevFiles.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const openBidModal = (job) => {
    setSelectedJob(job);
    setShowBidModal(true);
  };

  const filteredJobs = jobs.filter(job =>
    job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    job.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const navigation = [
    { name: 'Available Jobs', id: 'jobs', icon: Briefcase },
    { name: 'My Bids', id: 'bids', icon: DollarSign },
    { name: 'Awarded Projects', id: 'awarded', icon: Award }
  ];

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Mobile sidebar */}
      <div className={`lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 z-40 flex">
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)}></div>
          <div className="relative flex w-full max-w-xs flex-1 flex-col bg-gray-800">
            <div className="absolute top-0 right-0 -mr-12 pt-2">
              <button
                type="button"
                className="ml-1 flex h-10 w-10 items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                onClick={() => setSidebarOpen(false)}
              >
                <X className="h-6 w-6 text-white" />
              </button>
            </div>
            <div className="h-0 flex-1 overflow-y-auto pt-5 pb-4">
              <div className="flex flex-shrink-0 items-center px-4">
                <Building2 className="h-8 w-8 text-orange-500" />
                <span className="ml-2 text-xl font-bold text-white">BuildBidz Sales</span>
              </div>
              <nav className="mt-5 space-y-1 px-2">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  return (
                    <button
                      key={item.id}
                      onClick={() => {
                        setActiveTab(item.id);
                        setSidebarOpen(false);
                      }}
                      className={`group flex items-center w-full px-2 py-2 text-base font-medium rounded-md transition-colors ${
                        activeTab === item.id
                          ? 'bg-orange-600 text-white'
                          : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                      }`}
                    >
                      <Icon className="h-5 w-5 mr-3" />
                      {item.name}
                    </button>
                  );
                })}
              </nav>
              <div className="px-4 py-4 border-t border-gray-700 mt-4">
                <div className="flex items-center">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-white">{user?.company_name}</p>
                    <p className="text-xs text-gray-400 capitalize">{user?.role}</p>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="ml-3 text-gray-400 hover:text-white flex items-center"
                  >
                    <LogOut className="h-5 w-5 mr-2" />
                    <span className="text-sm">Logout</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="glass border-r border-gray-700 flex min-h-0 flex-1 flex-col">
          <div className="flex flex-1 flex-col overflow-y-auto pt-5 pb-4">
            <div className="flex flex-shrink-0 items-center px-4">
              <Building2 className="h-8 w-8 text-orange-500" />
              <span className="ml-2 text-xl font-bold text-white">BuildBidz Sales</span>
            </div>
            <nav className="mt-5 flex-1 space-y-1 px-2">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`group flex items-center w-full px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                      activeTab === item.id
                        ? 'bg-orange-600 text-white'
                        : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                    }`}
                  >
                    <Icon className="h-5 w-5 mr-3" />
                    {item.name}
                  </button>
                );
              })}
            </nav>
            <div className="px-4 py-4 border-t border-gray-700">
              <div className="flex items-center">
                <div className="flex-1">
                  <p className="text-sm font-medium text-white">{user?.company_name}</p>
                  <p className="text-xs text-gray-400 capitalize">{user?.role}</p>
                </div>
                <button
                  onClick={handleLogout}
                  className="ml-3 text-gray-400 hover:text-white"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64 flex flex-col flex-1">
        {/* Top navigation */}
        <div className="sticky top-0 z-10 glass border-b border-gray-700 pl-1 pt-1 sm:pl-3 sm:pt-3 lg:hidden">
          <button
            type="button"
            className="-ml-0.5 -mt-0.5 h-12 w-12 inline-flex items-center justify-center rounded-md text-gray-500 hover:text-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-orange-500"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>
        </div>

        <main className="flex-1">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              {/* Header */}
              <div className="mb-8">
                <h1 className="text-3xl font-bold text-white">
                  Sales Dashboard
                </h1>
                <p className="text-gray-400 mt-2">
                  Submit bids on behalf of unregistered companies
                </p>
              </div>

              {/* Search Bar */}
              <div className="mb-6">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder={`Search ${activeTab === 'jobs' ? 'jobs' : 'bids'}...`}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  />
                </div>
              </div>

              {/* Content */}
              {activeTab === 'jobs' ? (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-white">Available Jobs</h2>
                  <div className="grid gap-6">
                    {filteredJobs.map((job) => (
                      <div key={job.id} className="glass rounded-lg p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-white mb-2">{job.title}</h3>
                            <p className="text-gray-400 mb-3">{job.description}</p>
                            
                            {/* Job File Attachments */}
                            <div className="mb-3">
                              <FileList 
                                fileType="job" 
                                itemId={job.id} 
                                title="Job Attachments"
                              />
                            </div>
                            <div className="flex items-center space-x-4 text-sm text-gray-400">
                              <span className="flex items-center">
                                <MapPin className="h-4 w-4 mr-1" />
                                {job.location}
                              </span>
                              <span className="flex items-center">
                                <Clock className="h-4 w-4 mr-1" />
                                {job.delivery_timeline}
                              </span>
                              {job.budget_range && (
                                <span className="flex items-center">
                                  <DollarSign className="h-4 w-4 mr-1" />
                                  {job.budget_range}
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center space-x-3">
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                              job.status === 'open' ? 'bg-green-600 text-white' : 'bg-gray-600 text-white'
                            }`}>
                              {job.status}
                            </span>
                            {job.status === 'open' && (
                              <button
                                onClick={() => openBidModal(job)}
                                className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
                              >
                                Submit Bid
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : activeTab === 'bids' ? (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-white">My Submitted Bids</h2>
                  <div className="grid gap-6">
                    {myBids.map((bid) => (
                      <div key={bid.id} className="glass rounded-lg p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-white mb-2">
                              {bid.job_info?.title || 'Job Title'}
                            </h3>
                            <div className="flex items-center space-x-4 text-sm mb-3">
                              <span className="text-orange-400 font-semibold">₹{bid.price_quote?.toLocaleString()}</span>
                              <span className="text-gray-400">{bid.delivery_estimate}</span>
                            </div>
                            {bid.company_represented && (
                              <div className="bg-gray-700 rounded-lg p-3 mb-3">
                                <h4 className="text-sm font-medium text-white mb-2">Bid placed for:</h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-gray-300">
                                  <div>
                                    <span className="font-medium">Company:</span> {bid.company_represented.company_name}
                                  </div>
                                  <div>
                                    <span className="font-medium">Phone:</span> {bid.company_represented.contact_phone}
                                  </div>
                                  {bid.company_represented.email && (
                                    <div>
                                      <span className="font-medium">Email:</span> {bid.company_represented.email}
                                    </div>
                                  )}
                                  {bid.company_represented.gst_number && (
                                    <div>
                                      <span className="font-medium">GST:</span> {bid.company_represented.gst_number}
                                    </div>
                                  )}
                                </div>
                                {bid.company_represented.address && (
                                  <div className="mt-2 text-xs text-gray-300">
                                    <span className="font-medium">Address:</span> {bid.company_represented.address}
                                  </div>
                                )}
                              </div>
                            )}
                            {bid.notes && (
                              <div className="text-sm text-gray-400 mb-2">
                                <span className="font-medium">Notes:</span> {bid.notes}
                              </div>
                            )}
                            <div className="text-xs text-gray-500">
                              Submitted on {new Date(bid.created_at).toLocaleDateString()}
                            </div>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            bid.status === 'submitted' ? 'bg-blue-600 text-white' : 
                            bid.status === 'awarded' ? 'bg-green-600 text-white' : 
                            'bg-red-600 text-white'
                          }`}>
                            {bid.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-white">Awarded Projects</h2>
                  {awardedProjects.length === 0 ? (
                    <div className="glass rounded-lg p-12 text-center">
                      <Award className="h-16 w-16 text-gray-500 mx-auto mb-4" />
                      <h3 className="text-xl font-semibold text-white mb-2">No awarded projects yet</h3>
                      <p className="text-gray-400">Your awarded bids will appear here when buyers select your proposals</p>
                    </div>
                  ) : (
                    <div className="grid gap-6">
                      {awardedProjects.map((project) => (
                        <div key={project.id} className="glass rounded-lg p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-2">
                                <Award className="h-5 w-5 text-green-400" />
                                <h3 className="text-lg font-semibold text-white">
                                  {project.job_info?.title || 'Project Title'}
                                </h3>
                                <span className="px-2 py-1 bg-green-600 text-white text-xs font-semibold rounded-full">
                                  AWARDED
                                </span>
                              </div>
                              <div className="flex items-center space-x-4 text-sm mb-3">
                                <span className="text-orange-400 font-semibold">₹{project.price_quote?.toLocaleString()}</span>
                                <span className="text-gray-400">{project.delivery_estimate}</span>
                                <span className="text-green-400">• {project.job_info?.category}</span>
                              </div>
                              {project.company_represented && (
                                <div className="bg-gray-700 rounded-lg p-3 mb-3">
                                  <h4 className="text-sm font-medium text-white mb-2">Project awarded to:</h4>
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-gray-300">
                                    <div>
                                      <span className="font-medium">Company:</span> {project.company_represented.company_name}
                                    </div>
                                    <div>
                                      <span className="font-medium">Phone:</span> {project.company_represented.contact_phone}
                                    </div>
                                  </div>
                                </div>
                              )}
                              <div className="text-xs text-gray-500">
                                Awarded on {new Date(project.updated_at || project.created_at).toLocaleDateString()}
                              </div>
                            </div>
                          </div>
                          {project.notes && (
                            <div className="border-t border-gray-600 pt-3 mt-3">
                              <p className="text-sm text-gray-300">
                                <span className="font-medium">Project Notes:</span> {project.notes}
                              </p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </main>
      </div>

      {/* Bid Submission Modal */}
      {showBidModal && selectedJob && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-900 bg-opacity-75 transition-opacity" onClick={() => setShowBidModal(false)}></div>
            
            <div className="inline-block align-bottom bg-gray-800 rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full sm:p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-2xl font-bold text-white">Submit Bid for {selectedJob.title}</h3>
                <button
                  onClick={() => setShowBidModal(false)}
                  className="text-gray-400 hover:text-white"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              <form onSubmit={handleSubmitBid} className="space-y-6">
                {/* Company Details */}
                <div className="bg-gray-700 rounded-lg p-4">
                  <h4 className="text-lg font-semibold text-white mb-4">Company Details</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-gray-300 text-sm font-medium mb-2">
                        Company Name *
                      </label>
                      <input
                        type="text"
                        value={newBid.company_name}
                        onChange={(e) => setNewBid({...newBid, company_name: e.target.value})}
                        required
                        className="w-full px-4 py-3 bg-gray-600 border border-gray-500 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                        placeholder="Enter company name"
                      />
                    </div>
                    <div>
                      <label className="block text-gray-300 text-sm font-medium mb-2">
                        Contact Phone *
                      </label>
                      <input
                        type="tel"
                        value={newBid.company_contact_phone}
                        onChange={(e) => setNewBid({...newBid, company_contact_phone: e.target.value})}
                        required
                        className="w-full px-4 py-3 bg-gray-600 border border-gray-500 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                        placeholder="Enter contact phone"
                      />
                    </div>
                    <div>
                      <label className="block text-gray-300 text-sm font-medium mb-2">
                        Email
                      </label>
                      <input
                        type="email"
                        value={newBid.company_email}
                        onChange={(e) => setNewBid({...newBid, company_email: e.target.value})}
                        className="w-full px-4 py-3 bg-gray-600 border border-gray-500 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                        placeholder="Enter email"
                      />
                    </div>
                    <div>
                      <label className="block text-gray-300 text-sm font-medium mb-2">
                        GST Number *
                      </label>
                      <input
                        type="text"
                        value={newBid.company_gst_number}
                        onChange={(e) => setNewBid({...newBid, company_gst_number: e.target.value})}
                        required
                        pattern="[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}"
                        title="Please enter a valid 15-digit GST number (e.g., 27ABCDE1234F1Z5)"
                        className="w-full px-4 py-3 bg-gray-600 border border-gray-500 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                        placeholder="Enter GST number (e.g., 27ABCDE1234F1Z5)"
                      />
                    </div>
                    <div className="md:col-span-2">
                      <label className="block text-gray-300 text-sm font-medium mb-2">
                        Business Address *
                      </label>
                      <textarea
                        value={newBid.company_address}
                        onChange={(e) => setNewBid({...newBid, company_address: e.target.value})}
                        required
                        rows={2}
                        className="w-full px-4 py-3 bg-gray-600 border border-gray-500 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                        placeholder="Enter complete business address with city, state, and pincode"
                      />
                    </div>
                  </div>
                </div>

                {/* Bid Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      Price Quote (₹) *
                    </label>
                    <input
                      type="number"
                      value={newBid.price_quote}
                      onChange={(e) => setNewBid({...newBid, price_quote: e.target.value})}
                      required
                      className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      placeholder="Enter price quote"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      Delivery Estimate *
                    </label>
                    <input
                      type="text"
                      value={newBid.delivery_estimate}
                      onChange={(e) => setNewBid({...newBid, delivery_estimate: e.target.value})}
                      required
                      className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      placeholder="e.g., 10-15 days"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">
                    Additional Notes
                  </label>
                  <textarea
                    value={newBid.notes}
                    onChange={(e) => setNewBid({...newBid, notes: e.target.value})}
                    rows={3}
                    className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    placeholder="Include any additional information, terms, or conditions"
                  />
                </div>

                {/* File Upload Section */}
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">
                    Attach Files (Optional)
                  </label>
                  <div className="border-2 border-dashed border-gray-600 rounded-lg p-6 text-center hover:border-gray-500 transition-colors">
                    <input
                      type="file"
                      id="salesman-bid-files"
                      multiple
                      accept=".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt,.xls,.xlsx"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <label
                      htmlFor="salesman-bid-files"
                      className="cursor-pointer flex flex-col items-center"
                    >
                      <Upload className="h-12 w-12 text-gray-400 mb-2" />
                      <span className="text-gray-400 mb-1">
                        Click to upload files or drag and drop
                      </span>
                      <span className="text-xs text-gray-500">
                        PDF, JPG, PNG, DOCX, XLSX (Max 10MB each)
                      </span>
                    </label>
                  </div>
                  
                  {/* Selected Files Display */}
                  {bidFiles.length > 0 && (
                    <div className="mt-4 space-y-2">
                      <h4 className="text-sm font-medium text-gray-300">Selected Files:</h4>
                      {bidFiles.map((file, index) => (
                        <div key={index} className="flex items-center justify-between bg-gray-700 rounded-lg p-3">
                          <div className="flex items-center space-x-3">
                            <FileText className="h-5 w-5 text-blue-400" />
                            <div>
                              <p className="text-sm font-medium text-white">{file.name}</p>
                              <p className="text-xs text-gray-400">{formatFileSize(file.size)}</p>
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={() => removeFile(index)}
                            className="text-red-400 hover:text-red-300 p-1"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex justify-end space-x-4">
                  <button
                    type="button"
                    onClick={() => setShowBidModal(false)}
                    className="px-6 py-3 border border-gray-600 text-gray-300 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading || uploading}
                    className="bg-orange-600 hover:bg-orange-700 disabled:bg-orange-600/50 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
                  >
                    {loading ? 'Submitting...' : uploading ? 'Uploading Files...' : 'Submit Bid'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SalesmanDashboard;