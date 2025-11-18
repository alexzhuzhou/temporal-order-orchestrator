import { Link } from 'react-router-dom';

export default function Documentation() {
  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <Link
          to="/"
          className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-6"
        >
          ← Back to Home
        </Link>

        <div className="bg-white rounded-lg shadow-md p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">📚 Platform Documentation</h1>
          <p className="text-gray-600 mb-8">
            Learn how to use the Temporal Order Orchestrator to manage customer orders with workflow orchestration
          </p>

          {/* Table of Contents */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-blue-900 mb-4">📋 Table of Contents</h2>
            <ul className="space-y-2 text-blue-800">
              <li><a href="#overview" className="hover:underline">1. Overview</a></li>
              <li><a href="#getting-started" className="hover:underline">2. Getting Started</a></li>
              <li><a href="#creating-customers" className="hover:underline">3. Creating Customers</a></li>
              <li><a href="#starting-orders" className="hover:underline">4. Starting Orders</a></li>
              <li><a href="#workflow-lifecycle" className="hover:underline">5. Workflow Lifecycle</a></li>
              <li><a href="#managing-orders" className="hover:underline">6. Managing Orders</a></li>
              <li><a href="#search-filter" className="hover:underline">7. Search & Filter</a></li>
              <li><a href="#signals" className="hover:underline">8. Workflow Signals</a></li>
              <li><a href="#troubleshooting" className="hover:underline">9. Troubleshooting</a></li>
            </ul>
          </div>

          {/* Overview */}
          <section id="overview" className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Overview</h2>
            <p className="text-gray-700 mb-4">
              The Temporal Order Orchestrator is a production-ready system that demonstrates resilient workflow
              orchestration for e-commerce order processing. Built with Temporal, it showcases:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li><strong>Workflow Orchestration:</strong> Long-running order processes with state persistence</li>
              <li><strong>Signals:</strong> External commands to control running workflows (approve, cancel, update)</li>
              <li><strong>Manual Review:</strong> Human-in-the-loop approval before payment</li>
              <li><strong>Retry Logic:</strong> Automatic retries for failed operations</li>
              <li><strong>Search Attributes:</strong> Advanced querying and filtering of workflows</li>
              <li><strong>Separate Task Queues:</strong> Isolated processing for different workflow types</li>
            </ul>
          </section>

          {/* Getting Started */}
          <section id="getting-started" className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Getting Started</h2>
            <div className="bg-gray-50 rounded-lg p-6 mb-4">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Quick Start Steps</h3>
              <ol className="list-decimal list-inside space-y-2 text-gray-700">
                <li>Create a customer (or use existing ones)</li>
                <li>Start a new order workflow</li>
                <li>Approve the order for processing</li>
                <li>Monitor workflow progress in real-time</li>
                <li>Search and filter your orders</li>
              </ol>
            </div>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm text-yellow-800">
                <strong>💡 Tip:</strong> Orders require manual approval before payment processing.
                You have 30 seconds to approve before the workflow times out.
              </p>
            </div>
          </section>

          {/* Creating Customers */}
          <section id="creating-customers" className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">3. Creating Customers</h2>
            <p className="text-gray-700 mb-4">
              Before creating orders, you need at least one customer in the system.
            </p>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-4">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">How to Create a Customer</h3>
              <ol className="list-decimal list-inside space-y-2 text-blue-800">
                <li>Navigate to the <Link to="/orders" className="font-semibold underline">Orders page</Link></li>
                <li>Click the <strong>"👤 New Customer"</strong> button (top right)</li>
                <li>Fill in the customer details:
                  <ul className="list-disc list-inside ml-6 mt-2 space-y-1">
                    <li><strong>Name:</strong> Customer's full name (required)</li>
                    <li><strong>Email:</strong> Valid email address (required, must be unique)</li>
                    <li><strong>Phone:</strong> Contact number (optional)</li>
                  </ul>
                </li>
                <li>Click <strong>"👤 Create Customer"</strong></li>
                <li>You'll see a success message with the customer ID</li>
              </ol>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm text-green-800">
                <strong>✓ Customer Created:</strong> The customer will immediately appear in order creation forms
                and search filters.
              </p>
            </div>
          </section>

          {/* Starting Orders */}
          <section id="starting-orders" className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Starting Orders</h2>
            <p className="text-gray-700 mb-4">
              Create a new order workflow with customer information and order details.
            </p>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-4">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">Steps to Start an Order</h3>
              <ol className="list-decimal list-inside space-y-2 text-blue-800">
                <li>Go to the <Link to="/" className="font-semibold underline">Home page</Link></li>
                <li>Fill in the order form:
                  <ul className="list-disc list-inside ml-6 mt-2 space-y-1">
                    <li><strong>Customer:</strong> Select from dropdown (required)</li>
                    <li><strong>Order Total:</strong> Dollar amount (default: $100.00)</li>
                    <li><strong>Priority:</strong> NORMAL, HIGH, or URGENT</li>
                    <li><strong>Order ID:</strong> Auto-generated, or enter custom</li>
                    <li><strong>Payment ID:</strong> Auto-generated idempotency key</li>
                  </ul>
                </li>
                <li>Click <strong>"🚀 Start Order Workflow"</strong></li>
                <li>You'll be redirected to the order detail page</li>
              </ol>
            </div>

            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-semibold text-gray-800 mb-2">Priority Levels</h4>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li><strong>🟢 NORMAL:</strong> Standard processing (default)</li>
                  <li><strong>🟡 HIGH:</strong> Elevated priority, faster handling</li>
                  <li><strong>🔴 URGENT:</strong> Critical orders, immediate attention</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Workflow Lifecycle */}
          <section id="workflow-lifecycle" className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Workflow Lifecycle</h2>
            <p className="text-gray-700 mb-4">
              Every order goes through a series of states from creation to completion:
            </p>

            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mb-4">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold">1</div>
                  <div>
                    <strong className="text-gray-900">RECEIVING</strong>
                    <p className="text-sm text-gray-600">Order is created in the database</p>
                  </div>
                </div>
                <div className="ml-4 border-l-2 border-blue-300 h-4"></div>

                <div className="flex items-center gap-3">
                  <div className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold">2</div>
                  <div>
                    <strong className="text-gray-900">VALIDATING</strong>
                    <p className="text-sm text-gray-600">Order details are validated</p>
                  </div>
                </div>
                <div className="ml-4 border-l-2 border-blue-300 h-4"></div>

                <div className="flex items-center gap-3">
                  <div className="bg-yellow-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold">3</div>
                  <div>
                    <strong className="text-gray-900">AWAITING_MANUAL_APPROVAL</strong>
                    <p className="text-sm text-gray-600">⏰ Waiting for human approval (30s timeout)</p>
                  </div>
                </div>
                <div className="ml-4 border-l-2 border-yellow-300 h-4"></div>

                <div className="flex items-center gap-3">
                  <div className="bg-green-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold">4</div>
                  <div>
                    <strong className="text-gray-900">CHARGING_PAYMENT</strong>
                    <p className="text-sm text-gray-600">Payment is processed (idempotent)</p>
                  </div>
                </div>
                <div className="ml-4 border-l-2 border-green-300 h-4"></div>

                <div className="flex items-center gap-3">
                  <div className="bg-purple-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold">5</div>
                  <div>
                    <strong className="text-gray-900">SHIPPING</strong>
                    <p className="text-sm text-gray-600">Package prepared and dispatched (with retries)</p>
                  </div>
                </div>
                <div className="ml-4 border-l-2 border-purple-300 h-4"></div>

                <div className="flex items-center gap-3">
                  <div className="bg-green-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold">✓</div>
                  <div>
                    <strong className="text-gray-900">COMPLETED</strong>
                    <p className="text-sm text-gray-600">Order successfully fulfilled</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-800">
                <strong>⚠️ Important:</strong> Orders can be cancelled before payment is charged.
                After payment, cancellation is no longer possible.
              </p>
            </div>
          </section>

          {/* Managing Orders */}
          <section id="managing-orders" className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Managing Orders</h2>
            <p className="text-gray-700 mb-4">
              View and interact with your orders through the order detail page.
            </p>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-4">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">Order Detail Page</h3>
              <p className="text-blue-800 mb-3">
                Access by clicking any order ID from the Orders page, or after creating an order.
              </p>
              <ul className="list-disc list-inside space-y-2 text-blue-800">
                <li><strong>Status Section:</strong> Current workflow state and details</li>
                <li><strong>Timeline:</strong> Visual progress through workflow stages</li>
                <li><strong>Signal Buttons:</strong> Actions you can take (approve, cancel, update address)</li>
                <li><strong>Real-time Updates:</strong> Auto-refreshes every 3 seconds</li>
              </ul>
            </div>
          </section>

          {/* Search & Filter */}
          <section id="search-filter" className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Search & Filter Orders</h2>
            <p className="text-gray-700 mb-4">
              Use advanced search attributes to find specific orders quickly.
            </p>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-4">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">Available Filters</h3>
              <div className="space-y-3 text-blue-800">
                <div>
                  <strong>Customer (Dropdown):</strong>
                  <p className="text-sm">Filter by exact customer ID - shows only orders for selected customer</p>
                </div>
                <div>
                  <strong>Customer Name Search:</strong>
                  <p className="text-sm">Text search - finds customers by name (e.g., "John" matches "John Doe")</p>
                </div>
                <div>
                  <strong>Priority:</strong>
                  <p className="text-sm">Filter by NORMAL, HIGH, or URGENT orders</p>
                </div>
                <div>
                  <strong>Order Total Range:</strong>
                  <p className="text-sm">Filter by minimum and/or maximum dollar amounts</p>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Example Searches</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li><strong>High-value orders:</strong> Min Total: $500</li>
                <li><strong>Urgent orders:</strong> Priority: URGENT</li>
                <li><strong>Customer's orders:</strong> Select customer from dropdown</li>
                <li><strong>Orders in range:</strong> Min: $100, Max: $500</li>
                <li><strong>Combined:</strong> Priority: URGENT + Min Total: $1000</li>
              </ul>
            </div>
          </section>

          {/* Signals */}
          <section id="signals" className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Workflow Signals</h2>
            <p className="text-gray-700 mb-4">
              Signals allow you to send commands to running workflows. Available on the order detail page.
            </p>

            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-green-900 mb-2">✅ Approve Order</h3>
                <p className="text-sm text-green-800 mb-2">
                  <strong>When:</strong> After order validation, during AWAITING_MANUAL_APPROVAL
                </p>
                <p className="text-sm text-green-800 mb-2">
                  <strong>Effect:</strong> Allows workflow to proceed to payment and shipping
                </p>
                <p className="text-sm text-green-800">
                  <strong>Timeout:</strong> Must approve within 30 seconds or workflow fails
                </p>
              </div>

              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-red-900 mb-2">❌ Cancel Order</h3>
                <p className="text-sm text-red-800 mb-2">
                  <strong>When:</strong> Before payment is charged
                </p>
                <p className="text-sm text-red-800 mb-2">
                  <strong>Effect:</strong> Immediately stops the workflow gracefully
                </p>
                <p className="text-sm text-red-800">
                  <strong>Cannot cancel:</strong> After payment charging has started
                </p>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-blue-900 mb-2">📍 Update Address</h3>
                <p className="text-sm text-blue-800 mb-2">
                  <strong>When:</strong> Before shipping starts
                </p>
                <p className="text-sm text-blue-800 mb-2">
                  <strong>Effect:</strong> Updates the shipping address for the order
                </p>
                <p className="text-sm text-blue-800">
                  <strong>Cannot update:</strong> After shipping workflow begins
                </p>
              </div>
            </div>
          </section>

          {/* Troubleshooting */}
          <section id="troubleshooting" className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Troubleshooting</h2>

            <div className="space-y-4">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="font-semibold text-yellow-900 mb-2">Workflow times out / fails</h3>
                <p className="text-sm text-yellow-800 mb-2">
                  <strong>Cause:</strong> Didn't approve within 30 seconds
                </p>
                <p className="text-sm text-yellow-800">
                  <strong>Solution:</strong> Start a new order and approve quickly, or increase timeout in backend
                </p>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="font-semibold text-yellow-900 mb-2">No customers available</h3>
                <p className="text-sm text-yellow-800 mb-2">
                  <strong>Cause:</strong> No customers created yet
                </p>
                <p className="text-sm text-yellow-800">
                  <strong>Solution:</strong> Go to Orders page → Click "👤 New Customer" → Create customer
                </p>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="font-semibold text-yellow-900 mb-2">Search returns no results</h3>
                <p className="text-sm text-yellow-800 mb-2">
                  <strong>Cause:</strong> Filters too restrictive, or no workflows match
                </p>
                <p className="text-sm text-yellow-800">
                  <strong>Solution:</strong> Click "Clear" to reset filters, or adjust filter criteria
                </p>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="font-semibold text-yellow-900 mb-2">Signal doesn't work</h3>
                <p className="text-sm text-yellow-800 mb-2">
                  <strong>Cause:</strong> Workflow not in correct state for that signal
                </p>
                <p className="text-sm text-yellow-800">
                  <strong>Solution:</strong> Check workflow state - signals only work in specific states
                </p>
              </div>
            </div>
          </section>

          {/* Additional Resources */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">📖 Additional Resources</h2>
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
              <ul className="space-y-3 text-gray-700">
                <li className="flex items-start gap-3">
                  <span className="text-2xl">🔗</span>
                  <div>
                    <strong>Temporal UI:</strong>
                    <a href="http://localhost:8080" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline ml-2">
                      http://localhost:8080
                    </a>
                    <p className="text-sm text-gray-600">View workflow history, search attributes, and execution details</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-2xl">📡</span>
                  <div>
                    <strong>API Documentation:</strong>
                    <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline ml-2">
                      http://localhost:8000/docs
                    </a>
                    <p className="text-sm text-gray-600">Interactive Swagger API documentation</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-2xl">📚</span>
                  <div>
                    <strong>Temporal Documentation:</strong>
                    <a href="https://docs.temporal.io/" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline ml-2">
                      docs.temporal.io
                    </a>
                    <p className="text-sm text-gray-600">Official Temporal workflow engine documentation</p>
                  </div>
                </li>
              </ul>
            </div>
          </section>

          {/* Quick Links */}
          <div className="bg-gray-100 rounded-lg p-6 text-center">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Navigation</h3>
            <div className="flex flex-wrap gap-3 justify-center">
              <Link
                to="/"
                className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition"
              >
                Start New Order
              </Link>
              <Link
                to="/orders"
                className="px-6 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition"
              >
                View Orders
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
