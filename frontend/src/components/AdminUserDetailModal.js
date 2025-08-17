import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../App';
import { 
  X, User, Mail, Phone, Building2, MapPin, FileText, 
  DollarSign, Clock, Calendar, Package, Users, Wrench, Award
} from 'lucide-react';
import axios from 'axios';

const AdminUserDetailModal = ({ userId, isOpen, onClose }) => {
  const { API } = useContext(AuthContext);
  const [userDetails, setUserDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('info');

  useEffect(() => {
    if (isOpen && userId) {
      fetchUserDetails();
    }
  }, [isOpen, userId]);

  const fetchUserDetails = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/admin/users/${userId}/details`);
      setUserDetails(response.data);
    } catch (error) {
      console.error('Failed to fetch user details:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'material': return <Package className="h-4 w-4" />;
      case 'labor': return <Users className="h-4 w-4" />;
      case 'machinery': return <Wrench className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
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

  const getStatusColor = (status) => {
    switch (status) {
      case 'open': return 'bg-green-600 text-white';
      case 'awarded': return 'bg-blue-600 text-white';
      case 'closed': return 'bg-gray-600 text-white';
      case 'submitted': return 'bg-blue-600 text-white';
      case 'rejected': return 'bg-red-600 text-white';
      default: return 'bg-gray-600 text-white';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-900 bg-opacity-75 transition-opacity" onClick={onClose}></div>
        
        <div className="inline-block align-bottom bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <div className="flex justify-between items-center p-6 border-b border-gray-700">
            <h3 className="text-2xl font-bold text-white">User Details</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-orange-500 mx-auto"></div>
              <p className="text-gray-400 mt-4">Loading user details...</p>
            </div>
          ) : userDetails ? (
            <div className="p-6">
              {/* Tabs */}
              <div className="flex space-x-1 mb-6">
                <button
                  onClick={() => setActiveTab('info')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    activeTab === 'info'
                      ? 'bg-orange-600 text-white'
                      : 'glass text-gray-300 hover:text-white'
                  }`}
                >
                  User Info
                </button>
                <button
                  onClick={() => setActiveTab('jobs')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    activeTab === 'jobs'
                      ? 'bg-orange-600 text-white'
                      : 'glass text-gray-300 hover:text-white'
                  }`}
                >
                  Jobs Posted ({userDetails.jobs_posted})
                </button>
                <button
                  onClick={() => setActiveTab('bids')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    activeTab === 'bids'
                      ? 'bg-orange-600 text-white'
                      : 'glass text-gray-300 hover:text-white'
                  }`}
                >
                  Bids Submitted ({userDetails.bids_submitted})
                </button>
              </div>

              {/* User Info Tab */}
              {activeTab === 'info' && (
                <div className="glass rounded-lg p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div className="flex items-center space-x-3">
                        <User className="h-5 w-5 text-orange-500" />
                        <div>
                          <p className="text-sm text-gray-400">Company Name</p>
                          <p className="text-white font-semibold">{userDetails.user.company_name}</p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        <Mail className="h-5 w-5 text-orange-500" />
                        <div>
                          <p className="text-sm text-gray-400">Email Address</p>
                          <p className="text-white font-semibold">{userDetails.user.email}</p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        <Phone className="h-5 w-5 text-orange-500" />
                        <div>
                          <p className="text-sm text-gray-400">Contact Phone</p>
                          <p className="text-white font-semibold">{userDetails.user.contact_phone}</p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        <Building2 className="h-5 w-5 text-orange-500" />
                        <div>
                          <p className="text-sm text-gray-400">Role</p>
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full capitalize ${
                            userDetails.user.role === 'buyer' ? 'bg-blue-600 text-white' : 'bg-green-600 text-white'
                          }`}>
                            {userDetails.user.role}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {userDetails.user.gst_number && (
                        <div className="flex items-center space-x-3">
                          <FileText className="h-5 w-5 text-orange-500" />
                          <div>
                            <p className="text-sm text-gray-400">GST Number</p>
                            <p className="text-white font-semibold">{userDetails.user.gst_number}</p>
                          </div>
                        </div>
                      )}

                      {userDetails.user.address && (
                        <div className="flex items-start space-x-3">
                          <MapPin className="h-5 w-5 text-orange-500 mt-1" />
                          <div>
                            <p className="text-sm text-gray-400">Address</p>
                            <p className="text-white">{userDetails.user.address}</p>
                          </div>
                        </div>
                      )}

                      <div className="flex items-center space-x-3">
                        <Calendar className="h-5 w-5 text-orange-500" />
                        <div>
                          <p className="text-sm text-gray-400">Joined</p>
                          <p className="text-white">{new Date(userDetails.user.created_at).toLocaleDateString()}</p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        <Award className="h-5 w-5 text-orange-500" />
                        <div>
                          <p className="text-sm text-gray-400">Subscription Status</p>
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full capitalize ${
                            userDetails.user.subscription_status === 'active' ? 'bg-green-600 text-white' :
                            userDetails.user.subscription_status === 'trial' ? 'bg-blue-600 text-white' :
                            'bg-red-600 text-white'
                          }`}>
                            {userDetails.user.subscription_status}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Password Note */}
                  <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                    <p className="text-yellow-400 text-sm">
                      <strong>Security Note:</strong> User passwords are securely hashed and cannot be viewed. 
                      Users can reset their passwords using the "Forgot Password" feature.
                    </p>
                  </div>
                </div>
              )}

              {/* Jobs Tab */}
              {activeTab === 'jobs' && (
                <div className="space-y-4">
                  {userDetails.jobs.length === 0 ? (
                    <div className="glass rounded-lg p-8 text-center">
                      <Building2 className="h-16 w-16 text-gray-500 mx-auto mb-4" />
                      <p className="text-gray-400">No jobs posted by this user</p>
                    </div>
                  ) : (
                    userDetails.jobs.map((job) => (
                      <div key={job.id} className="glass rounded-lg p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center">
                            <div className={`${getCategoryColor(job.category)} p-2 rounded-lg mr-3`}>
                              {getCategoryIcon(job.category)}
                            </div>
                            <div>
                              <h4 className="text-lg font-semibold text-white">{job.title}</h4>
                              <p className="text-sm text-gray-400 capitalize">{job.category}</p>
                            </div>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(job.status)}`}>
                            {job.status}
                          </span>
                        </div>

                        <p className="text-gray-300 mb-4">{job.description}</p>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
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

                        <div className="mt-4 text-xs text-gray-500">
                          Posted on {new Date(job.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Bids Tab */}
              {activeTab === 'bids' && (
                <div className="space-y-4">
                  {userDetails.bids.length === 0 ? (
                    <div className="glass rounded-lg p-8 text-center">
                      <DollarSign className="h-16 w-16 text-gray-500 mx-auto mb-4" />
                      <p className="text-gray-400">No bids submitted by this user</p>
                    </div>
                  ) : (
                    userDetails.bids.map((bid) => (
                      <div key={bid.id} className="glass rounded-lg p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h4 className="text-lg font-semibold text-white">Bid #{bid.id.substring(0, 8)}</h4>
                            <p className="text-sm text-gray-400">Job ID: {bid.job_id.substring(0, 8)}</p>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(bid.status)}`}>
                            {bid.status}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mb-4">
                          <div className="flex items-center text-gray-400">
                            <DollarSign className="h-4 w-4 mr-2" />
                            <span className="text-orange-400 font-semibold">₹{bid.price_quote?.toLocaleString()}</span>
                          </div>
                          <div className="flex items-center text-gray-400">
                            <Clock className="h-4 w-4 mr-2" />
                            <span>{bid.delivery_estimate}</span>
                          </div>
                        </div>

                        {bid.notes && (
                          <div className="mb-4">
                            <h5 className="text-sm font-medium text-gray-300 mb-2">Notes:</h5>
                            <p className="text-gray-400 text-sm">{bid.notes}</p>
                          </div>
                        )}

                        <div className="text-xs text-gray-500">
                          Submitted on {new Date(bid.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="p-8 text-center">
              <p className="text-gray-400">Failed to load user details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminUserDetailModal;