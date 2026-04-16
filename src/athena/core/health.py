from typing import Any

from athena.memory.vectors import get_client, get_embedding


class HealthCheck:
    """Core health monitoring for Athena services."""

    @staticmethod
    def check_vector_api() -> dict[str, Any]:
        """Check if the Gemini Embedding API is responsive and returns correct dimensions."""
        try:
            test_text = "health check"
            embedding = get_embedding(test_text)
            dims = len(embedding)
            if dims == 3072:
                return {"status": "PASS", "dims": 3072, "model": "gemini-embedding-001"}
            else:
                return {
                    "status": "FAIL",
                    "error": f"Incorrect dimensions: {dims} (expected 3072)",
                }
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    @staticmethod
    def check_database() -> dict[str, Any]:
        """Check Supabase connectivity and RPC health."""
        try:
            client = get_client()
            # Test a lightweight RPC or query
            # Checking sessions table count as a proxy for connectivity
            response = (
                client.table("sessions")
                .select("count", count="exact")
                .limit(1)
                .execute()
            )
            count = response.count if hasattr(response, "count") else 0
            return {"status": "PASS", "record_count": count}
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    @classmethod
    def run_all(cls) -> bool:
        """Run all critical health checks and print results."""
        print("\n🔍 SYSTEM HEALTH AUDIT")
        print("─" * 30)

        vector = cls.check_vector_api()
        v_status = (
            f"✅ {vector['model']} ({vector['dims']}d)"
            if vector["status"] == "PASS"
            else f"❌ {vector.get('error')}"
        )
        print(f"   Vectors:  {v_status}")

        db = cls.check_database()
        db_status = (
            f"✅ Connected ({db['record_count']} records)"
            if db["status"] == "PASS"
            else f"❌ {db.get('error')}"
        )
        print(f"   Database: {db_status}")

        print("─" * 30)
        return vector["status"] == "PASS" and db["status"] == "PASS"


if __name__ == "__main__":
    # Internal test
    HealthCheck.run_all()
