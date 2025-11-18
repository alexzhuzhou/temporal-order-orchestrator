import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Customer API
export const customerAPI = {
  // Create a new customer
  createCustomer: async (customerData) => {
    const response = await api.post('/customers', customerData);
    return response.data;
  },

  // Get all customers
  getCustomers: async () => {
    const response = await api.get('/customers');
    return response.data;
  },

  // Get customer by ID
  getCustomer: async (customerId) => {
    const response = await api.get(`/customers/${customerId}`);
    return response.data;
  },
};

// Order API
export const orderAPI = {
  // Start a new order
  startOrder: async (orderId, orderData) => {
    const response = await api.post(`/orders/${orderId}/start`, orderData);
    return response.data;
  },

  // List/search orders
  listOrders: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.customer_id) params.append('customer_id', filters.customer_id);
    if (filters.customer_name) params.append('customer_name', filters.customer_name);
    if (filters.priority) params.append('priority', filters.priority);
    if (filters.min_total) params.append('min_total', filters.min_total);
    if (filters.max_total) params.append('max_total', filters.max_total);
    if (filters.limit) params.append('limit', filters.limit);

    const response = await api.get(`/orders?${params.toString()}`);
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

export const generateCustomerId = () => {
  return `cust-${Math.random().toString(36).substring(2, 10)}`;
};

export default api;
