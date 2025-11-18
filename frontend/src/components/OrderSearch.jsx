import { useState } from 'react';

export default function OrderSearch({ onSearch, customers = [] }) {
  const [customerId, setCustomerId] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [priority, setPriority] = useState('');
  const [minTotal, setMinTotal] = useState('');
  const [maxTotal, setMaxTotal] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();

    const filters = {};
    if (customerId) filters.customer_id = customerId;
    if (customerName) filters.customer_name = customerName;
    if (priority) filters.priority = priority;
    if (minTotal) filters.min_total = minTotal;
    if (maxTotal) filters.max_total = maxTotal;

    onSearch(filters);
  };

  const handleClear = () => {
    setCustomerId('');
    setCustomerName('');
    setPriority('');
    setMinTotal('');
    setMaxTotal('');
    onSearch({});
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h3 className="text-lg font-bold mb-4 text-gray-800">🔍 Search & Filter Orders</h3>

      <form onSubmit={handleSearch} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Customer
            </label>
            <select
              value={customerId}
              onChange={(e) => setCustomerId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">All Customers</option>
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Customer Name Search
            </label>
            <input
              type="text"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Search by name..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">All Priorities</option>
              <option value="NORMAL">🟢 Normal</option>
              <option value="HIGH">🟡 High</option>
              <option value="URGENT">🔴 Urgent</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Order Total Range
            </label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <span className="absolute left-2 top-2 text-gray-500 text-sm">$</span>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={minTotal}
                  onChange={(e) => setMinTotal(e.target.value)}
                  className="w-full pl-6 pr-2 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Min"
                />
              </div>
              <span className="self-center text-gray-500">to</span>
              <div className="relative flex-1">
                <span className="absolute left-2 top-2 text-gray-500 text-sm">$</span>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={maxTotal}
                  onChange={(e) => setMaxTotal(e.target.value)}
                  className="w-full pl-6 pr-2 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Max"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="flex gap-2">
          <button
            type="submit"
            className="flex-1 bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 transition font-medium"
          >
            🔍 Search
          </button>
          <button
            type="button"
            onClick={handleClear}
            className="px-6 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition font-medium"
          >
            Clear
          </button>
        </div>
      </form>
    </div>
  );
}
