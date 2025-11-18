import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { orderAPI, customerAPI } from '../services/api';
import CustomerForm from '../components/CustomerForm';
import OrderSearch from '../components/OrderSearch';

export default function Orders() {
  const [filters, setFilters] = useState({});
  const [showCustomerForm, setShowCustomerForm] = useState(false);
  const queryClient = useQueryClient();

  // Fetch orders
  const { data: ordersData, isLoading: ordersLoading, error: ordersError } = useQuery({
    queryKey: ['orders', filters],
    queryFn: () => orderAPI.listOrders(filters),
  });

  // Fetch customers for filter dropdown
  const { data: customersData } = useQuery({
    queryKey: ['customers'],
    queryFn: () => customerAPI.getCustomers(),
  });

  const handleSearch = (newFilters) => {
    setFilters(newFilters);
  };

  const handleCustomerCreated = () => {
    // Refresh customers list
    queryClient.invalidateQueries({ queryKey: ['customers'] });
    setShowCustomerForm(false);
  };

  const getPriorityBadge = (priority) => {
    const badges = {
      NORMAL: '🟢 Normal',
      HIGH: '🟡 High',
      URGENT: '🔴 Urgent',
    };
    return badges[priority] || priority;
  };

  const getStatusBadge = (status) => {
    const badges = {
      RUNNING: '▶️ Running',
      COMPLETED: '✅ Completed',
      FAILED: '❌ Failed',
      CANCELED: '⛔ Canceled',
    };
    return badges[status] || status;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div className="flex gap-4 items-center">
            <Link
              to="/"
              className="inline-flex items-center text-primary-600 hover:text-primary-700"
            >
              ← Back to Home
            </Link>
            <Link
              to="/docs"
              className="inline-flex items-center text-green-600 hover:text-green-700 text-sm"
            >
              📚 Help
            </Link>
          </div>
          <button
            onClick={() => setShowCustomerForm(!showCustomerForm)}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition"
          >
            {showCustomerForm ? 'Hide' : '👤 New Customer'}
          </button>
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-6">📋 Orders Dashboard</h1>

        {showCustomerForm && (
          <div className="mb-6">
            <CustomerForm onCustomerCreated={handleCustomerCreated} />
          </div>
        )}

        <OrderSearch
          onSearch={handleSearch}
          customers={customersData?.customers || []}
        />

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-800">
              Workflow Results
              {ordersData && ` (${ordersData.count})`}
            </h2>
            {ordersData?.query && (
              <span className="text-sm text-gray-600">
                Query: <code className="bg-gray-100 px-2 py-1 rounded">{ordersData.query}</code>
              </span>
            )}
          </div>

          {ordersLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin text-4xl mb-4">⏳</div>
              <p className="text-gray-600">Loading workflows...</p>
            </div>
          ) : ordersError ? (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-red-800">
                ❌ Error loading orders: {ordersError.message}
              </p>
            </div>
          ) : ordersData?.workflows?.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📭</div>
              <p className="text-gray-600 mb-4">No orders found matching your filters</p>
              <Link
                to="/"
                className="inline-block px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition font-medium"
              >
                Start New Order
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Order ID
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Customer
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Priority
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Started
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {ordersData.workflows.map((workflow) => (
                    <tr key={workflow.workflow_id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 whitespace-nowrap">
                        <Link
                          to={`/orders/${workflow.workflow_id}`}
                          className="text-primary-600 hover:text-primary-700 font-medium"
                        >
                          {workflow.workflow_id}
                        </Link>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {workflow.customer_name}
                        </div>
                        <div className="text-xs text-gray-500">
                          {workflow.customer_id}
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm font-medium">
                        ${workflow.order_total.toFixed(2)}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm">
                        {getPriorityBadge(workflow.priority)}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm">
                        {getStatusBadge(workflow.status)}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-xs text-gray-500">
                        {new Date(workflow.start_time).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm">
                        <Link
                          to={`/orders/${workflow.workflow_id}`}
                          className="text-primary-600 hover:text-primary-700"
                        >
                          View →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-md p-4">
          <h3 className="font-semibold text-blue-900 mb-2">💡 Tip</h3>
          <p className="text-sm text-blue-800">
            You can also view workflows in the{' '}
            <a
              href="http://localhost:8080"
              target="_blank"
              rel="noopener noreferrer"
              className="font-semibold underline"
            >
              Temporal UI
            </a>{' '}
            where you can see search attributes and apply advanced filters.
          </p>
        </div>
      </div>
    </div>
  );
}
