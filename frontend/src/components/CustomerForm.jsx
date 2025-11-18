import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { customerAPI } from '../services/api';

export default function CustomerForm({ onCustomerCreated }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');

  const createCustomerMutation = useMutation({
    mutationFn: () => customerAPI.createCustomer({ name, email, phone }),
    onSuccess: (data) => {
      // Reset form
      setName('');
      setEmail('');
      setPhone('');

      // Call callback if provided
      if (onCustomerCreated) {
        onCustomerCreated(data);
      }
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    createCustomerMutation.mutate();
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold mb-4 text-gray-800">Create New Customer</h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Customer Name *
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="John Doe"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email *
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="john@example.com"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Phone (optional)
          </label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="555-0123"
          />
        </div>

        {createCustomerMutation.isSuccess && (
          <div className="bg-green-50 border border-green-200 rounded-md p-3">
            <p className="text-sm text-green-800">
              ✓ Customer created successfully!
              <br />
              <span className="font-medium">
                ID: {createCustomerMutation.data.id}
              </span>
            </p>
          </div>
        )}

        {createCustomerMutation.isError && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <p className="text-sm text-red-800">
              ❌ Error: {createCustomerMutation.error.message}
            </p>
          </div>
        )}

        <button
          type="submit"
          disabled={createCustomerMutation.isPending}
          className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition font-medium"
        >
          {createCustomerMutation.isPending ? (
            <span className="flex items-center justify-center gap-2">
              <span className="animate-spin">⏳</span>
              Creating...
            </span>
          ) : (
            '👤 Create Customer'
          )}
        </button>
      </form>
    </div>
  );
}
