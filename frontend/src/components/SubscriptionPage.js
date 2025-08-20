import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import { 
  Building2, CheckCircle, ArrowLeft, CreditCard, Shield, Clock,
  Award, Users, TrendingUp, Star
} from 'lucide-react';
import axios from 'axios';

const SubscriptionPage = () => {
  const { user, API } = useContext(AuthContext);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubscribe = async () => {
    setLoading(true);
    setError('');

    try {
      // Create Razorpay order
      const orderResponse = await axios.post(`${API}/payments/create-subscription-order`);
      const order = orderResponse.data;

      // Initialize Razorpay
      const options = {
        key: 'rzp_live_R5uXLNwkjvkrju', // This should ideally come from environment
        amount: order.amount,
        currency: 'INR',
        name: 'BuildBidz',
        description: 'Annual Subscription for Construction Companies',
        order_id: order.id,
        handler: async function (response) {
          try {
            // Verify payment
            const formData = new FormData();
            formData.append('order_id', response.razorpay_order_id);
            formData.append('payment_id', response.razorpay_payment_id);
            formData.append('signature', response.razorpay_signature);

            await axios.post(`${API}/payments/verify-subscription`, formData);
            
            // Redirect to dashboard with success message
            navigate('/dashboard');
            window.location.reload(); // Refresh to update user context
          } catch (error) {
            setError('Payment verification failed. Please contact support.');
          }
        },
        prefill: {
          name: user?.company_name,
          email: user?.email,
          contact: user?.contact_phone
        },
        theme: {
          color: '#f97316'
        }
      };

      const rzp = new window.Razorpay(options);
      rzp.open();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to create payment order');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center mb-8">
          <Link
            to="/dashboard"
            className="flex items-center text-gray-400 hover:text-white transition-colors mr-4"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Back to Dashboard
          </Link>
        </div>

        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <Building2 className="h-10 w-10 text-orange-500 mr-3" />
            <h1 className="text-4xl font-bold text-white">BuildBidz Subscription</h1>
          </div>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Unlock the full potential of BuildBidz with our comprehensive subscription plan
          </p>
        </div>

        {/* Subscription Status */}
        {user?.subscription_status === 'active' ? (
          <div className="glass rounded-xl p-8 mb-8 border border-green-500">
            <div className="text-center">
              <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-white mb-2">Subscription Active</h2>
              <p className="text-gray-400 mb-4">
                Your subscription is active and expires on{' '}
                {user?.subscription_expires_at ? 
                  new Date(user.subscription_expires_at).toLocaleDateString() : 
                  'Never'
                }
              </p>
              <div className="flex justify-center space-x-4">
                <Link
                  to="/jobs"
                  className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
                >
                  Post New Job
                </Link>
                <Link
                  to="/dashboard"
                  className="glass border border-gray-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors"
                >
                  Go to Dashboard
                </Link>
              </div>
            </div>
          </div>
        ) : (
          <>
            {/* Pricing Card */}
            <div className="glass rounded-xl p-8 border border-orange-500 relative mb-8">
              <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <span className="bg-orange-600 text-white px-6 py-2 rounded-full text-sm font-semibold">
                  Best Value
                </span>
              </div>
              
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-white mb-4">
                  Monthly Subscription for Construction Companies
                </h2>
                <div className="flex items-center justify-center mb-4">
                  <span className="text-5xl font-bold text-orange-500">₹5,000</span>
                  <span className="text-gray-400 ml-2">/month</span>
                </div>
                <p className="text-gray-400 mb-6">
                  Start with a 1-month free trial! Cancel anytime.
                </p>

                {error && (
                  <div className="bg-red-500/10 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-6">
                    {error}
                  </div>
                )}

                <button
                  onClick={handleSubscribe}
                  disabled={loading}
                  className="bg-orange-600 hover:bg-orange-700 disabled:bg-orange-600/50 text-white px-12 py-4 rounded-lg text-xl font-semibold transition-colors inline-flex items-center"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <CreditCard className="mr-3 h-6 w-6" />
                      Subscribe Now
                    </>
                  )}
                </button>
              </div>

              {/* Features */}
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-4">Core Features</h3>
                  <ul className="space-y-3">
                    <li className="flex items-center text-gray-300">
                      <CheckCircle className="h-5 w-5 text-orange-500 mr-3" />
                      Unlimited job postings
                    </li>
                    <li className="flex items-center text-gray-300">
                      <CheckCircle className="h-5 w-5 text-orange-500 mr-3" />
                      Access to all verified suppliers
                    </li>
                    <li className="flex items-center text-gray-300">
                      <CheckCircle className="h-5 w-5 text-orange-500 mr-3" />
                      Advanced bid comparison tools
                    </li>
                    <li className="flex items-center text-gray-300">
                      <CheckCircle className="h-5 w-5 text-orange-500 mr-3" />
                      Project management dashboard
                    </li>
                    <li className="flex items-center text-gray-300">
                      <CheckCircle className="h-5 w-5 text-orange-500 mr-3" />
                      Document sharing & file uploads
                    </li>
                  </ul>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-4">Premium Benefits</h3>
                  <ul className="space-y-3">
                    <li className="flex items-center text-gray-300">
                      <CheckCircle className="h-5 w-5 text-orange-500 mr-3" />
                      AI-powered bid ranking
                    </li>
                    <li className="flex items-center text-gray-300">
                      <CheckCircle className="h-5 w-5 text-orange-500 mr-3" />
                      Priority customer support
                    </li>
                    <li className="flex items-center text-gray-300">
                      <CheckCircle className="h-5 w-5 text-orange-500 mr-3" />
                      Advanced analytics & reports
                    </li>
                    <li className="flex items-center text-gray-300">
                      <CheckCircle className="h-5 w-5 text-orange-500 mr-3" />
                      Bulk job posting tools
                    </li>
                    <li className="flex items-center text-gray-300">
                      <CheckCircle className="h-5 w-5 text-orange-500 mr-3" />
                      Integration with GST & invoicing
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Trust Indicators */}
            <div className="grid md:grid-cols-3 gap-6 mb-8">
              <div className="glass p-6 rounded-lg text-center">
                <Shield className="h-12 w-12 text-green-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">Secure Payments</h3>
                <p className="text-gray-400 text-sm">
                  Powered by Razorpay with bank-grade security
                </p>
              </div>
              <div className="glass p-6 rounded-lg text-center">
                <Award className="h-12 w-12 text-blue-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">Verified Network</h3>
                <p className="text-gray-400 text-sm">
                  10,000+ verified suppliers and contractors
                </p>
              </div>
              <div className="glass p-6 rounded-lg text-center">
                <Clock className="h-12 w-12 text-orange-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">24/7 Support</h3>
                <p className="text-gray-400 text-sm">
                  Round-the-clock customer support
                </p>
              </div>
            </div>

            {/* Testimonials */}
            <div className="glass rounded-xl p-8">
              <h3 className="text-2xl font-bold text-white text-center mb-8">
                What Our Customers Say
              </h3>
              <div className="grid md:grid-cols-2 gap-8">
                <div className="text-center">
                  <div className="flex justify-center mb-4">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-5 w-5 text-yellow-500 fill-current" />
                    ))}
                  </div>
                  <p className="text-gray-300 mb-4">
                    "BuildBidz revolutionized our procurement process. We saved 30% on costs and reduced project timelines significantly."
                  </p>
                  <p className="text-orange-500 font-semibold">- Rajesh Kumar, Site Manager</p>
                </div>
                <div className="text-center">
                  <div className="flex justify-center mb-4">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-5 w-5 text-yellow-500 fill-current" />
                    ))}
                  </div>
                  <p className="text-gray-300 mb-4">
                    "The platform connects us with reliable suppliers. The bid comparison feature is incredibly useful."
                  </p>
                  <p className="text-orange-500 font-semibold">- Priya Sharma, Project Director</p>
                </div>
              </div>
            </div>
          </>
        )}

        {/* FAQ or Additional Info */}
        <div className="mt-12 text-center">
          <p className="text-gray-400 mb-4">
            Questions about our subscription? 
          </p>
          <div className="flex justify-center space-x-6">
            <span className="text-gray-300">📞 +91 8709326986</span>
            <span className="text-gray-300">📧 support@buildbidz.co.in</span>
          </div>
        </div>
      </div>

      {/* Load Razorpay Script */}
      <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    </div>
  );
};

export default SubscriptionPage;