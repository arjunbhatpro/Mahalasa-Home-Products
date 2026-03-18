import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../utils/api';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { Package, Download, ArrowLeft, Truck, CheckCircle2, Clock } from 'lucide-react';

const OrdersPage = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const { orderId } = useParams();

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await api.get('/orders');
      setOrders(response.data);
    } catch (error) {
      toast.error('Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  const downloadInvoice = async (id) => {
    try {
      const response = await api.get(`/orders/${id}/invoice`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `invoice_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Invoice downloaded!');
    } catch (error) {
      toast.error('Failed to download invoice');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4" />;
      case 'payment_verified':
      case 'confirmed':
        return <CheckCircle2 className="h-4 w-4" />;
      case 'shipped':
        return <Truck className="h-4 w-4" />;
      case 'delivered':
        return <Package className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getStatusMessage = (order) => {
    if (order.payment_type === 'cod') {
      switch (order.order_status) {
        case 'confirmed':
          return 'Your order is confirmed and will be shipped soon';
        case 'shipped':
          return order.expected_delivery
            ? `Your order will be delivered by ${new Date(order.expected_delivery).toLocaleDateString()}`
            : 'Your order is on the way';
        case 'delivered':
          return 'Order delivered. Thank you for shopping with us!';
        default:
          return 'Processing your order';
      }
    } else {
      switch (order.order_status) {
        case 'pending':
          return 'Your order is pending payment';
        case 'payment_verified':
          return 'Payment received! Your order is confirmed';
        case 'confirmed':
          return 'Your order is confirmed and will be shipped soon';
        case 'shipped':
          return order.expected_delivery
            ? `Your order will be delivered by ${new Date(order.expected_delivery).toLocaleDateString()}`
            : 'Your order is on the way';
        case 'delivered':
          return 'Order delivered. Thank you for shopping with us!';
        default:
          return 'Processing your order';
      }
    }
  };

  const getStatusVariant = (status) => {
    switch (status) {
      case 'pending':
        return 'secondary';
      case 'payment_verified':
      case 'confirmed':
        return 'default';
      case 'shipped':
        return 'default';
      case 'delivered':
        return 'default';
      default:
        return 'secondary';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-lg text-slate-600">Loading orders...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link to="/products">
              <Button variant="ghost" data-testid="back-to-products">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Products
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-slate-900">My Orders</h1>
            <div className="w-32"></div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {orders.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent className="space-y-4">
              <Package className="mx-auto h-16 w-16 text-slate-400" />
              <h2 className="text-2xl font-semibold text-slate-900">No orders yet</h2>
              <p className="text-slate-600">Start shopping to see your orders here!</p>
              <Link to="/products">
                <Button className="mt-4">Browse Products</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {orders.map((order) => (
              <Card key={order.id} data-testid={`order-${order.id}`}>
                <CardHeader className="bg-slate-50 border-b">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">Order #{order.id.substring(0, 8)}</CardTitle>
                      <p className="text-sm text-slate-600 mt-1">
                        Placed on {new Date(order.created_at).toLocaleDateString('en-IN', {
                          day: 'numeric',
                          month: 'long',
                          year: 'numeric'
                        })}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant={getStatusVariant(order.order_status)} className="flex items-center gap-1">
                          {getStatusIcon(order.order_status)}
                          {order.order_status.replace('_', ' ').toUpperCase()}
                        </Badge>
                        <Badge variant={order.payment_type === 'cod' ? 'outline' : 'secondary'}>
                          {order.payment_type === 'cod' ? 'COD' : 'UPI'}
                        </Badge>
                      </div>
                      <Badge variant={order.payment_status === 'paid' ? 'default' : 'secondary'}>
                        Payment: {order.payment_status}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="space-y-4">
                    {/* Status Message */}
                    <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                      <p className="text-sm text-orange-900 font-medium">
                        {getStatusMessage(order)}
                      </p>
                    </div>

                    {/* Items */}
                    <div className="space-y-2">
                      {order.items.map((item, idx) => (
                        <div key={idx} className="flex justify-between items-center py-2 border-b last:border-0">
                          <div>
                            <span className="font-medium">{item.product_name}</span>
                            <span className="text-slate-600 text-sm ml-2">
                              {item.quantity} {item.unit || 'unit'}
                            </span>
                          </div>
                          <span className="font-semibold">₹{(item.price * item.quantity).toFixed(2)}</span>
                        </div>
                      ))}
                    </div>

                    {/* Total */}
                    <div className="flex justify-between items-center pt-4 border-t">
                      <span className="text-lg font-semibold">Total</span>
                      <span className="text-2xl font-bold text-orange-600">₹{order.total_amount.toFixed(2)}</span>
                    </div>

                    {/* Shipping Info */}
                    <div className="pt-4 border-t">
                      <p className="text-sm text-slate-600">
                        <strong>Shipping to:</strong> {order.shipping_address}
                      </p>
                      <p className="text-sm text-slate-600 mt-1">
                        <strong>Contact:</strong> {order.phone}
                      </p>
                    </div>

                    {/* Download Invoice */}
                    {order.payment_status === 'paid' && (
                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={() => downloadInvoice(order.id)}
                        data-testid={`download-invoice-${order.id}`}
                      >
                        <Download className="mr-2 h-4 w-4" />
                        Download Invoice
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default OrdersPage;
