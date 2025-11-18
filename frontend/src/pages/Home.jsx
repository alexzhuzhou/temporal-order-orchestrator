import OrderForm from '../components/OrderForm';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Order Orchestrator Dashboard
          </h1>
          <p className="text-xl text-gray-600 mb-6">
            Temporal Workflow Orchestration for E-Commerce Orders
          </p>
          <div className="flex justify-center gap-4 flex-wrap">
            <Link
              to="/orders"
              className="inline-flex items-center gap-2 px-6 py-3 bg-white text-primary-600 rounded-lg shadow hover:shadow-lg transition font-medium"
            >
              📋 View All Orders
            </Link>
            <Link
              to="/docs"
              className="inline-flex items-center gap-2 px-6 py-3 bg-white text-green-600 rounded-lg shadow hover:shadow-lg transition font-medium"
            >
              📚 Documentation
            </Link>
            <a
              href="http://localhost:8080"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 bg-white text-purple-600 rounded-lg shadow hover:shadow-lg transition font-medium"
            >
              ⚡ Temporal UI
            </a>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl mb-3">⏸️</div>
            <h3 className="font-semibold text-lg mb-2">Manual Approval</h3>
            <p className="text-gray-600 text-sm">
              Workflows pause for human review before payment processing
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl mb-3">🔄</div>
            <h3 className="font-semibold text-lg mb-2">Auto Retry</h3>
            <p className="text-gray-600 text-sm">
              Failed shipping automatically retries up to 3 times
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl mb-3">📡</div>
            <h3 className="font-semibold text-lg mb-2">Real-Time Signals</h3>
            <p className="text-gray-600 text-sm">
              Send signals to running workflows: approve, cancel, update address
            </p>
          </div>
        </div>

        {/* Order Form */}
        <OrderForm />

        {/* Footer Info */}
        <div className="mt-12 text-center text-gray-600 text-sm">
          <p>Powered by Temporal Workflow Engine + FastAPI + React</p>
          <p className="mt-2">
            Task Queues: <span className="font-mono bg-white px-2 py-1 rounded">order-tq</span> |
            <span className="font-mono bg-white px-2 py-1 rounded ml-2">shipping-tq</span>
          </p>
        </div>
      </div>
    </div>
  );
}
