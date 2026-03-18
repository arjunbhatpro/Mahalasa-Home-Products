import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../utils/api';
import { parseApiError } from '../utils/errorHandler';
import { useCart } from '../context/CartContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardFooter } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { ShoppingCart, Plus } from 'lucide-react';
import { motion } from 'framer-motion';

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedQuantities, setSelectedQuantities] = useState({});
  const { addToCart, cartCount } = useCart();

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products');
      setProducts(response.data);
      // Initialize quantities
      const initialQuantities = {};
      response.data.forEach(product => {
        if (product.weight_options?.length > 0) {
          initialQuantities[product.id] = product.weight_options[0];
        } else if (product.piece_options?.length > 0) {
          initialQuantities[product.id] = product.piece_options[0].pieces;
        } else if (product.combo_options?.length > 0) {
          initialQuantities[product.id] = product.combo_options[0];
        } else {
          initialQuantities[product.id] = 1;
        }
      });
      setSelectedQuantities(initialQuantities);
    } catch (error) {
      toast.error(parseApiError(error));
    } finally {
      setLoading(false);
    }
  };

  const handleQuantityChange = (productId, value) => {
    setSelectedQuantities(prev => ({
      ...prev,
      [productId]: value
    }));
  };

  const handleAddToCart = async (product) => {
    const quantity = selectedQuantities[product.id] || 1;
    const result = await addToCart(product.id, parseFloat(quantity));
    if (result.success) {
      toast.success(`Added ${quantity} ${product.unit} to cart!`);
    } else {
      toast.error(result.error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-lg text-slate-600">Loading products...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-orange-600 to-amber-500">
              ShopHub
            </h1>
            <div className="flex items-center gap-4">
              <Link to="/orders">
                <Button variant="ghost" data-testid="orders-link">My Orders</Button>
              </Link>
              <Link to="/cart">
                <Button className="relative" data-testid="cart-button">
                  <ShoppingCart className="mr-2 h-4 w-4" />
                  Cart
                  {cartCount > 0 && (
                    <Badge className="absolute -top-2 -right-2 bg-emerald-500">
                      {cartCount}
                    </Badge>
                  )}
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Products Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h2 className="text-4xl font-bold text-slate-900 mb-2">Premium Collection</h2>
          <p className="text-slate-600">Discover our curated selection of exceptional products</p>
        </div>

        {products.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-600">No products available</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {products.map((product, index) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="group overflow-hidden border-slate-200 hover:shadow-xl transition-all duration-300" data-testid={`product-card-${product.id}`}>
                  <div className="aspect-square overflow-hidden bg-slate-100 relative">
                    <img
                      src={product.images?.[0] || 'https://images.unsplash.com/photo-1606741965509-717b9fdd6549?crop=entropy&cs=srgb&fm=jpg&q=85'}
                      alt={product.name}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                    />
                    {product.coming_soon && (
                      <div className="absolute inset-0 bg-black bg-opacity-60 flex items-center justify-center">
                        <span className="bg-amber-500 text-white px-4 py-2 rounded-lg font-semibold">
                          Coming Soon
                        </span>
                      </div>
                    )}
                  </div>
                  <CardContent className="p-4">
                    <h3 className="font-semibold text-lg text-slate-900 mb-1" data-testid={`product-name-${product.id}`}>
                      {product.name}
                    </h3>
                    <p className="text-sm text-slate-600 mb-3 line-clamp-2">
                      {product.description}
                    </p>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-2xl font-bold text-orange-600" data-testid={`product-price-${product.id}`}>
                        ₹{product.price}
                      </span>
                      <span className="text-sm text-slate-600">/ {product.unit}</span>
                    </div>
                    
                    {/* Quantity Selector */}
                    {product.available && !product.coming_soon && (
                      <div className="mb-3">
                        <select
                          className="w-full px-3 py-2 border border-slate-300 rounded-md bg-white text-sm"
                          value={selectedQuantities[product.id] || ''}
                          onChange={(e) => handleQuantityChange(product.id, e.target.value)}
                          data-testid={`quantity-select-${product.id}`}
                        >
                          {product.weight_options?.map(weight => (
                            <option key={weight} value={weight}>
                              {weight} kg
                            </option>
                          ))}
                          {product.piece_options?.map(option => (
                            <option key={option.pieces} value={option.pieces}>
                              {option.pieces} Pieces - ₹{option.price}
                            </option>
                          ))}
                          {product.combo_options?.map(combo => (
                            <option key={combo} value={combo}>
                              {combo} Combo{combo > 1 ? 's' : ''}
                            </option>
                          ))}
                        </select>
                      </div>
                    )}
                    
                    {product.available && !product.coming_soon && (
                      <Badge variant="default" className="bg-emerald-500">
                        Available
                      </Badge>
                    )}
                    {product.coming_soon && (
                      <Badge variant="secondary">
                        Coming Soon
                      </Badge>
                    )}
                    {!product.available && !product.coming_soon && (
                      <Badge variant="destructive">
                        Out of Stock
                      </Badge>
                    )}
                  </CardContent>
                  <CardFooter className="p-4 pt-0">
                    <Button
                      className="w-full"
                      onClick={() => handleAddToCart(product)}
                      disabled={!product.available || product.stock === 0}
                      data-testid={`add-to-cart-${product.id}`}
                    >
                      <Plus className="mr-2 h-4 w-4" />
                      {product.coming_soon ? 'Coming Soon' : 'Add to Cart'}
                    </Button>
                  </CardFooter>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductsPage;
