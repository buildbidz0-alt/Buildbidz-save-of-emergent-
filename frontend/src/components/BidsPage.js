import React, { useState, useEffect, useContext } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { AuthContext } from '../App';
import { 
  Building2, ArrowLeft, DollarSign, Clock, Award, X, CheckCircle,
  TrendingUp, Package, Users, Wrench, MapPin, Calendar, MessageCircle,
  Upload, FileText
} from 'lucide-react';
import axios from 'axios';

const BidsPage = () => {
  const { user, API } = useContext(AuthContext);
  const [searchParams] = useSearchParams();
  const jobId = searchParams.get('job_id');
  const action = searchParams.get('action');
  
  const [bids, setBids] = useState([]);
  const [myBids, setMyBids] = useState([]);
  const [allMyJobs, setAllMyJobs] = useState([]); // For buyer: all their jobs with bids
  const [jobDetails, setJobDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(user?.role === 'buyer' ? 'received' : 'my-bids');
  const [showBidModal, setShowBidModal] = useState(action === 'bid');
  const [error, setError] = useState('');

  const [newBid, setNewBid] = useState({
    price_quote: '',
    delivery_estimate: '',
    notes: ''
  });

  const [bidFiles, setBidFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (user?.role === 'supplier') {
      fetchMyBids();
    } else if (user?.role === 'buyer') {
      if (jobId) {
        // Specific job bids
        fetchJobBids();
        fetchJobDetails();
      } else {
        // All jobs with their bids for buyer overview
        fetchAllMyJobsWithBids();
      }
    }
  }, [jobId]);

  const fetchJobDetails = async () => {
    try {
      const response = await axios.get(`${API}/jobs`);
      const job = response.data.find(j => j.id === jobId);
      setJobDetails(job);
    } catch (error) {
      console.error('Failed to fetch job details:', error);
    }
  };

  const fetchJobBids = async () => {
    if (!jobId) return;
    try {
      const response = await axios.get(`${API}/jobs/${jobId}/bids`);
      setBids(response.data);
    } catch (error) {
      console.error('Failed to fetch job bids:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAllMyJobsWithBids = async () => {
    try {
      // Get all buyer's jobs
      const jobsResponse = await axios.get(`${API}/jobs/my`);
      const jobs = jobsResponse.data;
      
      // For each job, get its bids
      const jobsWithBids = await Promise.all(
        jobs.map(async (job) => {
          try {
            const bidsResponse = await axios.get(`${API}/jobs/${job.id}/bids`);
            return {
              ...job,
              bids: bidsResponse.data
            };
          } catch (error) {
            // If can't fetch bids, return job with empty bids array
            return {
              ...job,
              bids: []
            };
          }
        })
      );
      
      setAllMyJobs(jobsWithBids);
    } catch (error) {
      console.error('Failed to fetch jobs with bids:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMyBids = async () => {
    try {
      const response = await axios.get(`${API}/bids/my`);
      setMyBids(response.data);
    } catch (error) {
      console.error('Failed to fetch my bids:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitBid = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // First submit the bid
      const bidResponse = await axios.post(`${API}/jobs/${jobId}/bids`, {
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
      setNewBid({ price_quote: '', delivery_estimate: '', notes: '' });
      setBidFiles([]);
      fetchMyBids();
      if (jobId) fetchJobBids();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to submit bid');
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

  const handleAwardBid = async (bidId) => {
    try {
      await axios.post(`${API}/jobs/${jobId}/award/${bidId}`);
      fetchJobBids();
      alert('Bid awarded successfully!');
    } catch (error) {
      alert('Failed to award bid: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

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
              <Link to="/jobs" className="flex items-center text-gray-400 hover:text-white mr-8">
                <ArrowLeft className="h-5 w-5 mr-2" />
                Jobs
              </Link>
              <div className="flex items-center space-x-3">
                <Building2 className="h-8 w-8 text-orange-500" />
                <span className="text-xl font-bold text-white">Bids</span>
              </div>
            </div>
            {user?.role === 'supplier' && jobDetails && (
              <button
                onClick={() => setShowBidModal(true)}
                className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
              >
                Submit Bid
              </button>
            )}
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Job Details Header */}
        {jobDetails && (
          <div className="glass rounded-lg p-6 mb-8">
            <div className="flex items-start justify-between">
              <div className="flex items-center mb-4">
                <div className={`${getCategoryColor(jobDetails.category)} p-3 rounded-lg mr-4`}>
                  {getCategoryIcon(jobDetails.category)}
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white mb-2">{jobDetails.title}</h1>
                  <div className="flex flex-wrap items-center gap-4 text-gray-400">
                    <div className="flex items-center">
                      <MapPin className="h-4 w-4 mr-1" />
                      <span>{jobDetails.location}</span>
                    </div>
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-1" />
                      <span>{jobDetails.delivery_timeline}</span>
                    </div>
                    {jobDetails.budget_range && (
                      <div className="flex items-center">
                        <DollarSign className="h-4 w-4 mr-1" />
                        <span>{jobDetails.budget_range}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                jobDetails.status === 'open' ? 'bg-green-600 text-white' : 
                jobDetails.status === 'awarded' ? 'bg-blue-600 text-white' : 
                'bg-gray-600 text-white'
              }`}>
                {jobDetails.status}
              </div>
            </div>
            <p className="text-gray-300">{jobDetails.description}</p>
          </div>
        )}

        {/* Tabs */}
        <div className="flex space-x-1 mb-8">
          {user?.role === 'buyer' && jobId && (
            <button
              onClick={() => setActiveTab('received')}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                activeTab === 'received'
                  ? 'bg-orange-600 text-white'
                  : 'glass text-gray-300 hover:text-white'
              }`}
            >
              Received Bids ({bids.length})
            </button>
          )}
          {user?.role === 'supplier' && (
            <button
              onClick={() => setActiveTab('my-bids')}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                activeTab === 'my-bids'
                  ? 'bg-orange-600 text-white'
                  : 'glass text-gray-300 hover:text-white'
              }`}
            >
              My Bids ({myBids.length})
            </button>
          )}
        </div>

        {/* Bid Listings */}
        {loading ? (
          <div className="space-y-6">
            {[1,2,3].map((i) => (
              <div key={i} className="glass rounded-lg p-6">
                <div className="animate-pulse">
                  <div className="h-6 bg-gray-700 rounded w-3/4 mb-4"></div>
                  <div className="h-4 bg-gray-700 rounded w-1/2 mb-2"></div>
                  <div className="h-4 bg-gray-700 rounded w-full"></div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-6">
            {activeTab === 'received' ? (
              // Buyer view - either specific job bids or overview of all jobs
              jobId ? (
                // Specific job bids
                bids.length === 0 ? (
                  <div className="glass rounded-lg p-12 text-center">
                    <TrendingUp className="h-16 w-16 text-gray-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-white mb-2">No bids received yet</h3>
                    <p className="text-gray-400">Suppliers will submit bids for your job posting</p>
                  </div>
                ) : (
                  <div className="grid gap-6">
                    {bids.map((bid) => (
                      <BidCard 
                        key={bid.id} 
                        bid={bid} 
                        jobId={jobId}
                        onAward={() => handleAwardBid(bid.id)}
                        canAward={user?.role === 'buyer' && jobDetails?.status === 'open'}
                      />
                    ))}
                  </div>
                )
              ) : (
                // All jobs overview for buyer
                allMyJobs.length === 0 ? (
                  <div className="glass rounded-lg p-12 text-center">
                    <Building2 className="h-16 w-16 text-gray-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-white mb-2">No jobs posted yet</h3>
                    <p className="text-gray-400 mb-6">Post your first job to start receiving bids</p>
                    <Link
                      to="/jobs?action=post"
                      className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors inline-flex items-center"
                    >
                      Post a Job
                    </Link>
                  </div>
                ) : (
                  <div className="space-y-8">
                    {allMyJobs.map((job) => (
                      <div key={job.id} className="glass rounded-lg p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center">
                            <div className={`${getCategoryColor(job.category)} p-3 rounded-lg mr-4`}>
                              {getCategoryIcon(job.category)}
                            </div>
                            <div>
                              <h3 className="text-xl font-semibold text-white mb-2">{job.title}</h3>
                              <div className="flex items-center space-x-4 text-gray-400 text-sm">
                                <span className="flex items-center">
                                  <MapPin className="h-4 w-4 mr-1" />
                                  {job.location}
                                </span>
                                <span className="flex items-center">
                                  <Calendar className="h-4 w-4 mr-1" />
                                  {new Date(job.created_at).toLocaleDateString()}
                                </span>
                                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                                  job.status === 'open' ? 'bg-green-600 text-white' : 
                                  job.status === 'awarded' ? 'bg-blue-600 text-white' : 
                                  'bg-gray-600 text-white'
                                }`}>
                                  {job.status}
                                </span>
                              </div>
                            </div>
                          </div>
                          <Link
                            to={`/bids?job_id=${job.id}`}
                            className="text-orange-400 hover:text-orange-300 text-sm font-medium"
                          >
                            View Details →
                          </Link>
                        </div>
                        
                        <div className="mb-4">
                          <p className="text-gray-300 text-sm">{job.description}</p>
                        </div>

                        {job.bids && job.bids.length > 0 ? (
                          <div className="space-y-3">
                            <h4 className="text-white font-medium">
                              Received Bids ({job.bids.length})
                            </h4>
                            <div className="grid gap-3">
                              {job.bids.slice(0, 3).map((bid) => (
                                <div key={bid.id} className="bg-gray-700 rounded-lg p-4">
                                  <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center space-x-3">
                                      <span className="text-white font-medium">
                                        {bid.supplier_info?.company_name || 'Unknown Supplier'}
                                      </span>
                                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                                        bid.status === 'submitted' ? 'bg-blue-600 text-white' : 
                                        bid.status === 'awarded' ? 'bg-green-600 text-white' : 
                                        'bg-red-600 text-white'
                                      }`}>
                                        {bid.status}
                                      </span>
                                    </div>
                                    <span className="text-orange-400 font-semibold">
                                      ₹{bid.price_quote?.toLocaleString()}
                                    </span>
                                  </div>
                                  <div className="text-gray-400 text-sm">
                                    Delivery: {bid.delivery_estimate}
                                  </div>
                                </div>
                              ))}
                              {job.bids.length > 3 && (
                                <Link
                                  to={`/bids?job_id=${job.id}`}
                                  className="text-orange-400 hover:text-orange-300 text-sm font-medium text-center block py-2"
                                >
                                  View all {job.bids.length} bids →
                                </Link>
                              )}
                            </div>
                          </div>
                        ) : (
                          <div className="text-gray-400 text-sm py-4 text-center">
                            No bids received yet
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )
              )
            ) : (
              myBids.length === 0 ? (
                <div className="glass rounded-lg p-12 text-center">
                  <DollarSign className="h-16 w-16 text-gray-500 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">No bids submitted yet</h3>
                  <p className="text-gray-400 mb-6">Browse available jobs and submit your first bid</p>
                  <Link
                    to="/jobs"
                    className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors inline-flex items-center"
                  >
                    Browse Jobs
                  </Link>
                </div>
              ) : (
                <div className="grid gap-6">
                  {myBids.map((bid) => (
                    <MyBidCard key={bid.id} bid={bid} />
                  ))}
                </div>
              )
            )}
          </div>
        )}
      </div>

      {/* Submit Bid Modal */}
      {showBidModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-900 bg-opacity-75 transition-opacity" onClick={() => setShowBidModal(false)}></div>
            
            <div className="inline-block align-bottom bg-gray-800 rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-2xl font-bold text-white">Submit Bid</h3>
                <button
                  onClick={() => setShowBidModal(false)}
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

              <form onSubmit={handleSubmitBid} className="space-y-6">
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">
                    Price Quote (₹) *
                  </label>
                  <div className="relative">
                    <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="number"
                      value={newBid.price_quote}
                      onChange={(e) => setNewBid({...newBid, price_quote: e.target.value})}
                      required
                      className="w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      placeholder="Enter your price quote"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">
                    Delivery Estimate *
                  </label>
                  <div className="relative">
                    <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      value={newBid.delivery_estimate}
                      onChange={(e) => setNewBid({...newBid, delivery_estimate: e.target.value})}
                      required
                      className="w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
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
                      id="bid-files"
                      multiple
                      accept=".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt,.xls,.xlsx"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <label
                      htmlFor="bid-files"
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

// Bid Card Component for received bids
const BidCard = ({ bid, onAward, canAward, jobId }) => {
  return (
    <div className="glass rounded-lg p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-white mb-2">
            {bid.supplier_info?.company_name || 'Unknown Supplier'}
          </h3>
          <div className="flex items-center space-x-4 text-sm text-gray-400">
            <div className="flex items-center">
              <DollarSign className="h-4 w-4 mr-1" />
              <span className="text-orange-400 font-semibold">₹{bid.price_quote?.toLocaleString()}</span>
            </div>
            <div className="flex items-center">
              <Clock className="h-4 w-4 mr-1" />
              <span>{bid.delivery_estimate}</span>
            </div>
            <div className="flex items-center">
              <Calendar className="h-4 w-4 mr-1" />
              <span>Submitted {new Date(bid.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
          bid.status === 'submitted' ? 'bg-blue-600 text-white' : 
          bid.status === 'awarded' ? 'bg-green-600 text-white' : 
          'bg-red-600 text-white'
        }`}>
          {bid.status}
        </div>
      </div>

      {bid.notes && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-300 mb-2">Additional Notes:</h4>
          <p className="text-gray-400 text-sm">{bid.notes}</p>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-400">
          Contact: {bid.supplier_info?.contact_phone}
        </div>
        <div className="flex space-x-2">
          {bid.status === 'awarded' && (
            <Link
              to={`/chat?job_id=${jobId}`}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors inline-flex items-center"
            >
              <MessageCircle className="h-4 w-4 mr-2" />
              Chat
            </Link>
          )}
          {canAward && bid.status === 'submitted' && (
            <button
              onClick={onAward}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors inline-flex items-center"
            >
              <Award className="h-4 w-4 mr-2" />
              Award Bid
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

// My Bid Card Component
const MyBidCard = ({ bid }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'awarded':
        return 'bg-green-600 text-white';
      case 'rejected':
        return 'bg-red-600 text-white';
      case 'submitted':
        return 'bg-blue-600 text-white';
      default:
        return 'bg-gray-600 text-white';
    }
  };

  const getStatusMessage = (status) => {
    switch (status) {
      case 'awarded':
        return '🎉 Congratulations! Your bid was awarded';
      case 'rejected':
        return 'Bid not selected this time';
      case 'submitted':
        return 'Bid submitted - awaiting review';
      default:
        return 'Status unknown';
    }
  };

  return (
    <div className="glass rounded-lg p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-white mb-2">
            {bid.job_info?.title || 'Job Title'}
          </h3>
          <div className="flex items-center space-x-4 text-sm text-gray-400 mb-2">
            <span className="capitalize">{bid.job_info?.category}</span>
            <span>{bid.job_info?.location}</span>
          </div>
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center text-gray-400">
              <DollarSign className="h-4 w-4 mr-1" />
              <span className="text-orange-400 font-semibold">₹{bid.price_quote?.toLocaleString()}</span>
            </div>
            <div className="flex items-center text-gray-400">
              <Clock className="h-4 w-4 mr-1" />
              <span>{bid.delivery_estimate}</span>
            </div>
          </div>
        </div>
        <div className="text-center">
          <div className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(bid.status)}`}>
            {bid.status}
          </div>
        </div>
      </div>

      {/* Status message */}
      <div className={`p-3 rounded-lg mb-4 ${
        bid.status === 'awarded' ? 'bg-green-500/10 border border-green-500/30' :
        bid.status === 'rejected' ? 'bg-red-500/10 border border-red-500/30' :
        'bg-blue-500/10 border border-blue-500/30'
      }`}>
        <p className={`text-sm font-medium ${
          bid.status === 'awarded' ? 'text-green-400' :
          bid.status === 'rejected' ? 'text-red-400' :
          'text-blue-400'
        }`}>
          {getStatusMessage(bid.status)}
        </p>
      </div>

      {bid.notes && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-300 mb-2">Your Notes:</h4>
          <p className="text-gray-400 text-sm">{bid.notes}</p>
        </div>
      )}

      <div className="text-sm text-gray-400">
        Submitted on {new Date(bid.created_at).toLocaleDateString()}
      </div>
    </div>
  );
};

export default BidsPage;