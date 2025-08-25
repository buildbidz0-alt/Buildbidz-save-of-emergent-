import React, { useState, useEffect, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import { 
  Building2, LogOut, Users, Briefcase, DollarSign, TrendingUp,
  Search, Filter, Trash2, Eye, MoreVertical, Menu, X, Settings,
  Calendar, MapPin, Clock, Phone, Mail, Package
} from 'lucide-react';
import axios from 'axios';
import FileList from './FileList';

const AdminDashboard = () => {
  const { user, logout, API } = useContext(AuthContext);
  const navigate = useNavigate();
  const [stats, setStats] = useState({});
  const [users, setUsers] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [bids, setBids] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Detail view states
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [selectedBid, setSelectedBid] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    fetchDashboardStats();
    fetchUsers();
    fetchJobs();
    fetchBids();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/admin/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    }
  };

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API}/admin/jobs`);
      setJobs(response.data);
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
    }
  };

  const fetchBids = async () => {
    try {
      const response = await axios.get(`${API}/admin/bids`);
      setBids(response.data);
    } catch (error) {
      console.error('Failed to fetch bids:', error);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      try {
        await axios.delete(`${API}/admin/users/${userId}`);
        fetchUsers();
        fetchDashboardStats();
        alert('User deleted successfully');
      } catch (error) {
        alert('Failed to delete user: ' + (error.response?.data?.detail || 'Unknown error'));
      }
    }
  };

  const handleDeleteJob = async (jobId) => {
    if (window.confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
      try {
        await axios.delete(`${API}/admin/jobs/${jobId}`);
        fetchJobs();
        fetchDashboardStats();
        alert('Job deleted successfully');
      } catch (error) {
        alert('Failed to delete job: ' + (error.response?.data?.detail || 'Unknown error'));
      }
    }
  };

  const handleDeleteBid = async (bidId) => {
    if (window.confirm('Are you sure you want to delete this bid? This action cannot be undone.')) {
      try {
        await axios.delete(`${API}/admin/bids/${bidId}`);
        fetchBids();
        alert('Bid deleted successfully');
      } catch (error) {
        alert('Failed to delete bid: ' + (error.response?.data?.detail || 'Unknown error'));
      }
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Detail view handlers
  const handleViewUser = async (userId) => {
    setDetailLoading(true);
    try {
      const response = await axios.get(`${API}/admin/users/${userId}/details`);
      setSelectedUser(response.data);
      setSelectedJob(null);
      setSelectedBid(null);
      setShowDetailModal(true);
    } catch (error) {
      alert('Failed to fetch user details: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setDetailLoading(false);
    }
  };

  const handleViewJob = async (job) => {
    setDetailLoading(true);
    try {
      // For job details, we can use the job data we already have
      // but we might want to fetch additional data like bids
      const bidsResponse = await axios.get(`${API}/jobs/${job.id}/bids`);
      setSelectedJob({
        ...job,
        bids: bidsResponse.data
      });
      setSelectedUser(null);
      setSelectedBid(null);
      setShowDetailModal(true);
    } catch (error) {
      // If bids fetch fails, still show job details
      setSelectedJob(job);
      setSelectedUser(null);
      setSelectedBid(null);
      setShowDetailModal(true);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleViewBid = async (bid) => {
    setSelectedBid(bid);
    setSelectedUser(null);
    setSelectedJob(null);
    setShowDetailModal(true);
  };

  const closeDetailModal = () => {
    setShowDetailModal(false);
    setSelectedUser(null);
    setSelectedJob(null);
    setSelectedBid(null);
  };

  const filteredUsers = users.filter(user => 
    user.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredJobs = jobs.filter(job =>
    job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    job.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredBids = bids.filter(bid =>
    bid.job_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    bid.supplier_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const navigation = [
    { name: 'Overview', id: 'overview', icon: TrendingUp },
    { name: 'Users', id: 'users', icon: Users },
    { name: 'Jobs', id: 'jobs', icon: Briefcase },
    { name: 'Bids', id: 'bids', icon: DollarSign }
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
                <span className="ml-2 text-xl font-bold text-white">BuildBidz Admin</span>
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
              <span className="ml-2 text-xl font-bold text-white">BuildBidz Admin</span>
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
                <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
                <p className="text-gray-400 mt-2">Manage users, jobs, and bids across the platform</p>
              </div>

              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <>
                  {/* Stats Cards */}
                  {loading ? (
                    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
                      {[1,2,3,4].map((i) => (
                        <div key={i} className="glass rounded-lg p-6">
                          <div className="animate-pulse">
                            <div className="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
                            <div className="h-8 bg-gray-700 rounded w-1/2"></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
                      <div className="glass rounded-lg p-6">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                              <Users className="h-6 w-6 text-white" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <h3 className="text-sm font-medium text-gray-400">Total Users</h3>
                            <p className="text-2xl font-semibold text-white">{stats.total_users || 0}</p>
                          </div>
                        </div>
                      </div>

                      <div className="glass rounded-lg p-6">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center">
                              <Briefcase className="h-6 w-6 text-white" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <h3 className="text-sm font-medium text-gray-400">Total Jobs</h3>
                            <p className="text-2xl font-semibold text-white">{stats.total_jobs || 0}</p>
                          </div>
                        </div>
                      </div>

                      <div className="glass rounded-lg p-6">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-orange-600 rounded-lg flex items-center justify-center">
                              <DollarSign className="h-6 w-6 text-white" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <h3 className="text-sm font-medium text-gray-400">Total Bids</h3>
                            <p className="text-2xl font-semibold text-white">{stats.total_bids || 0}</p>
                          </div>
                        </div>
                      </div>

                      <div className="glass rounded-lg p-6">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
                              <TrendingUp className="h-6 w-6 text-white" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <h3 className="text-sm font-medium text-gray-400">Active Jobs</h3>
                            <p className="text-2xl font-semibold text-white">{stats.active_jobs || 0}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* Search Bar for other tabs */}
              {activeTab !== 'overview' && (
                <div className="mb-6">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      placeholder={`Search ${activeTab}...`}
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    />
                  </div>
                </div>
              )}

              {/* Users Tab */}
              {activeTab === 'users' && (
                <div className="glass rounded-lg overflow-hidden">
                  <div className="px-6 py-4 border-b border-gray-700">
                    <h3 className="text-lg font-semibold text-white">Users Management</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead className="bg-gray-800">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Company
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Email
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Role
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Created
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-700">
                        {filteredUsers.map((user) => (
                          <tr key={user.id} className="hover:bg-gray-800">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-white">{user.company_name}</div>
                              <div className="text-sm text-gray-400">{user.contact_phone}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-white">{user.email}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                user.role === 'buyer' ? 'bg-blue-600 text-white' : 'bg-green-600 text-white'
                              }`}>
                                {user.role}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                user.subscription_status === 'active' || user.subscription_status === 'trial'
                                  ? 'bg-green-600 text-white' 
                                  : 'bg-red-600 text-white'
                              }`}>
                                {user.subscription_status || 'inactive'}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                              {new Date(user.created_at).toLocaleDateString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                              <div className="flex space-x-2">
                                <button
                                  onClick={() => handleViewUser(user.id)}
                                  className="text-blue-400 hover:text-blue-300"
                                  title="View Details"
                                >
                                  <Eye className="h-4 w-4" />
                                </button>
                                <button
                                  onClick={() => handleDeleteUser(user.id)}
                                  className="text-red-400 hover:text-red-300"
                                  title="Delete User"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Jobs Tab */}
              {activeTab === 'jobs' && (
                <div className="glass rounded-lg overflow-hidden">
                  <div className="px-6 py-4 border-b border-gray-700">
                    <h3 className="text-lg font-semibold text-white">Jobs Management</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead className="bg-gray-800">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Title
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Category
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Location
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Created
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-700">
                        {filteredJobs.map((job) => (
                          <tr key={job.id} className="hover:bg-gray-800">
                            <td className="px-6 py-4">
                              <div className="text-sm font-medium text-white">{job.title}</div>
                              <div className="text-sm text-gray-400 truncate max-w-xs">{job.description}</div>
                              {job.posted_by_info && (
                                <div className="text-xs text-orange-400 mt-1">
                                  Posted by: {job.posted_by_info.company_name}
                                </div>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-600 text-white capitalize">
                                {job.category}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                              {job.location}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                job.status === 'open' ? 'bg-green-600 text-white' : 
                                job.status === 'awarded' ? 'bg-blue-600 text-white' : 
                                'bg-gray-600 text-white'
                              }`}>
                                {job.status}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                              {new Date(job.created_at).toLocaleDateString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                              <div className="flex space-x-2">
                                <button
                                  onClick={() => handleViewJob(job)}
                                  className="text-blue-400 hover:text-blue-300"
                                  title="View Details"
                                >
                                  <Eye className="h-4 w-4" />
                                </button>
                                <button
                                  onClick={() => handleDeleteJob(job.id)}
                                  className="text-red-400 hover:text-red-300"
                                  title="Delete Job"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Bids Tab */}
              {activeTab === 'bids' && (
                <div className="glass rounded-lg overflow-hidden">
                  <div className="px-6 py-4 border-b border-gray-700">
                    <h3 className="text-lg font-semibold text-white">Bids Management</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead className="bg-gray-800">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Job ID
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Supplier ID
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Price Quote
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Created
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-700">
                        {filteredBids.map((bid) => (
                          <tr key={bid.id} className="hover:bg-gray-800">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-white">{bid.job_id.substring(0, 8)}...</div>
                              {bid.job_info && (
                                <div className="text-xs text-blue-400">{bid.job_info.title}</div>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-white">{bid.supplier_id.substring(0, 8)}...</div>
                              {bid.supplier_info && (
                                <div className="text-xs text-green-400">{bid.supplier_info.company_name}</div>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-orange-400">
                              ₹{bid.price_quote?.toLocaleString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                bid.status === 'submitted' ? 'bg-blue-600 text-white' : 
                                bid.status === 'awarded' ? 'bg-green-600 text-white' : 
                                'bg-red-600 text-white'
                              }`}>
                                {bid.status}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                              {new Date(bid.created_at).toLocaleDateString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                              <div className="flex space-x-2">
                                <button
                                  onClick={() => handleViewBid(bid)}
                                  className="text-blue-400 hover:text-blue-300"
                                  title="View Details"
                                >
                                  <Eye className="h-4 w-4" />
                                </button>
                                <button
                                  onClick={() => handleDeleteBid(bid.id)}
                                  className="text-red-400 hover:text-red-300"
                                  title="Delete Bid"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>

      {/* Detail Modal */}
      {showDetailModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-900 bg-opacity-75 transition-opacity" onClick={closeDetailModal}></div>
            
            <div className="inline-block align-bottom bg-gray-800 rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full sm:p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-2xl font-bold text-white">
                  {selectedUser ? 'User Details' : selectedJob ? 'Job Details' : 'Bid Details'}
                </h3>
                <button
                  onClick={closeDetailModal}
                  className="text-gray-400 hover:text-white"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              {detailLoading ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* User Details */}
                  {selectedUser && (
                    <UserDetailView user={selectedUser} />
                  )}

                  {/* Job Details */}
                  {selectedJob && (
                    <JobDetailView job={selectedJob} />
                  )}

                  {/* Bid Details */}
                  {selectedBid && (
                    <BidDetailView bid={selectedBid} />
                  )}
                </div>
              )}

              <div className="flex justify-end mt-6">
                <button
                  onClick={closeDetailModal}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// User Detail View Component
const UserDetailView = ({ user }) => {
  const maskPassword = (password) => {
    return '•'.repeat(12);
  };

  return (
    <div className="space-y-6">
      {/* Basic User Info */}
      <div className="glass rounded-lg p-6">
        <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
          <Users className="h-5 w-5 mr-2 text-blue-400" />
          User Information
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-400">Company Name</label>
            <p className="text-white">{user.user.company_name}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400">Email</label>
            <p className="text-white flex items-center">
              <Mail className="h-4 w-4 mr-1 text-gray-400" />
              {user.user.email}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400">Contact Phone</label>
            <p className="text-white flex items-center">
              <Phone className="h-4 w-4 mr-1 text-gray-400" />
              {user.user.contact_phone}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400">Role</label>
            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
              user.user.role === 'buyer' ? 'bg-blue-600 text-white' : 'bg-green-600 text-white'
            }`}>
              {user.user.role}
            </span>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400">Password</label>
            <p className="text-gray-300">{maskPassword()}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400">GST Number</label>
            <p className="text-white">{user.user.gst_number || 'Not provided'}</p>
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-400">Address</label>
            <p className="text-white">{user.user.address || 'Not provided'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400">Subscription Status</label>
            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
              user.user.subscription_status === 'active' || user.user.subscription_status === 'trial'
                ? 'bg-green-600 text-white' 
                : 'bg-red-600 text-white'
            }`}>
              {user.user.subscription_status || 'inactive'}
            </span>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400">Member Since</label>
            <p className="text-white flex items-center">
              <Calendar className="h-4 w-4 mr-1 text-gray-400" />
              {new Date(user.user.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass rounded-lg p-4">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
              <Briefcase className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Jobs Posted</p>
              <p className="text-xl font-semibold text-white">{user.jobs_posted}</p>
            </div>
          </div>
        </div>
        <div className="glass rounded-lg p-4">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center mr-3">
              <DollarSign className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Bids Submitted</p>
              <p className="text-xl font-semibold text-white">{user.bids_submitted}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Jobs Posted */}
      {user.jobs && user.jobs.length > 0 && (
        <div className="glass rounded-lg p-6">
          <h4 className="text-lg font-semibold text-white mb-4">Jobs Posted</h4>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {user.jobs.map((job) => (
              <div key={job.id} className="bg-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h5 className="font-medium text-white">{job.title}</h5>
                    <p className="text-sm text-gray-400 mt-1">{job.description}</p>
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span className="flex items-center">
                        <MapPin className="h-3 w-3 mr-1" />
                        {job.location}
                      </span>
                      <span className="flex items-center">
                        <Calendar className="h-3 w-3 mr-1" />
                        {new Date(job.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    job.status === 'open' ? 'bg-green-600 text-white' : 
                    job.status === 'awarded' ? 'bg-blue-600 text-white' : 
                    'bg-gray-600 text-white'
                  }`}>
                    {job.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bids Submitted */}
      {user.bids && user.bids.length > 0 && (
        <div className="glass rounded-lg p-6">
          <h4 className="text-lg font-semibold text-white mb-4">Bids Submitted</h4>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {user.bids.map((bid) => (
              <div key={bid.id} className="bg-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4">
                      <span className="text-orange-400 font-semibold">₹{bid.price_quote?.toLocaleString()}</span>
                      <span className="text-gray-400 text-sm">{bid.delivery_estimate}</span>
                    </div>
                    {bid.notes && (
                      <p className="text-sm text-gray-400 mt-1">{bid.notes}</p>
                    )}
                    <p className="text-xs text-gray-500 mt-2">
                      Submitted on {new Date(bid.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
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
      )}
    </div>
  );
};

// Job Detail View Component
const JobDetailView = ({ job }) => {
  const getCategoryIcon = (category) => {
    switch (category) {
      case 'material': return <Package className="h-5 w-5" />;
      case 'labor': return <Users className="h-5 w-5" />;
      case 'machinery': return <Settings className="h-5 w-5" />;
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
    <div className="space-y-6">
      {/* Job Info */}
      <div className="glass rounded-lg p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center">
            <div className={`${getCategoryColor(job.category)} p-3 rounded-lg mr-4`}>
              {getCategoryIcon(job.category)}
            </div>
            <div>
              <h4 className="text-xl font-semibold text-white">{job.title}</h4>
              <div className="flex items-center space-x-4 mt-2 text-gray-400">
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
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
            job.status === 'open' ? 'bg-green-600 text-white' : 
            job.status === 'awarded' ? 'bg-blue-600 text-white' : 
            'bg-gray-600 text-white'
          }`}>
            {job.status}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-400">Category</label>
            <p className="text-white capitalize">{job.category}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400">Quantity</label>
            <p className="text-white">{job.quantity || 'Not specified'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400">Posted By</label>
            <p className="text-white">{job.posted_by_info?.company_name || 'Unknown'}</p>
            {job.posted_by_info?.email && (
              <p className="text-gray-400 text-sm">{job.posted_by_info.email}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400">Posted On</label>
            <p className="text-white">{new Date(job.created_at).toLocaleDateString()}</p>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-400 mb-2">Description</label>
          <p className="text-gray-300">{job.description}</p>
        </div>
      </div>

      {/* Bids Received */}
      {job.bids && job.bids.length > 0 && (
        <div className="glass rounded-lg p-6">
          <h4 className="text-lg font-semibold text-white mb-4">
            Bids Received ({job.bids.length})
          </h4>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {job.bids.map((bid) => (
              <div key={bid.id} className="bg-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="font-medium text-white">
                        {bid.supplier_info?.company_name || 'Unknown Supplier'}
                      </h5>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        bid.status === 'submitted' ? 'bg-blue-600 text-white' : 
                        bid.status === 'awarded' ? 'bg-green-600 text-white' : 
                        'bg-red-600 text-white'
                      }`}>
                        {bid.status}
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 text-sm">
                      <span className="text-orange-400 font-semibold">₹{bid.price_quote?.toLocaleString()}</span>
                      <span className="text-gray-400">{bid.delivery_estimate}</span>
                      {bid.supplier_info?.contact_phone && (
                        <span className="text-gray-400">{bid.supplier_info.contact_phone}</span>
                      )}
                    </div>
                    {bid.notes && (
                      <p className="text-sm text-gray-400 mt-2">{bid.notes}</p>
                    )}
                    <p className="text-xs text-gray-500 mt-1">
                      Submitted on {new Date(bid.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Bid Detail View Component
const BidDetailView = ({ bid }) => {
  return (
    <div className="space-y-6">
      <div className="glass rounded-lg p-6">
        <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
          <DollarSign className="h-5 w-5 mr-2 text-orange-400" />
          Bid Information
        </h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-400">Price Quote</label>
            <p className="text-2xl font-semibold text-orange-400">₹{bid.price_quote?.toLocaleString()}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400">Delivery Estimate</label>
            <p className="text-white flex items-center">
              <Clock className="h-4 w-4 mr-1 text-gray-400" />
              {bid.delivery_estimate}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400">Status</label>
            <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${
              bid.status === 'submitted' ? 'bg-blue-600 text-white' : 
              bid.status === 'awarded' ? 'bg-green-600 text-white' : 
              'bg-red-600 text-white'
            }`}>
              {bid.status}
            </span>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400">Submitted On</label>
            <p className="text-white flex items-center">
              <Calendar className="h-4 w-4 mr-1 text-gray-400" />
              {new Date(bid.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {bid.notes && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-400 mb-2">Additional Notes</label>
            <div className="bg-gray-700 rounded-lg p-4">
              <p className="text-gray-300">{bid.notes}</p>
            </div>
          </div>
        )}

        {/* Supplier Info */}
        {bid.supplier_info && (
          <div className="border-t border-gray-700 pt-4">
            <h5 className="text-md font-semibold text-white mb-3">Supplier Information</h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-400">Company Name</label>
                <p className="text-white">{bid.supplier_info.company_name}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Contact</label>
                <p className="text-white flex items-center">
                  <Phone className="h-4 w-4 mr-1 text-gray-400" />
                  {bid.supplier_info.contact_phone}
                </p>
              </div>
              {bid.supplier_info.email && (
                <div>
                  <label className="block text-sm font-medium text-gray-400">Email</label>
                  <p className="text-white flex items-center">
                    <Mail className="h-4 w-4 mr-1 text-gray-400" />
                    {bid.supplier_info.email}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Job Info */}
        {bid.job_info && (
          <div className="border-t border-gray-700 pt-4 mt-4">
            <h5 className="text-md font-semibold text-white mb-3">Job Information</h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-400">Job Title</label>
                <p className="text-white">{bid.job_info.title}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Category</label>
                <p className="text-white capitalize">{bid.job_info.category}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Location</label>
                <p className="text-white flex items-center">
                  <MapPin className="h-4 w-4 mr-1 text-gray-400" />
                  {bid.job_info.location}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;