import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../App';
import { 
  Building2, Plus, MapPin, Clock, DollarSign, Filter, Search,
  Calendar, Package, Users, Wrench, ArrowLeft, Upload, X, FileText
} from 'lucide-react';
import axios from 'axios';

const JobsPage = () => {
  const { user, API } = useContext(AuthContext);
  const [jobs, setJobs] = useState([]);
  const [myJobs, setMyJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(user?.role === 'buyer' ? 'my-jobs' : 'browse');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [error, setError] = useState('');

  const [newJob, setNewJob] = useState({
    title: '',
    category: 'material',
    description: '',
    quantity: '',
    location: '',
    delivery_timeline: '',
    budget_range: ''
  });

  const [jobFiles, setJobFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchJobs();
    if (user?.role === 'buyer') {
      fetchMyJobs();
    }
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

  const fetchMyJobs = async () => {
    try {
      const response = await axios.get(`${API}/jobs/my`);
      setMyJobs(response.data);
    } catch (error) {
      console.error('Failed to fetch my jobs:', error);
    }
  };

  const handleCreateJob = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // First create the job
      const jobResponse = await axios.post(`${API}/jobs`, newJob);
      const createdJob = jobResponse.data;
      
      // Upload files if any are selected
      if (jobFiles.length > 0) {
        setUploading(true);
        const formData = new FormData();
        jobFiles.forEach((file) => {
          formData.append('files', file);
        });
        
        try {
          await axios.post(`${API}/upload/job/${createdJob.id}`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });
        } catch (fileError) {
          console.error('File upload failed:', fileError);
          // Don't fail job creation if file upload fails
          alert('Job created successfully, but file upload failed. You can upload files later.');
        }
      }
      
      setShowCreateModal(false);
      setNewJob({
        title: '',
        category: 'material',
        description: '',
        quantity: '',
        location: '',
        delivery_timeline: '',
        budget_range: ''
      });
      setJobFiles([]);
      fetchMyJobs();
      setActiveTab('my-jobs');
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to create job');
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
    
    setJobFiles(prevFiles => [...prevFiles, ...validFiles]);
  };

  const removeFile = (index) => {
    setJobFiles(prevFiles => prevFiles.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const filteredJobs = jobs.filter(job => {
    const matchesSearch = job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || job.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'material': return <Package className="h-5 w-5" />;
      case 'labor': return <Users className="h-5 w-5" />;
      case 'machinery': return <Wrench className="h-5 w-5" />;
      default: return <Package className="h-5 w-5" />;
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'material': return 'bg-blue-600';
      case 'labor': return 'bg-green-600';
      case 'machinery': return 'bg-orange-600';
      default: return 'bg-gray-600';
    }
  };

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
                <Building2 className="h-8 w-8 text-orange-500" />
                <span className="text-xl font-bold text-white">Jobs</span>
              </div>
            </div>
            {user?.role === 'buyer' && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors inline-flex items-center"
              >
                <Plus className="h-5 w-5 mr-2" />
                Post Job
              </button>
            )}
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex space-x-1 mb-8">
          {user?.role === 'buyer' && (
            <button
              onClick={() => setActiveTab('my-jobs')}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                activeTab === 'my-jobs'
                  ? 'bg-orange-600 text-white'
                  : 'glass text-gray-300 hover:text-white'
              }`}
            >
              My Jobs ({myJobs.length})
            </button>
          )}
          <button
            onClick={() => setActiveTab('browse')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'browse'
                ? 'bg-orange-600 text-white'
                : 'glass text-gray-300 hover:text-white'
            }`}
          >
            {user?.role === 'buyer' ? 'All Jobs' : 'Browse Jobs'} ({jobs.length})
          </button>
        </div>

        {/* Search and Filters */}
        {activeTab === 'browse' && (
          <div className="glass rounded-lg p-6 mb-8">
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search jobs by title, description, or location..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  />
                </div>
              </div>
              <div className="lg:w-64">
                <div className="relative">
                  <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <select
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  >
                    <option value="all">All Categories</option>
                    <option value="material">Material</option>
                    <option value="labor">Labor</option>
                    <option value="machinery">Machinery</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Job Listings */}
        {loading ? (
          <div className="grid gap-6">
            {[1,2,3].map((i) => (
              <div key={i} className="glass rounded-lg p-6">
                <div className="animate-pulse">
                  <div className="h-6 bg-gray-700 rounded w-3/4 mb-4"></div>
                  <div className="h-4 bg-gray-700 rounded w-1/2 mb-2"></div>
                  <div className="h-4 bg-gray-700 rounded w-full mb-4"></div>
                  <div className="flex space-x-4">
                    <div className="h-4 bg-gray-700 rounded w-20"></div>
                    <div className="h-4 bg-gray-700 rounded w-24"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid gap-6">
            {activeTab === 'my-jobs' ? (
              myJobs.length === 0 ? (
                <div className="glass rounded-lg p-12 text-center">
                  <Building2 className="h-16 w-16 text-gray-500 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">No jobs posted yet</h3>
                  <p className="text-gray-400 mb-6">Start by posting your first job requirement</p>
                  <button
                    onClick={() => setShowCreateModal(true)}
                    className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors inline-flex items-center"
                  >
                    <Plus className="h-5 w-5 mr-2" />
                    Post Your First Job
                  </button>
                </div>
              ) : (
                myJobs.map((job) => (
                  <JobCard key={job.id} job={job} isOwner={true} />
                ))
              )
            ) : (
              filteredJobs.length === 0 ? (
                <div className="glass rounded-lg p-12 text-center">
                  <Search className="h-16 w-16 text-gray-500 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">No jobs found</h3>
                  <p className="text-gray-400">Try adjusting your search or filters</p>
                </div>
              ) : (
                filteredJobs.map((job) => (
                  <JobCard key={job.id} job={job} isOwner={false} />
                ))
              )
            )}
          </div>
        )}
      </div>

      {/* Create Job Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-900 bg-opacity-75 transition-opacity" onClick={() => setShowCreateModal(false)}></div>
            
            <div className="inline-block align-bottom bg-gray-800 rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full sm:p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-2xl font-bold text-white">Post New Job</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-white"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-6">
                  {error}
                </div>
              )}

              <form onSubmit={handleCreateJob} className="space-y-6">
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">Job Title</label>
                  <input
                    type="text"
                    value={newJob.title}
                    onChange={(e) => setNewJob({...newJob, title: e.target.value})}
                    required
                    className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    placeholder="e.g., TMT Steel Bars Required for Residential Project"
                  />
                </div>

                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">Category</label>
                  <select
                    value={newJob.category}
                    onChange={(e) => setNewJob({...newJob, category: e.target.value})}
                    className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  >
                    <option value="material">Material</option>
                    <option value="labor">Labor</option>
                    <option value="machinery">Machinery</option>
                  </select>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">Quantity</label>
                    <input
                      type="text"
                      value={newJob.quantity}
                      onChange={(e) => setNewJob({...newJob, quantity: e.target.value})}
                      className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      placeholder="e.g., 100 tons, 50 workers, 5 units"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">Budget Range</label>
                    <input
                      type="text"
                      value={newJob.budget_range}
                      onChange={(e) => setNewJob({...newJob, budget_range: e.target.value})}
                      className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      placeholder="e.g., ₹5-10 lakhs"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">Location</label>
                    <input
                      type="text"
                      value={newJob.location}
                      onChange={(e) => setNewJob({...newJob, location: e.target.value})}
                      required
                      className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      placeholder="e.g., Mumbai, Maharashtra"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">Delivery Timeline</label>
                    <input
                      type="text"
                      value={newJob.delivery_timeline}
                      onChange={(e) => setNewJob({...newJob, delivery_timeline: e.target.value})}
                      required
                      className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      placeholder="e.g., Within 15 days"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">Description</label>
                  <textarea
                    value={newJob.description}
                    onChange={(e) => setNewJob({...newJob, description: e.target.value})}
                    required
                    rows={4}
                    className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    placeholder="Provide detailed requirements, specifications, quality standards, etc."
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
                      id="job-files"
                      multiple
                      accept=".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt,.xls,.xlsx"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <label
                      htmlFor="job-files"
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
                  {jobFiles.length > 0 && (
                    <div className="mt-4 space-y-2">
                      <h4 className="text-sm font-medium text-gray-300">Selected Files:</h4>
                      {jobFiles.map((file, index) => (
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
                    onClick={() => setShowCreateModal(false)}
                    className="px-6 py-3 border border-gray-600 text-gray-300 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="bg-orange-600 hover:bg-orange-700 disabled:bg-orange-600/50 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
                  >
                    {loading ? 'Posting...' : 'Post Job'}
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

// Job Card Component
const JobCard = ({ job, isOwner }) => {
  const { user } = useContext(AuthContext);
  
  const getCategoryIcon = (category) => {
    switch (category) {
      case 'material': return <Package className="h-5 w-5" />;
      case 'labor': return <Users className="h-5 w-5" />;
      case 'machinery': return <Wrench className="h-5 w-5" />;
      default: return <Package className="h-5 w-5" />;
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'material': return 'bg-blue-600';
      case 'labor': return 'bg-green-600';
      case 'machinery': return 'bg-orange-600';
      default: return 'bg-gray-600';
    }
  };

  return (
    <div className="glass rounded-lg p-6 card-hover">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center mb-2">
            <div className={`${getCategoryColor(job.category)} p-2 rounded-lg mr-3`}>
              {getCategoryIcon(job.category)}
            </div>
            <div>
              <h3 className="text-xl font-semibold text-white">{job.title}</h3>
              <p className="text-gray-400 capitalize">{job.category}</p>
            </div>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
          job.status === 'open' ? 'bg-green-600 text-white' : 
          job.status === 'awarded' ? 'bg-blue-600 text-white' : 
          'bg-gray-600 text-white'
        }`}>
          {job.status}
        </div>
      </div>

      <p className="text-gray-300 mb-4 line-clamp-2">{job.description}</p>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4 text-sm">
        {job.quantity && (
          <div className="flex items-center text-gray-400">
            <Package className="h-4 w-4 mr-2" />
            <span>{job.quantity}</span>
          </div>
        )}
        <div className="flex items-center text-gray-400">
          <MapPin className="h-4 w-4 mr-2" />
          <span>{job.location}</span>
        </div>
        <div className="flex items-center text-gray-400">
          <Clock className="h-4 w-4 mr-2" />
          <span>{job.delivery_timeline}</span>
        </div>
        {job.budget_range && (
          <div className="flex items-center text-gray-400">
            <DollarSign className="h-4 w-4 mr-2" />
            <span>{job.budget_range}</span>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center text-gray-400 text-sm">
          <Calendar className="h-4 w-4 mr-2" />
          <span>Posted {new Date(job.created_at).toLocaleDateString()}</span>
        </div>
        <div className="flex space-x-3">
          {isOwner ? (
            <Link
              to={`/bids?job_id=${job.id}`}
              className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
            >
              View Bids
            </Link>
          ) : (
            user?.role === 'supplier' && (
              <Link
                to={`/bids?job_id=${job.id}&action=bid`}
                className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
              >
                Submit Bid
              </Link>
            )
          )}
        </div>
      </div>
    </div>
  );
};

export default JobsPage;