import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { parseApiError } from '../utils/errorHandler';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { toast } from 'sonner';
import { CreditCard, Banknote, QrCode, CheckCircle2 } from 'lucide-react';

const CheckoutPage = () => {
  const { cart, cartTotal, clearCart } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [paymentType, setPaymentType] = useState('upi');
  const [showQRModal, setShowQRModal] = useState(false);
  const [qrData, setQrData] = useState(null);
  const [orderId, setOrderId] = useState(null);

  const [formData, setFormData] = useState({
    phone: user?.phone || '',
    address: '',
    state: 'Karnataka'
  });

  const handleCreateOrder = async (e) => {
    e.preventDefault();
    
    if (!formData.phone || !formData.address || !formData.state) {
      toast.error('Please fill all fields');
      return;
    }

    if (!cart.items || cart.items.length === 0) {
      toast.error('Cart is empty');
      return;
    }

    setLoading(true);

    try {
      // Calculate courier charge
      const courierResponse = await api.post('/orders/calculate-courier', {
        state: formData.state,
        items: cart.items.map(item => ({
          product_name: item.product?.name,
          quantity: item.quantity
        })),
        subtotal: cartTotal
      });
      
      const courierCharge = courierResponse.data.courier_charge;
      const finalTotal = cartTotal + courierCharge;

      // Create order
      const orderPayload = {
        items: cart.items.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity
        })),
        shipping_address: formData.address,
        phone: formData.phone,
        state: formData.state,
        courier_charge: courierCharge,
        payment_type: paymentType
      };

      const orderResponse = await api.post('/orders', orderPayload);
      const order = orderResponse.data;
      setOrderId(order.id);

      if (paymentType === 'cod') {
        // COD - Order confirmed immediately
        toast.success('Order placed successfully!');
        await clearCart();
        navigate(`/orders/${order.id}`);
      } else {
        // UPI - Show QR code
        const paymentResponse = await api.post('/payments/initiate', {
          order_id: order.id,
          amount: finalTotal
        });

        setQrData(paymentResponse.data);
        setShowQRModal(true);
      }
    } catch (error) {
      console.error('Order creation error:', error);
      toast.error(parseApiError(error));
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentComplete = async () => {
    // In real implementation, this would be triggered by webhook
    // For demo, we'll simulate payment verification
    toast.success('Payment initiated! Please scan the QR code with any UPI app');
    setShowQRModal(false);
    await clearCart();
    navigate(`/orders/${orderId}`);
  };

  if (!cart.items || cart.items.length === 0) {
    navigate('/cart');
    return null;
  }

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">Checkout</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Checkout Form */}
          <div>
            <form onSubmit={handleCreateOrder} className="space-y-6">
              {/* Shipping Details */}
              <Card>
                <CardHeader>
                  <CardTitle>Shipping Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number *</Label>
                    <Input
                      id="phone"
                      data-testid="checkout-phone"
                      placeholder="+91XXXXXXXXXX"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="state">State *</Label>
                    <Select
                      value={formData.state}
                      onValueChange={(value) => setFormData({ ...formData, state: value })}
                    >
                      <SelectTrigger data-testid="checkout-state">
                        <SelectValue placeholder="Select state" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Karnataka">Karnataka</SelectItem>
                        <SelectItem value="Andhra Pradesh">Andhra Pradesh</SelectItem>
                        <SelectItem value="Maharashtra">Maharashtra</SelectItem>
                        <SelectItem value="Tamil Nadu">Tamil Nadu</SelectItem>
                        <SelectItem value="Kerala">Kerala</SelectItem>
                        <SelectItem value="Telangana">Telangana</SelectItem>
                        <SelectItem value="Goa">Goa</SelectItem>
                        <SelectItem value="Gujarat">Gujarat</SelectItem>
                        <SelectItem value="Rajasthan">Rajasthan</SelectItem>
                        <SelectItem value="Delhi">Delhi</SelectItem>
                        <SelectItem value="Other">Other State</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-muted-foreground">
                      {formData.state === 'Karnataka' && cartTotal < 350 ? 
                        'Courier charge: ₹30 (Karnataka, order < ₹350)' : 
                        formData.state !== 'Karnataka' ? 
                        'Courier charges calculated based on weight' : 
                        'Free shipping for orders ≥ ₹350'
                      }
                    </p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="address">Shipping Address *</Label>
                    <Textarea
                      id="address"
                      data-testid="checkout-address"
                      placeholder="Enter your complete shipping address"
                      rows={4}
                      value={formData.address}
                      onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                      required
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Payment Method */}
              <Card>
                <CardHeader>
                  <CardTitle>Payment Method</CardTitle>
                  <CardDescription>Choose how you'd like to pay</CardDescription>
                </CardHeader>
                <CardContent>
                  <RadioGroup value={paymentType} onValueChange={setPaymentType}>
                    <div className="space-y-3">
                      <div
                        className={`flex items-center space-x-3 p-4 border-2 rounded-lg cursor-pointer transition-all ${
                          paymentType === 'upi' ? 'border-orange-500 bg-orange-50' : 'border-slate-200'
                        }`}
                        onClick={() => setPaymentType('upi')}
                        data-testid="payment-upi"
                      >
                        <RadioGroupItem value="upi" id="upi" />
                        <Label htmlFor="upi" className="flex items-center gap-3 cursor-pointer flex-1">
                          <CreditCard className="h-5 w-5 text-orange-600" />
                          <div>
                            <div className="font-semibold">Pay Now (UPI)</div>
                            <div className="text-sm text-slate-600">Pay online via UPI</div>
                          </div>
                        </Label>
                      </div>

                      <div
                        className={`flex items-center space-x-3 p-4 border-2 rounded-lg cursor-pointer transition-all ${
                          paymentType === 'cod' ? 'border-emerald-500 bg-emerald-50' : 'border-slate-200'
                        }`}
                        onClick={() => setPaymentType('cod')}
                        data-testid="payment-cod"
                      >
                        <RadioGroupItem value="cod" id="cod" />
                        <Label htmlFor="cod" className="flex items-center gap-3 cursor-pointer flex-1">
                          <Banknote className="h-5 w-5 text-emerald-600" />
                          <div>
                            <div className="font-semibold">Cash on Delivery</div>
                            <div className="text-sm text-slate-600">Pay when you receive</div>
                          </div>
                        </Label>
                      </div>
                    </div>
                  </RadioGroup>
                </CardContent>
              </Card>

              <Button
                type="submit"
                className="w-full"
                size="lg"
                disabled={loading}
                data-testid="place-order-btn"
              >
                {loading ? 'Processing...' : paymentType === 'cod' ? 'Place Order' : 'Proceed to Payment'}
              </Button>
            </form>
          </div>

          {/* Order Summary */}
          <div>
            <Card className="sticky top-4">
              <CardHeader>
                <CardTitle>Order Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  {cart.items.map((item) => (
                    <div key={item.product_id} className="flex justify-between text-sm">
                      <span className="text-slate-600">
                        {item.product?.name} x {item.quantity} {item.product?.unit}
                      </span>
                      <span className="font-semibold">
                        ₹{(item.product?.price * item.quantity).toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
                <div className="border-t pt-4 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Subtotal</span>
                    <span className="font-semibold">₹{cartTotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Shipping</span>
                    <span className="font-semibold text-emerald-600">FREE</span>
                  </div>
                  <div className="flex justify-between text-lg font-bold pt-2 border-t">
                    <span>Total</span>
                    <span className="text-orange-600">₹{cartTotal.toFixed(2)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* QR Code Modal for UPI Payment */}
        <Dialog open={showQRModal} onOpenChange={setShowQRModal}>
          <DialogContent className="sm:max-w-md" data-testid="qr-modal">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <QrCode className="h-5 w-5" />
                Scan QR Code to Pay
              </DialogTitle>
              <DialogDescription>
                Use any UPI app (PhonePe, GPay, Paytm, etc.) to scan and pay
              </DialogDescription>
            </DialogHeader>
            {qrData && (
              <div className="space-y-4">
                <div className="bg-slate-100 p-6 rounded-lg flex flex-col items-center">
                  <div className="w-64 h-64 bg-white rounded-lg flex items-center justify-center mb-4">
                    <img
                      src={qrData.qr_code_url}
                      alt="UPI QR Code"
                      className="w-full h-full object-contain"
                      onError={(e) => {
                        e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><rect width="200" height="200" fill="%23f1f5f9"/><text x="50%" y="50%" text-anchor="middle" fill="%2364748b" font-size="14">QR Code</text></svg>';
                      }}
                    />
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-violet-600">₹{qrData.amount}</p>
                    <p className="text-sm text-slate-600 mt-1">Amount to pay</p>
                  </div>
                </div>
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <p className="text-sm text-amber-800">
                    <strong>Demo Mode:</strong> This is a mock QR code. In production, scan with any UPI app to complete payment.
                  </p>
                </div>
                <Button
                  className="w-full"
                  onClick={handlePaymentComplete}
                  data-testid="payment-complete-btn"
                >
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  I've Completed Payment
                </Button>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default CheckoutPage;
