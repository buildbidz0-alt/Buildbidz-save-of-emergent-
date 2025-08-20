import React, { useState, useEffect, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import { 
  Building2, LogOut, Plus, TrendingUp, Clock, CheckCircle, 
  DollarSign, Users, Award, AlertTriangle, Menu, X, Settings
} from 'lucide-react';
import axios from 'axios';
import NotificationBell from './NotificationBell';

const Dashboard = () => {
  const { user, logout, API } = useContext(AuthContext);
  const navigate = useNavigate();
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    fetchDashboardStats();
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

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const needsSubscription = user?.role === 'buyer' && user?.subscription_status !== 'active' && 
    (!user?.trial_expires_at || new Date(user.trial_expires_at) <= new Date());

  const isTrialActive = user?.role === 'buyer' && user?.subscription_status === 'trial' && 
    user?.trial_expires_at && new Date(user.trial_expires_at) > new Date();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', current: true },
    { name: 'Jobs', href: '/jobs', current: false },
    { name: 'Bids', href: '/bids', current: false },
    { name: 'Messages', href: '/chat', current: false },
    { name: 'Settings', href: '/settings', current: false },
    ...(user?.role === 'buyer' ? [{ name: 'Subscription', href: '/subscription', current: false }] : [])
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
                <span className="ml-2 text-xl font-bold text-white">BuildBidz</span>
              </div>
              <nav className="mt-5 space-y-1 px-2">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className="group flex items-center px-2 py-2 text-base font-medium rounded-md text-gray-300 hover:bg-gray-700 hover:text-white"
                    onClick={() => setSidebarOpen(false)}
                  >
                    {item.name}
                  </Link>
                ))}
              </nav>
              {/* Mobile logout button */}
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
              <span className="ml-2 text-xl font-bold text-white">BuildBidz</span>
            </div>
            <nav className="mt-5 flex-1 space-y-1 px-2">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className="group flex items-center px-2 py-2 text-sm font-medium rounded-md text-gray-300 hover:bg-gray-700 hover:text-white"
                >
                  {item.name === 'Settings' && <Settings className="h-4 w-4 mr-2" />}
                  {item.name}
                </Link>
              ))}
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
        <div className="sticky top-0 z-10 glass border-b border-gray-700 pl-1 pt-1 sm:pl-3 sm:pt-3 lg:flex lg:justify-between lg:items-center lg:px-6 lg:py-4">
          <button
            type="button"
            className="-ml-0.5 -mt-0.5 h-12 w-12 inline-flex items-center justify-center rounded-md text-gray-500 hover:text-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-orange-500 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>
          
          {/* Mobile Notification Bell */}
          <div className="lg:hidden">
            <NotificationBell />
          </div>
          
          {/* Desktop Notification Bell */}
          <div className="hidden lg:block">
            <div className="flex items-center space-x-4">
              <NotificationBell />
            </div>
          </div>
        </div>

        <main className="flex-1">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              {/* Header */}
              <div className="mb-8">
                <h1 className="text-3xl font-bold text-white">
                  Welcome back, {user?.company_name}!
                </h1>
                <p className="text-gray-400 mt-2">
                  {user?.role === 'buyer' 
                    ? 'Manage your construction requirements and track bids'
                    : 'Explore opportunities and manage your bids'
                  }
                </p>
              </div>

              {/* Trial Warning for Buyers */}
              {isTrialActive && (
                <div className="mb-8 glass border border-blue-500 rounded-lg p-6">
                  <div className="flex items-center">
                    <Clock className="h-8 w-8 text-blue-500 mr-4" />
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-white">Free Trial Active</h3>
                      <p className="text-gray-400 mt-1">
                        Your free trial expires on {new Date(user.trial_expires_at).toLocaleDateString()}. 
                        Subscribe to continue posting jobs.
                      </p>
                    </div>
                    <Link
                      to="/subscription"
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
                    >
                      Subscribe Now
                    </Link>
                  </div>
                </div>
              )}

              {/* Subscription Warning for Buyers */}
              {needsSubscription && (
                <div className="mb-8 glass border border-orange-500 rounded-lg p-6">
                  <div className="flex items-center">
                    <AlertTriangle className="h-8 w-8 text-orange-500 mr-4" />
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-white">Activate Your Subscription</h3>
                      <p className="text-gray-400 mt-1">
                        Subscribe to post job requirements and access all premium features.
                      </p>
                    </div>
                    <Link
                      to="/subscription"
                      className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
                    >
                      Subscribe Now
                    </Link>
                  </div>
                </div>
              )}

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
                  {user?.role === 'buyer' ? (
                    <>
                      <div className="glass rounded-lg p-6">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                              <Building2 className="h-6 w-6 text-white" />
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
                            <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center">
                              <Clock className="h-6 w-6 text-white" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <h3 className="text-sm font-medium text-gray-400">Active Jobs</h3>
                            <p className="text-2xl font-semibold text-white">{stats.active_jobs || 0}</p>
                          </div>
                        </div>
                      </div>

                      <div className="glass rounded-lg p-6">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-orange-600 rounded-lg flex items-center justify-center">
                              <Users className="h-6 w-6 text-white" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <h3 className="text-sm font-medium text-gray-400">Bids Received</h3>
                            <p className="text-2xl font-semibold text-white">{stats.total_bids_received || 0}</p>
                          </div>
                        </div>
                      </div>

                      <div className="glass rounded-lg p-6">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                              stats.subscription_status === 'active' ? 'bg-green-600' : 
                              stats.subscription_status === 'trial' ? 'bg-blue-600' : 'bg-red-600'
                            }`}>
                              <CheckCircle className="h-6 w-6 text-white" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <h3 className="text-sm font-medium text-gray-400">Status</h3>
                            <p className="text-sm font-semibold text-white capitalize">
                              {stats.subscription_status === 'trial' ? 'Free Trial' : stats.subscription_status || 'Inactive'}
                            </p>
                          </div>
                        </div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="glass rounded-lg p-6">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
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
                            <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center">
                              <Award className="h-6 w-6 text-white" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <h3 className="text-sm font-medium text-gray-400">Won Bids</h3>
                            <p className="text-2xl font-semibold text-white">{stats.won_bids || 0}</p>
                          </div>
                        </div>
                      </div>

                      <div className="glass rounded-lg p-6">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-orange-600 rounded-lg flex items-center justify-center">
                              <TrendingUp className="h-6 w-6 text-white" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <h3 className="text-sm font-medium text-gray-400">Win Rate</h3>
                            <p className="text-2xl font-semibold text-white">{stats.win_rate || '0%'}</p>
                          </div>
                        </div>
                      </div>

                      <div className="glass rounded-lg p-6">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
                              <CheckCircle className="h-6 w-6 text-white" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <h3 className="text-sm font-medium text-gray-400">Status</h3>
                            <p className="text-sm font-semibold text-white">Verified</p>
                          </div>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* Quick Actions */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="glass rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
                  <div className="space-y-3">
                    {user?.role === 'buyer' ? (
                      <>
                        <Link
                          to="/jobs"
                          className="flex items-center p-3 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors group"
                        >
                          <Plus className="h-5 w-5 text-orange-500 mr-3" />
                          <span className="text-white group-hover:text-orange-400">Post New Job</span>
                        </Link>
                        <Link
                          to="/jobs"
                          className="flex items-center p-3 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors group"
                        >
                          <Building2 className="h-5 w-5 text-orange-500 mr-3" />
                          <span className="text-white group-hover:text-orange-400">View My Jobs</span>
                        </Link>
                        <Link
                          to="/bids"
                          className="flex items-center p-3 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors group"
                        >
                          <Users className="h-5 w-5 text-orange-500 mr-3" />
                          <span className="text-white group-hover:text-orange-400">Review Bids</span>
                        </Link>
                      </>
                    ) : (
                      <>
                        <Link
                          to="/jobs"
                          className="flex items-center p-3 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors group"
                        >
                          <Building2 className="h-5 w-5 text-orange-500 mr-3" />
                          <span className="text-white group-hover:text-orange-400">Browse Jobs</span>
                        </Link>
                        <Link
                          to="/bids"
                          className="flex items-center p-3 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors group"
                        >
                          <DollarSign className="h-5 w-5 text-orange-500 mr-3" />
                          <span className="text-white group-hover:text-orange-400">My Bids</span>
                        </Link>
                        <Link
                          to="/bids"
                          className="flex items-center p-3 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors group"
                        >
                          <Award className="h-5 w-5 text-orange-500 mr-3" />
                          <span className="text-white group-hover:text-orange-400">Won Projects</span>
                        </Link>
                      </>
                    )}
                  </div>
                </div>

                <div className="glass rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
                  <div className="space-y-4">
                    <div className="text-center text-gray-400 py-8">
                      <Clock className="h-12 w-12 mx-auto mb-3 opacity-50" />
                      <p>No recent activity</p>
                      <p className="text-sm">Start by {user?.role === 'buyer' ? 'posting a job' : 'browsing available jobs'}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;