import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/api';
import { useAuth } from './AuthContext';

const CartContext = createContext();

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within CartProvider');
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState({ items: [] });
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    if (user && user.role === 'customer') {
      fetchCart();
    }
  }, [user]);

  const fetchCart = async () => {
    try {
      setLoading(true);
      const response = await api.get('/cart');
      setCart(response.data);
    } catch (error) {
      console.error('Error fetching cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (productId, quantity = 1) => {
    try {
      const existingItem = cart.items.find(item => item.product_id === productId);
      let newItems;

      if (existingItem) {
        newItems = cart.items.map(item =>
          item.product_id === productId
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      } else {
        newItems = [...cart.items.map(item => ({ product_id: item.product_id, quantity: item.quantity })), { product_id: productId, quantity }];
      }

      await api.post('/cart', { items: newItems });
      await fetchCart();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Failed to add to cart' };
    }
  };

  const updateQuantity = async (productId, quantity) => {
    try {
      let newItems;
      if (quantity <= 0) {
        newItems = cart.items.filter(item => item.product_id !== productId).map(item => ({ product_id: item.product_id, quantity: item.quantity }));
      } else {
        newItems = cart.items.map(item =>
          item.product_id === productId
            ? { product_id: item.product_id, quantity }
            : { product_id: item.product_id, quantity: item.quantity }
        );
      }

      await api.post('/cart', { items: newItems });
      await fetchCart();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Failed to update cart' };
    }
  };

  const removeFromCart = async (productId) => {
    return await updateQuantity(productId, 0);
  };

  const clearCart = async () => {
    try {
      await api.delete('/cart');
      setCart({ items: [] });
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Failed to clear cart' };
    }
  };

  const cartCount = cart.items?.reduce((sum, item) => sum + item.quantity, 0) || 0;
  const cartTotal = cart.items?.reduce((sum, item) => sum + (item.product?.price || 0) * item.quantity, 0) || 0;

  return (
    <CartContext.Provider value={{ cart, loading, cartCount, cartTotal, fetchCart, addToCart, updateQuantity, removeFromCart, clearCart }}>
      {children}
    </CartContext.Provider>
  );
};
