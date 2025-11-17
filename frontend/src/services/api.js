import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Order API
export const orderAPI = {
  // Start a new order
  startOrder: async (orderId, paymentId = null) => {
    const response = await api.post(`/orders/${orderId}/start`, {
      payment_id: paymentId,
    });
    return response.data;
  },

  // Get order status
  getStatus: async (orderId) => {
    const response = await api.get(`/orders/${orderId}/status`);
    return response.data;
  },

  // Get order result
  getResult: async (orderId) => {
    const response = await api.get(`/orders/${orderId}/result`);
    return response.data;
  },

  // Send approve signal
  approveOrder: async (orderId) => {
    const response = await api.post(`/orders/${orderId}/signals/approve`);
    return response.data;
  },

  // Send cancel signal
  cancelOrder: async (orderId) => {
    const response = await api.post(`/orders/${orderId}/signals/cancel`);
    return response.data;
  },

  // Send update address signal
  updateAddress: async (orderId, address) => {
    const response = await api.post(`/orders/${orderId}/signals/update-address`, address);
    return response.data;
  },
};

// Helper to generate unique IDs
export const generateOrderId = () => {
  return `order-${Math.random().toString(36).substring(2, 10)}`;
};

export const generatePaymentId = () => {
  return `payment-${Math.random().toString(36).substring(2, 10)}`;
};

export default api;
