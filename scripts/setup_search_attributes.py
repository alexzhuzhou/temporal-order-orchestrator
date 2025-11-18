"""
Register custom search attributes with Temporal

This script must be run once to register the search attributes used by workflows.
Search attributes enable querying and filtering workflows by custom fields.
"""

import asyncio
from temporalio.client import Client
from temporalio.service import OperatorServiceStubs

from temporal_app.config import TEMPORAL_HOST


async def setup_search_attributes():
    """Register custom search attributes with Temporal"""
    print(f"Connecting to Temporal at {TEMPORAL_HOST}...")
    client = await Client.connect(TEMPORAL_HOST)

    # Get operator service for administrative operations
    operator = client.operator_service()

    print("\nRegistering custom search attributes...")

    search_attributes = {
        "CustomerId": "Keyword",  # Exact match queries
        "CustomerName": "Text",  # Full-text search
        "OrderTotal": "Double",  # Numeric range queries
        "Priority": "Keyword",  # Exact match queries (NORMAL, HIGH, URGENT)
    }

    for name, type_name in search_attributes.items():
        try:
            print(f"  - {name} ({type_name})...", end=" ")

            # Note: In Temporal, we need to use the operator service to add search attributes
            # This is typically done via tctl command line:
            # tctl admin cluster add-search-attributes --name CustomerId --type Keyword

            # For programmatic access, we'll use the add_search_attributes method
            from temporalio.api.operatorservice.v1 import AddSearchAttributesRequest
            from temporalio.api.enums.v1 import IndexedValueType

            type_map = {
                "Keyword": IndexedValueType.INDEXED_VALUE_TYPE_KEYWORD,
                "Text": IndexedValueType.INDEXED_VALUE_TYPE_TEXT,
                "Double": IndexedValueType.INDEXED_VALUE_TYPE_DOUBLE,
                "Int": IndexedValueType.INDEXED_VALUE_TYPE_INT,
                "Bool": IndexedValueType.INDEXED_VALUE_TYPE_BOOL,
                "Datetime": IndexedValueType.INDEXED_VALUE_TYPE_DATETIME,
            }

            request = AddSearchAttributesRequest(
                search_attributes={name: type_map[type_name]},
                namespace="default",
            )

            await operator.add_search_attributes(request)
            print("✓")

        except Exception as e:
            # Attribute might already exist
            if "already exists" in str(e).lower():
                print("(already exists)")
            else:
                print(f"✗ Error: {e}")

    print("\n✓ Search attributes setup complete!")
    print("\nRegistered attributes:")
    print("  - CustomerId (Keyword): Query by exact customer ID")
    print("  - CustomerName (Text): Search by customer name")
    print("  - OrderTotal (Double): Filter by order amount")
    print("  - Priority (Keyword): Filter by priority level")

    print("\nExample queries:")
    print('  CustomerId = "cust-12345"')
    print('  CustomerName = "John Doe"')
    print('  OrderTotal >= 100.0 AND OrderTotal <= 500.0')
    print('  Priority = "HIGH"')
    print('  CustomerId = "cust-12345" AND Priority = "URGENT"')


if __name__ == "__main__":
    print("=" * 60)
    print("Temporal Search Attributes Setup")
    print("=" * 60)

    try:
        asyncio.run(setup_search_attributes())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: Search attributes can also be registered using tctl:")
        print("  docker exec temporal tctl admin cluster add-search-attributes \\")
        print('    --name CustomerId --type Keyword')
        print("  docker exec temporal tctl admin cluster add-search-attributes \\")
        print('    --name CustomerName --type Text')
        print("  docker exec temporal tctl admin cluster add-search-attributes \\")
        print('    --name OrderTotal --type Double')
        print("  docker exec temporal tctl admin cluster add-search-attributes \\")
        print('    --name Priority --type Keyword')
        import traceback
        traceback.print_exc()
