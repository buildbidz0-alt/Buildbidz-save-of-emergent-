import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Building2, Eye, EyeOff, User, Mail, Phone, MapPin } from 'lucide-react';
import { AuthContext } from '../App';
import axios from 'axios';

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login, API } = useContext(AuthContext);
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    company_name: '',
    contact_phone: '',
    role: 'buyer',
    gst_number: '',
    address: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const payload = isLogin 
        ? { email: formData.email, password: formData.password }
        : formData;

      const response = await axios.post(`${API}${endpoint}`, payload);
      
      login(response.data.access_token, response.data.user);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col lg:flex-row">
      {/* Left side - Branding */}
      <div className="lg:w-1/2 bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center p-8">
        <div className="max-w-md text-center">
          <div className="flex items-center justify-center space-x-3 mb-8">
            <Building2 className="h-12 w-12 text-orange-500" />
            <span className="text-4xl font-bold text-white">BuildBidz</span>
          </div>
          <h2 className="text-3xl font-bold text-white mb-4">
            Welcome to India's Premier Construction Marketplace
          </h2>
          <p className="text-gray-300 text-lg">
            Connect with verified suppliers and contractors. Streamline your construction procurement process.
          </p>
          <div className="mt-8 space-y-4">
            <div className="flex items-center text-gray-300">
              <div className="w-2 h-2 bg-orange-500 rounded-full mr-3"></div>
              <span>1000+ Registered Suppliers</span>
            </div>
            <div className="flex items-center text-gray-300">
              <div className="w-2 h-2 bg-orange-500 rounded-full mr-3"></div>
              <span>Projects Worth ₹100+ Crore Completed</span>
            </div>
            <div className="flex items-center text-gray-300">
              <div className="w-2 h-2 bg-orange-500 rounded-full mr-3"></div>
              <span>24/7 Support Available</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Form */}
      <div className="lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-white mb-2">
              {isLogin ? 'Welcome Back' : 'Create Account'}
            </h3>
            <p className="text-gray-400">
              {isLogin 
                ? 'Sign in to your BuildBidz account' 
                : 'Join the construction marketplace revolution'
              }
            </p>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          <div className="glass p-8 rounded-xl">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Email */}
              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    placeholder="Enter your email"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    className="w-full pl-4 pr-12 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-300"
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>

              {/* Registration fields */}
              {!isLogin && (
                <>
                  {/* Role Selection */}
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      I am a
                    </label>
                    <div className="grid grid-cols-2 gap-4">
                      <button
                        type="button"
                        onClick={() => setFormData({...formData, role: 'buyer'})}
                        className={`p-4 rounded-lg border text-center transition-colors ${
                          formData.role === 'buyer'
                            ? 'border-orange-500 bg-orange-500/10 text-orange-400'
                            : 'border-gray-600 bg-gray-800 text-gray-300 hover:border-gray-500'
                        }`}
                      >
                        <Building2 className="h-6 w-6 mx-auto mb-2" />
                        <div className="font-medium">Construction Company</div>
                        <div className="text-xs opacity-75">Post requirements</div>
                      </button>
                      <button
                        type="button"
                        onClick={() => setFormData({...formData, role: 'supplier'})}
                        className={`p-4 rounded-lg border text-center transition-colors ${
                          formData.role === 'supplier'
                            ? 'border-orange-500 bg-orange-500/10 text-orange-400'
                            : 'border-gray-600 bg-gray-800 text-gray-300 hover:border-gray-500'
                        }`}
                      >
                        <User className="h-6 w-6 mx-auto mb-2" />
                        <div className="font-medium">Supplier/Contractor</div>
                        <div className="text-xs opacity-75">Submit bids</div>
                      </button>
                    </div>
                  </div>

                  {/* Company Name */}
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      Company Name
                    </label>
                    <input
                      type="text"
                      name="company_name"
                      value={formData.company_name}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      placeholder="Enter company name"
                    />
                  </div>

                  {/* Contact Phone */}
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      Contact Phone
                    </label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <input
                        type="tel"
                        name="contact_phone"
                        value={formData.contact_phone}
                        onChange={handleChange}
                        required
                        className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                        placeholder="Enter phone number"
                      />
                    </div>
                  </div>

                  {/* GST Number */}
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      GST Number *
                    </label>
                    <input
                      type="text"
                      name="gst_number"
                      value={formData.gst_number}
                      onChange={handleChange}
                      required
                      pattern="[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}"
                      title="Please enter a valid 15-digit GST number (e.g., 27ABCDE1234F1Z5)"
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      placeholder="Enter GST number (e.g., 27ABCDE1234F1Z5)"
                    />
                  </div>

                  {/* Address */}
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      Business Address *
                    </label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                      <textarea
                        name="address"
                        value={formData.address}
                        onChange={handleChange}
                        required
                        rows={3}
                        className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                        placeholder="Enter complete business address with city, state, and pincode"
                      />
                    </div>
                  </div>
                </>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-orange-600/50 text-white py-3 px-4 rounded-lg font-semibold transition-colors"
              >
                {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
              </button>
            </form>

            {/* Toggle Form */}
            <div className="mt-6 text-center">
              <p className="text-gray-400">
                {isLogin ? "Don't have an account? " : "Already have an account? "}
                <button
                  onClick={() => setIsLogin(!isLogin)}
                  className="text-orange-500 hover:text-orange-400 font-medium"
                >
                  {isLogin ? 'Sign up' : 'Sign in'}
                </button>
              </p>
            </div>
          </div>

          {/* Back to Home */}
          <div className="mt-6 text-center">
            <Link 
              to="/" 
              className="text-gray-400 hover:text-gray-300 text-sm"
            >
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;