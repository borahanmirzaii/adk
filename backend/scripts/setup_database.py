"""Setup database schema"""

import subprocess
import sys
from pathlib import Path


def setup_database():
    """Run Supabase migrations"""
    supabase_dir = Path(__file__).parent.parent.parent / "infrastructure" / "supabase"

    if not supabase_dir.exists():
        print("❌ Supabase directory not found. Run 'supabase init' first.")
        sys.exit(1)

    # Run migrations
    result = subprocess.run(
        ["supabase", "db", "push"],
        cwd=supabase_dir,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"❌ Database setup failed: {result.stderr}")
        sys.exit(1)

    print("✅ Database setup complete")


if __name__ == "__main__":
    setup_database()

