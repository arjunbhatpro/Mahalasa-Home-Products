import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { ShoppingBag, Package, CreditCard, Shield } from 'lucide-react';
import { motion } from 'framer-motion';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-orange-50">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center"
        >
          <h1 className="text-6xl md:text-7xl font-bold mb-6">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-orange-600 via-amber-600 to-orange-500">
              ShopHub
            </span>
          </h1>
          <p className="text-xl md:text-2xl text-slate-700 mb-8 max-w-3xl mx-auto">
            Your Premium Shopping Destination
          </p>
          <p className="text-lg text-slate-600 mb-12 max-w-2xl mx-auto">
            Experience seamless online shopping with secure payments, fast delivery, and exceptional customer service
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/login">
              <Button size="lg" className="text-lg px-8" data-testid="get-started-btn">
                <ShoppingBag className="mr-2 h-5 w-5" />
                Get Started
              </Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline" className="text-lg px-8" data-testid="admin-login-btn">
                <Shield className="mr-2 h-5 w-5" />
                Admin Login
              </Button>
            </Link>
          </div>
        </motion.div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20">
          {[
            {
              icon: <CreditCard className="h-10 w-10 text-violet-600" />,
              title: 'Flexible Payments',
              description: 'Pay online via UPI or choose Cash on Delivery'
            },
            {
              icon: <Package className="h-10 w-10 text-emerald-600" />,
              title: 'Fast Delivery',
              description: 'Track your orders in real-time with expected delivery dates'
            },
            {
              icon: <Shield className="h-10 w-10 text-purple-600" />,
              title: 'Secure Shopping',
              description: 'Your data is protected with industry-standard security'
            }
          ].map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 * index, duration: 0.6 }}
            >
              <div className="bg-white rounded-xl p-8 shadow-lg border border-slate-100 hover:shadow-xl transition-shadow">
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">{feature.title}</h3>
                <p className="text-slate-600">{feature.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
