import { Link } from 'react-router-dom';

export default function Orders() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <Link
          to="/"
          className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-6"
        >
          ← Back to Home
        </Link>

        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <div className="text-6xl mb-4">📋</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Orders List</h1>
          <p className="text-gray-600 mb-6">
            To view order history, you would need to query the database or add a list endpoint to the API.
          </p>

          <div className="bg-blue-50 border border-blue-200 rounded-md p-6 text-left max-w-xl mx-auto">
            <h3 className="font-semibold text-blue-900 mb-3">How to view orders:</h3>
            <ol className="text-sm text-blue-800 space-y-2 list-decimal list-inside">
              <li>Visit <a href="http://localhost:8080" target="_blank" rel="noopener noreferrer" className="font-semibold underline">Temporal UI</a> to see all workflows</li>
              <li>Or query your database directly:
                <pre className="mt-2 bg-blue-900 text-blue-50 p-2 rounded text-xs overflow-x-auto">
                  SELECT * FROM orders ORDER BY created_at DESC;
                </pre>
              </li>
              <li>Or add a <code className="bg-blue-200 px-1 rounded">GET /orders</code> endpoint to your FastAPI backend</li>
            </ol>
          </div>

          <div className="mt-8">
            <Link
              to="/"
              className="inline-block px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition font-medium"
            >
              Start New Order
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
