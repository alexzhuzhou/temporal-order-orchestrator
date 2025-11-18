import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { orderAPI } from '../services/api';
import OrderTimeline from '../components/OrderTimeline';
import SignalButtons from '../components/SignalButtons';

export default function OrderDetail() {
  const { orderId } = useParams();

  // Auto-refresh every 2 seconds
  const { data: status, isLoading, error } = useQuery({
    queryKey: ['orderStatus', orderId],
    queryFn: () => orderAPI.getStatus(orderId),
    refetchInterval: 2000, // Poll every 2 seconds
    retry: 3,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-spin">⏳</div>
          <p className="text-xl text-gray-600">Loading order status...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4">
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
            <div className="text-6xl mb-4">❌</div>
            <h2 className="text-2xl font-bold text-red-900 mb-2">Error Loading Order</h2>
            <p className="text-red-700 mb-6">
              {error.response?.data?.detail || error.message}
            </p>
            <Link
              to="/"
              className="inline-block px-6 py-3 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
            >
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex gap-4 items-center mb-4">
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
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  Order Details
                </h1>
                <p className="text-lg text-gray-600 font-mono">{orderId}</p>
              </div>
              <div className="text-right">
                {status.is_running ? (
                  <span className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-full font-medium">
                    <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
                    Running
                  </span>
                ) : status.status_details.cancelled ? (
                  <span className="px-4 py-2 bg-red-100 text-red-700 rounded-full font-medium">
                    ❌ Cancelled
                  </span>
                ) : status.workflow_state === 'COMPLETED' ? (
                  <span className="px-4 py-2 bg-green-100 text-green-700 rounded-full font-medium">
                    ✅ Completed
                  </span>
                ) : (
                  <span className="px-4 py-2 bg-gray-100 text-gray-700 rounded-full font-medium">
                    Finished
                  </span>
                )}
              </div>
            </div>

            {/* Status Details */}
            <div className="mt-6 grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Current State</p>
                <p className="text-lg font-semibold text-gray-900">
                  {status.workflow_state.replace(/_/g, ' ')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Manual Approval</p>
                <p className="text-lg font-semibold text-gray-900">
                  {status.status_details.manual_review_approved ? '✅ Approved' : '⏳ Pending'}
                </p>
              </div>
            </div>

            {status.status_details.updated_address && (
              <div className="mt-4 p-4 bg-blue-50 rounded-md">
                <p className="text-sm font-medium text-blue-900 mb-2">📍 Shipping Address</p>
                <p className="text-sm text-blue-800">
                  {status.status_details.updated_address.street}, {status.status_details.updated_address.city}, {status.status_details.updated_address.state} {status.status_details.updated_address.zip_code}
                </p>
              </div>
            )}

            {status.status_details.last_error && (
              <div className="mt-4 p-4 bg-red-50 rounded-md">
                <p className="text-sm font-medium text-red-900 mb-1">⚠️ Last Error</p>
                <p className="text-sm text-red-800 font-mono">
                  {status.status_details.last_error}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Timeline and Actions */}
        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <OrderTimeline
              currentState={status.workflow_state}
              cancelled={status.status_details.cancelled}
            />
          </div>
          <div>
            <SignalButtons
              orderId={orderId}
              orderState={status.workflow_state}
              cancelled={status.status_details.cancelled}
            />
          </div>
        </div>

        {/* Auto-refresh indicator */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>🔄 Auto-refreshing every 2 seconds</p>
        </div>
      </div>
    </div>
  );
}
