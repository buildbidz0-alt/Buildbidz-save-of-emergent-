import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Building2, ArrowLeft, Target, Users, TrendingUp, CheckCircle, 
  Zap, Shield, Globe, Award, Mail, Phone
} from 'lucide-react';

const AboutPage = () => {
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Navigation */}
      <nav className="glass border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link to="/" className="flex items-center text-gray-400 hover:text-white mr-8">
                <ArrowLeft className="h-5 w-5 mr-2" />
                Home
              </Link>
              <div className="flex items-center space-x-3">
                <Building2 className="h-8 w-8 text-orange-500" />
                <span className="text-xl font-bold text-white">About BuildBidz</span>
              </div>
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
      <section className="py-20 bg-gray-800">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
            About <span className="text-orange-500">BuildBidz</span>
          </h1>
          <p className="text-xl text-gray-300 leading-relaxed">
            BuildBidz is a digital procurement platform on a mission to organize one of India's largest and most unorganized sectors — the construction and infrastructure industry.
          </p>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-16 bg-gray-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="glass rounded-xl p-8 mb-12">
            <h2 className="text-2xl font-bold text-white mb-6">Our Mission</h2>
            <p className="text-gray-300 text-lg leading-relaxed mb-6">
              Every day, critical sourcing decisions are made over phone calls, WhatsApp chats, and informal networks. BuildBidz replaces this fragmented process with a transparent, structured, and efficient digital marketplace. We connect construction companies (buyers) with verified suppliers and contractors (vendors) who can bid on requirements for materials, labor, or machinery—all in one centralized platform.
            </p>
            <p className="text-gray-300 text-lg leading-relaxed">
              From posting job requirements to comparing bids, awarding jobs, chatting, and sharing files—BuildBidz streamlines the entire procurement lifecycle. We are bringing structure, speed, and scale to an industry that's long overdue for digital transformation.
            </p>
          </div>

          {/* Goal Section */}
          <div className="glass rounded-xl p-8 mb-12">
            <div className="flex items-center mb-6">
              <Target className="h-8 w-8 text-orange-500 mr-4" />
              <h2 className="text-2xl font-bold text-white">Our Goal</h2>
            </div>
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-orange-400 mb-4">
                Our goal is bold but clear:
              </h3>
              <p className="text-lg text-white mb-4">
                To organize India's largest unorganized sector—the construction and infrastructure industry—and to democratize access to opportunities.
              </p>
              <p className="text-gray-300 leading-relaxed">
                We believe that every supplier, no matter their size or network, deserves a fair shot at growth. And every construction company deserves a transparent, reliable way to procure what they need. BuildBidz is building that bridge.
              </p>
            </div>

            <h3 className="text-xl font-semibold text-white mb-4">By digitizing procurement, we aim to:</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-start">
                  <CheckCircle className="h-6 w-6 text-green-500 mr-3 mt-1" />
                  <p className="text-gray-300">
                    Bring transparency, accountability, and efficiency to the sourcing process
                  </p>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-6 w-6 text-green-500 mr-3 mt-1" />
                  <p className="text-gray-300">
                    Open up equal access to jobs for verified suppliers and contractors across India
                  </p>
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-start">
                  <CheckCircle className="h-6 w-6 text-green-500 mr-3 mt-1" />
                  <p className="text-gray-300">
                    Help buyers make faster, smarter decisions with real-time data and competitive bids
                  </p>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-6 w-6 text-green-500 mr-3 mt-1" />
                  <p className="text-gray-300">
                    Create a level playing field that benefits everyone—from small vendors to large developers
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-8 p-6 bg-orange-500/10 border border-orange-500/30 rounded-lg">
              <p className="text-lg font-semibold text-orange-400 text-center">
                We're not just improving procurement—we're reshaping how India builds.
              </p>
            </div>
          </div>

          {/* Values Section */}
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="glass rounded-xl p-6 text-center">
              <div className="w-16 h-16 bg-orange-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Speed</h3>
              <p className="text-gray-400">
                Accelerating procurement cycles from weeks to days through digital efficiency
              </p>
            </div>

            <div className="glass rounded-xl p-6 text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Trust</h3>
              <p className="text-gray-400">
                Building confidence through verified suppliers, transparent processes, and secure transactions
              </p>
            </div>

            <div className="glass rounded-xl p-6 text-center">
              <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Globe className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Scale</h3>
              <p className="text-gray-400">
                Connecting thousands of suppliers with construction companies across India
              </p>
            </div>
          </div>

          {/* Impact Stats */}
          <div className="glass rounded-xl p-8 mb-12">
            <h2 className="text-2xl font-bold text-white text-center mb-8">Our Impact</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
              <div>
                <div className="text-3xl font-bold text-orange-500 mb-2">10,000+</div>
                <div className="text-gray-400">Verified Suppliers</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-orange-500 mb-2">₹500Cr+</div>
                <div className="text-gray-400">Projects Completed</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-orange-500 mb-2">98%</div>
                <div className="text-gray-400">Customer Satisfaction</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-orange-500 mb-2">24/7</div>
                <div className="text-gray-400">Support Available</div>
              </div>
            </div>
          </div>

          {/* Contact Section */}
          <div className="glass rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white text-center mb-8">Get in Touch</h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-orange-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Phone className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Phone Support</h3>
                <p className="text-orange-400 text-lg font-medium">+91 8709326986</p>
                <p className="text-gray-400 text-sm">Available 24/7</p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Mail className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Email Support</h3>
                <p className="text-blue-400 text-lg font-medium">support@buildbidz.co.in</p>
                <p className="text-gray-400 text-sm">We'll respond within 24 hours</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gray-800">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-white mb-6">
            Ready to Transform Your Construction Business?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Join thousands of construction professionals who trust BuildBidz for their procurement needs
          </p>
          <Link 
            to="/auth"
            className="bg-orange-600 hover:bg-orange-700 text-white px-12 py-4 rounded-lg text-xl font-semibold inline-flex items-center transition-colors"
          >
            Get Started Today
            <Building2 className="ml-3 h-6 w-6" />
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

export default AboutPage;