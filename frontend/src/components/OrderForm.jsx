import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { orderAPI, generateOrderId, generatePaymentId } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function OrderForm() {
  const navigate = useNavigate();
  const [orderId, setOrderId] = useState(generateOrderId());
  const [paymentId, setPaymentId] = useState(generatePaymentId());

  const startOrderMutation = useMutation({
    mutationFn: () => orderAPI.startOrder(orderId, paymentId),
    onSuccess: () => {
      navigate(`/orders/${orderId}`);
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    startOrderMutation.mutate();
  };

  const regenerateIds = () => {
    setOrderId(generateOrderId());
    setPaymentId(generatePaymentId());
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Start New Order</h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Order ID
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={orderId}
                onChange={(e) => setOrderId(e.target.value)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="order-abc123"
                required
              />
              <button
                type="button"
                onClick={regenerateIds}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition"
              >
                🔄 Regenerate
              </button>
            </div>
            <p className="mt-1 text-sm text-gray-500">
              Unique identifier for this order
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Payment ID
            </label>
            <input
              type="text"
              value={paymentId}
              onChange={(e) => setPaymentId(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="payment-xyz789"
              required
            />
            <p className="mt-1 text-sm text-gray-500">
              Idempotency key for payment processing
            </p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <h3 className="font-medium text-blue-900 mb-2">What happens next?</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Order will be created and validated</li>
              <li>• Workflow will pause for <strong>manual approval</strong></li>
              <li>• You can approve, cancel, or update address</li>
              <li>• After approval, payment is charged and shipping begins</li>
            </ul>
          </div>

          {startOrderMutation.isError && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-sm text-red-800">
                ❌ Error: {startOrderMutation.error.message}
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={startOrderMutation.isPending}
            className="w-full bg-primary-600 text-white py-3 px-6 rounded-md hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition font-medium text-lg"
          >
            {startOrderMutation.isPending ? (
              <span className="flex items-center justify-center gap-2">
                <span className="animate-spin">⏳</span>
                Starting Order...
              </span>
            ) : (
              '🚀 Start Order Workflow'
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
