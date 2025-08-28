# moto-testkit

**moto-testkit** is an enhanced testing toolkit built on top of [moto](https://github.com/getmoto/moto), providing:
- Easy setup for **unit tests** (Pytest + Unittest).
- Support for **sync and async workflows**.
- Ready-to-use **helpers** for AWS services.
- A full **examples/** directory with practical test cases.

---

## 🚀 Benefits over `moto`
- ✅ Simplified setup for both sync & async tests.
- ✅ Preconfigured decorators and fixtures for Pytest & Unittest.
- ✅ Rich **examples** for DynamoDB, S3, and other AWS services.
- ✅ Helpers for repetitive patterns (table creation, sessions, contexts).

---

## 📂 Examples
Check the [examples/](examples) folder for:
- **Pytest usage** with async/sync.
- **Unittest usage** with decorators.
- **Service-specific helpers**.

```python
import unittest
from moto_testkit import use_moto_testkit

@use_moto_testkit(auto_start=True)
class TestDynamoDB(unittest.TestCase):
    def setUp(self):
        self.repo.create_table(
            table_name="Users",
            key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
            attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}]
        )

    def test_insert_user(self):
        self.repo.put_item(table_name="Users", item={"id": "123", "name": "Alice"})
        result = self.repo.get_item(table_name="Users", key={"id": "123"})
        assert result["Item"]["name"] == "Alice"

