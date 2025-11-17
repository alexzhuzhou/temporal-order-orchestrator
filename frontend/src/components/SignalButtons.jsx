import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { orderAPI } from '../services/api';

export default function SignalButtons({ orderId, orderState, cancelled }) {
  const queryClient = useQueryClient();
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [address, setAddress] = useState({
    street: '',
    city: '',
    state: '',
    zip_code: '',
    country: 'USA'
  });

  const approveMutation = useMutation({
    mutationFn: () => orderAPI.approveOrder(orderId),
    onSuccess: () => {
      queryClient.invalidateQueries(['orderStatus', orderId]);
    },
  });

  const cancelMutation = useMutation({
    mutationFn: () => orderAPI.cancelOrder(orderId),
    onSuccess: () => {
      queryClient.invalidateQueries(['orderStatus', orderId]);
    },
  });

  const updateAddressMutation = useMutation({
    mutationFn: (address) => orderAPI.updateAddress(orderId, address),
    onSuccess: () => {
      queryClient.invalidateQueries(['orderStatus', orderId]);
      setShowAddressForm(false);
    },
  });

  const handleAddressSubmit = (e) => {
    e.preventDefault();
    updateAddressMutation.mutate(address);
  };

  // Determine which buttons to show based on state
  const canApprove = orderState === 'AWAITING_MANUAL_APPROVAL' && !cancelled;
  const canCancel = !cancelled && !['COMPLETED', 'CHARGING_PAYMENT', 'SHIPPING', 'MARKING_SHIPPED'].includes(orderState);
  const canUpdateAddress = !cancelled && !['SHIPPING', 'MARKING_SHIPPED', 'COMPLETED'].includes(orderState);

  if (cancelled || orderState === 'COMPLETED') {
    return (
      <div className="bg-gray-50 rounded-lg p-6 text-center">
        <p className="text-gray-600">
          {cancelled ? '❌ Order was cancelled' : '✅ Order completed successfully'}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Actions</h3>

      {/* Approve Button */}
      {canApprove && (
        <button
          onClick={() => approveMutation.mutate()}
          disabled={approveMutation.isPending}
          className="w-full bg-green-600 text-white py-3 px-6 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition font-medium flex items-center justify-center gap-2"
        >
          {approveMutation.isPending ? (
            <>
              <span className="animate-spin">⏳</span>
              Approving...
            </>
          ) : (
            <>
              ✅ Approve Order
            </>
          )}
        </button>
      )}

      {approveMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3">
          <p className="text-sm text-red-800">
            Error: {approveMutation.error.response?.data?.detail || approveMutation.error.message}
          </p>
        </div>
      )}

      {/* Cancel Button */}
      {canCancel && (
        <button
          onClick={() => {
            if (window.confirm('Are you sure you want to cancel this order?')) {
              cancelMutation.mutate();
            }
          }}
          disabled={cancelMutation.isPending}
          className="w-full bg-red-600 text-white py-3 px-6 rounded-md hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition font-medium flex items-center justify-center gap-2"
        >
          {cancelMutation.isPending ? (
            <>
              <span className="animate-spin">⏳</span>
              Cancelling...
            </>
          ) : (
            <>
              ❌ Cancel Order
            </>
          )}
        </button>
      )}

      {cancelMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3">
          <p className="text-sm text-red-800">
            Error: {cancelMutation.error.response?.data?.detail || cancelMutation.error.message}
          </p>
        </div>
      )}

      {/* Update Address Button */}
      {canUpdateAddress && (
        <div>
          <button
            onClick={() => setShowAddressForm(!showAddressForm)}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 transition font-medium flex items-center justify-center gap-2"
          >
            📍 Update Shipping Address
          </button>

          {showAddressForm && (
            <form onSubmit={handleAddressSubmit} className="mt-4 space-y-3 bg-blue-50 p-4 rounded-md">
              <input
                type="text"
                placeholder="Street Address"
                value={address.street}
                onChange={(e) => setAddress({ ...address, street: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                required
              />
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="text"
                  placeholder="City"
                  value={address.city}
                  onChange={(e) => setAddress({ ...address, city: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-md"
                  required
                />
                <input
                  type="text"
                  placeholder="State"
                  value={address.state}
                  onChange={(e) => setAddress({ ...address, state: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-md"
                  required
                />
              </div>
              <input
                type="text"
                placeholder="ZIP Code"
                value={address.zip_code}
                onChange={(e) => setAddress({ ...address, zip_code: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                required
              />
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={updateAddressMutation.isPending}
                  className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400"
                >
                  {updateAddressMutation.isPending ? 'Updating...' : 'Submit'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddressForm(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {updateAddressMutation.isError && (
            <div className="mt-2 bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-sm text-red-800">
                Error: {updateAddressMutation.error.response?.data?.detail || updateAddressMutation.error.message}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Info message */}
      {!canApprove && !canCancel && !canUpdateAddress && orderState !== 'COMPLETED' && (
        <div className="bg-gray-50 rounded-md p-4 text-center">
          <p className="text-gray-600 text-sm">
            Order is {orderState.toLowerCase().replace('_', ' ')}...
          </p>
        </div>
      )}
    </div>
  );
}
