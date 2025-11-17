const WORKFLOW_STATES = [
  { key: 'RECEIVING', label: 'Receiving', icon: '📥', color: 'blue' },
  { key: 'VALIDATING', label: 'Validating', icon: '✓', color: 'blue' },
  { key: 'AWAITING_MANUAL_APPROVAL', label: 'Manual Approval', icon: '⏸️', color: 'yellow' },
  { key: 'CHARGING_PAYMENT', label: 'Charging Payment', icon: '💳', color: 'blue' },
  { key: 'SHIPPING', label: 'Shipping', icon: '📦', color: 'blue' },
  { key: 'MARKING_SHIPPED', label: 'Marking Shipped', icon: '✓', color: 'blue' },
  { key: 'COMPLETED', label: 'Completed', icon: '✅', color: 'green' },
  { key: 'CANCELLED', label: 'Cancelled', icon: '❌', color: 'red' },
];

export default function OrderTimeline({ currentState, cancelled }) {
  const displayState = cancelled ? 'CANCELLED' : currentState;
  const currentIndex = WORKFLOW_STATES.findIndex(s => s.key === displayState);

  const getStateStatus = (index) => {
    if (cancelled && WORKFLOW_STATES[index].key === 'CANCELLED') return 'current';
    if (cancelled) return 'inactive';
    if (index < currentIndex) return 'completed';
    if (index === currentIndex) return 'current';
    return 'pending';
  };

  const getColorClasses = (status, color) => {
    if (status === 'completed') return 'bg-green-500 text-white';
    if (status === 'current') {
      if (color === 'yellow') return 'bg-yellow-500 text-white animate-pulse';
      if (color === 'red') return 'bg-red-500 text-white';
      if (color === 'green') return 'bg-green-500 text-white';
      return 'bg-blue-500 text-white animate-pulse';
    }
    return 'bg-gray-200 text-gray-500';
  };

  const getLineColor = (status) => {
    if (status === 'completed') return 'bg-green-500';
    if (status === 'current') return 'bg-blue-500';
    return 'bg-gray-300';
  };

  // Filter out CANCELLED from timeline unless it's the current state
  const visibleStates = WORKFLOW_STATES.filter(s =>
    s.key !== 'CANCELLED' || cancelled
  );

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-6 text-gray-800">Workflow Progress</h3>

      <div className="space-y-4">
        {visibleStates.map((state, index) => {
          const status = getStateStatus(WORKFLOW_STATES.findIndex(s => s.key === state.key));

          return (
            <div key={state.key} className="relative">
              <div className="flex items-center gap-4">
                {/* Icon Circle */}
                <div className={`
                  w-12 h-12 rounded-full flex items-center justify-center
                  text-xl font-semibold transition-all duration-300
                  ${getColorClasses(status, state.color)}
                `}>
                  {state.icon}
                </div>

                {/* Label */}
                <div className="flex-1">
                  <p className={`
                    font-medium
                    ${status === 'current' ? 'text-gray-900 text-lg' : ''}
                    ${status === 'completed' ? 'text-gray-700' : ''}
                    ${status === 'pending' ? 'text-gray-400' : ''}
                  `}>
                    {state.label}
                  </p>
                  {status === 'current' && state.key === 'AWAITING_MANUAL_APPROVAL' && (
                    <p className="text-sm text-yellow-600 font-medium mt-1">
                      ⏳ Waiting for manual approval...
                    </p>
                  )}
                  {status === 'current' && state.key !== 'AWAITING_MANUAL_APPROVAL' && state.key !== 'COMPLETED' && state.key !== 'CANCELLED' && (
                    <p className="text-sm text-blue-600 font-medium mt-1">
                      In progress...
                    </p>
                  )}
                </div>

                {/* Status Badge */}
                <div>
                  {status === 'completed' && (
                    <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                      Done
                    </span>
                  )}
                  {status === 'current' && (
                    <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                      Active
                    </span>
                  )}
                </div>
              </div>

              {/* Connecting Line */}
              {index < visibleStates.length - 1 && (
                <div className="ml-6 h-8 w-0.5 transition-all duration-300"
                     style={{ backgroundColor: status === 'completed' ? '#10b981' : '#d1d5db' }}>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
