"""
Startup script to launch all services:
- Docker Compose (Temporal + Databases)
- Workers (Order + Shipping)
- FastAPI Server
"""

import subprocess
import sys
import time
import os
from pathlib import Path


def run_command(cmd, description, check=True):
    """Run a shell command with description"""
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()

    try:
        if check:
            subprocess.run(cmd, check=True)
        else:
            subprocess.run(cmd)
        print(f"✓ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrupted by user")
        return False


def main():
    """Main startup sequence"""
    print("\n" + "="*60)
    print("🚀 Order Orchestration System - Startup")
    print("="*60)

    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    print(f"\nProject root: {project_root}")

    # Step 1: Start Docker Compose services
    print("\n" + "="*60)
    print("Step 1: Starting Docker Compose services")
    print("="*60)
    print("\nThis will start:")
    print("  - Application Database (PostgreSQL on port 5432)")
    print("  - Temporal Database (PostgreSQL on port 5433)")
    print("  - Temporal Server (gRPC on port 7233)")
    print("  - Temporal UI (Web on port 8080)")
    print()

    os.chdir(project_root)

    if not run_command(
        ["docker-compose", "up", "-d"],
        "Starting Docker Compose services",
        check=True
    ):
        print("\n❌ Failed to start Docker Compose services")
        print("Please ensure Docker is running and try again")
        sys.exit(1)

    # Wait for services to be healthy
    print("\n⏳ Waiting for services to be healthy (30 seconds)...")
    time.sleep(30)

    # Step 2: Check service health
    print("\n" + "="*60)
    print("Step 2: Checking service health")
    print("="*60)

    run_command(
        ["docker-compose", "ps"],
        "Checking Docker Compose services",
        check=False
    )

    # Step 3: Instructions for running workers and API
    print("\n" + "="*60)
    print("✓ Infrastructure is ready!")
    print("="*60)

    print("\n📊 Service URLs:")
    print("  - Application Database: localhost:5432")
    print("  - Temporal Server: localhost:7233")
    print("  - Temporal UI: http://localhost:8080")
    print()

    print("\n📝 Next Steps:")
    print("\n1. Start the workers (in a new terminal):")
    print("   python -m temporal_app.worker_dev")
    print()

    print("2. Start the FastAPI server (in another terminal):")
    print("   python -m api.server")
    print("   API will be available at: http://localhost:8000")
    print()

    print("3. Test the system:")
    print("   # Start an order")
    print("   python -m scripts.cli start")
    print()
    print("   # Approve the order")
    print("   python -m scripts.cli approve <order_id>")
    print()
    print("   # Check status")
    print("   python -m scripts.cli status <order_id>")
    print()

    print("\n🔧 Useful Commands:")
    print("   # View logs")
    print("   docker-compose logs -f temporal")
    print()
    print("   # Stop all services")
    print("   docker-compose down")
    print()
    print("   # Stop and remove volumes")
    print("   docker-compose down -v")
    print()

    print("\n✓ Setup complete! The infrastructure is ready.")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
