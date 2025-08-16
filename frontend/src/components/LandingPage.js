import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Building2, Users, Shield, CheckCircle, TrendingUp, Clock, Star } from 'lucide-react';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Navigation */}
      <nav className="glass border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <Building2 className="h-8 w-8 text-orange-500" />
              <span className="text-2xl font-bold text-white">BuildBidz</span>
            </div>
            <div className="flex space-x-4">
              <Link 
                to="/auth" 
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Sign In
              </Link>
              <Link 
                to="/auth" 
                className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center">
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1694521787193-9293daeddbaa?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzZ8MHwxfHNlYXJjaHwxfHxjb25zdHJ1Y3Rpb24lMjB3b3JrZXJzfGVufDB8fHx8MTc1NTMyNjg1MXww&ixlib=rb-4.1.0&q=85')`
          }}
        >
          <div className="hero-overlay absolute inset-0"></div>
        </div>
        
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="hero-text text-4xl md:text-6xl font-bold text-white mb-6">
              India's Premier{' '}
              <span className="text-orange-500">Construction</span>{' '}
              Marketplace
            </h1>
            <p className="hero-subtitle text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
              Connect construction companies with verified suppliers and contractors. 
              Streamline procurement, compare bids, and build with confidence.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                to="/auth" 
                className="bg-orange-600 hover:bg-orange-700 text-white px-8 py-4 rounded-lg text-lg font-semibold inline-flex items-center transition-colors"
              >
                Start Building
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link 
                to="#features" 
                className="glass border border-gray-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-800 transition-colors"
              >
                Learn More
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Why Choose BuildBidz?
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              The only platform you need to manage your construction procurement
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="card-hover glass p-8 rounded-xl text-center">
              <div className="feature-accent w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
                <Users className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Verified Network</h3>
              <p className="text-gray-400">
                Access to thousands of verified suppliers and contractors across India
              </p>
            </div>

            <div className="card-hover glass p-8 rounded-xl text-center">
              <div className="bg-blue-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Secure Transactions</h3>
              <p className="text-gray-400">
                End-to-end security with escrow payments and digital documentation
              </p>
            </div>

            <div className="card-hover glass p-8 rounded-xl text-center">
              <div className="bg-green-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
                <TrendingUp className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">AI-Powered Matching</h3>
              <p className="text-gray-400">
                Smart bid ranking and supplier matching based on your requirements
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-400">
              Simple, efficient, transparent
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-orange-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-6 text-white font-bold text-xl">
                1
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Post Requirements</h3>
              <p className="text-gray-400">
                Construction companies post their material, labor, or machinery requirements
              </p>
            </div>

            <div className="text-center">
              <div className="bg-orange-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-6 text-white font-bold text-xl">
                2
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Receive Bids</h3>
              <p className="text-gray-400">
                Verified suppliers and contractors submit competitive bids with pricing and timelines
              </p>
            </div>

            <div className="text-center">
              <div className="bg-orange-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-6 text-white font-bold text-xl">
                3
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Award & Execute</h3>
              <p className="text-gray-400">
                Compare bids, award projects, and manage execution with built-in communication tools
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-400">
              Choose the plan that works for your business
            </p>
          </div>

          <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8">
            {/* Suppliers - Free */}
            <div className="glass p-8 rounded-xl border border-gray-600">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-white mb-2">Suppliers & Contractors</h3>
                <div className="text-4xl font-bold text-green-500 mb-2">FREE</div>
                <p className="text-gray-400">Always free for suppliers</p>
              </div>
              <ul className="space-y-4 mb-8">
                <li className="flex items-center text-gray-300">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                  View unlimited job postings
                </li>
                <li className="flex items-center text-gray-300">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                  Submit unlimited bids
                </li>
                <li className="flex items-center text-gray-300">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                  Direct communication with buyers
                </li>
                <li className="flex items-center text-gray-300">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                  Document sharing capabilities
                </li>
              </ul>
              <Link 
                to="/auth"
                className="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-6 rounded-lg font-semibold text-center block transition-colors"
              >
                Join as Supplier
              </Link>
            </div>

            {/* Buyers - Paid */}
            <div className="glass p-8 rounded-xl border border-orange-500 relative">
              <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <span className="bg-orange-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                  Most Popular
                </span>
              </div>
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-white mb-2">Construction Companies</h3>
                <div className="text-4xl font-bold text-orange-500 mb-2">₹5,000</div>
                <p className="text-gray-400">per year (₹416/month)</p>
              </div>
              <ul className="space-y-4 mb-8">
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
                  AI-powered bid comparison
                </li>
                <li className="flex items-center text-gray-300">
                  <CheckCircle className="h-5 w-5 text-orange-500 mr-3" />
                  Project management tools
                </li>
                <li className="flex items-center text-gray-300">
                  <CheckCircle className="h-5 w-5 text-orange-500 mr-3" />
                  Priority support
                </li>
              </ul>
              <Link 
                to="/auth"
                className="w-full bg-orange-600 hover:bg-orange-700 text-white py-3 px-6 rounded-lg font-semibold text-center block transition-colors"
              >
                Start Free Trial
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-orange-500 mb-2">10,000+</div>
              <div className="text-gray-400">Verified Suppliers</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-orange-500 mb-2">₹500Cr+</div>
              <div className="text-gray-400">Projects Completed</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-orange-500 mb-2">98%</div>
              <div className="text-gray-400">Customer Satisfaction</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-orange-500 mb-2">24/7</div>
              <div className="text-gray-400">Support Available</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gray-800">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Transform Your Construction Business?
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Join thousands of construction professionals who trust BuildBidz for their procurement needs
          </p>
          <Link 
            to="/auth"
            className="bg-orange-600 hover:bg-orange-700 text-white px-12 py-4 rounded-lg text-xl font-semibold inline-flex items-center transition-colors"
          >
            Get Started Today
            <ArrowRight className="ml-3 h-6 w-6" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 border-t border-gray-700 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Building2 className="h-8 w-8 text-orange-500" />
              <span className="text-2xl font-bold text-white">BuildBidz</span>
            </div>
            <p className="text-gray-400">© 2025 BuildBidz. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;