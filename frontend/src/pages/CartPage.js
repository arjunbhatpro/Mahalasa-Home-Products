import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { Minus, Plus, Trash2, ShoppingBag, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';

const CartPage = () => {
  const { cart, cartTotal, updateQuantity, removeFromCart, loading } = useCart();
  const navigate = useNavigate();

  const handleUpdateQuantity = async (productId, newQuantity) => {
    const result = await updateQuantity(productId, newQuantity);
    if (!result.success) {
      toast.error(result.error);
    }
  };

  const handleRemove = async (productId) => {
    const result = await removeFromCart(productId);
    if (result.success) {
      toast.success('Item removed from cart');
    } else {
      toast.error(result.error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-lg text-slate-600">Loading cart...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link to="/products">
              <Button variant="ghost" data-testid="back-to-products">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Products
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-slate-900">Shopping Cart</h1>
            <div className="w-32"></div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {!cart.items || cart.items.length === 0 ? (
          <Card className="text-center py-12" data-testid="empty-cart">
            <CardContent className="space-y-4">
              <ShoppingBag className="mx-auto h-16 w-16 text-slate-400" />
              <h2 className="text-2xl font-semibold text-slate-900">Your cart is empty</h2>
              <p className="text-slate-600">Add some products to get started!</p>
              <Link to="/products">
                <Button className="mt-4">Browse Products</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Cart Items */}
            <div className="lg:col-span-2 space-y-4">
              {cart.items.map((item) => (
                <Card key={item.product_id} data-testid={`cart-item-${item.product_id}`}>
                  <CardContent className="p-4">
                    <div className="flex gap-4">
                      <div className="w-24 h-24 bg-slate-100 rounded-lg overflow-hidden flex-shrink-0">
                        <img
                          src={item.product?.images?.[0] || 'https://images.unsplash.com/photo-1606741965509-717b9fdd6549?crop=entropy&cs=srgb&fm=jpg&q=85'}
                          alt={item.product?.name}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg text-slate-900">
                          {item.product?.name}
                        </h3>
                        <p className="text-sm text-slate-600 mt-1">
                          {item.product?.description?.substring(0, 100)}...
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                          {item.quantity} {item.product?.unit}
                        </p>
                        <div className="flex items-center justify-between mt-3">
                          <span className="text-lg font-bold text-orange-600">
                            ₹{item.product?.price} / {item.product?.unit}
                          </span>
                          <div className="flex items-center gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleUpdateQuantity(item.product_id, item.quantity - (item.product?.weight_options?.[0] || 1))}
                              data-testid={`decrease-${item.product_id}`}
                            >
                              <Minus className="h-4 w-4" />
                            </Button>
                            <span className="w-20 text-center font-semibold" data-testid={`quantity-${item.product_id}`}>
                              {item.quantity} {item.product?.unit}
                            </span>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleUpdateQuantity(item.product_id, item.quantity + (item.product?.weight_options?.[0] || 1))}
                              disabled={item.quantity >= item.product?.stock}
                              data-testid={`increase-${item.product_id}`}
                            >
                              <Plus className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleRemove(item.product_id)}
                              data-testid={`remove-${item.product_id}`}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
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
                  <div className="border-t pt-4">
                    <div className="flex justify-between text-lg font-bold">
                      <span>Total</span>
                      <span className="text-violet-600" data-testid="cart-total">
                        ₹{cartTotal.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </CardContent>
                <CardFooter>
                  <Button
                    className="w-full"
                    size="lg"
                    onClick={() => navigate('/checkout')}
                    data-testid="proceed-checkout"
                  >
                    Proceed to Checkout
                  </Button>
                </CardFooter>
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CartPage;
