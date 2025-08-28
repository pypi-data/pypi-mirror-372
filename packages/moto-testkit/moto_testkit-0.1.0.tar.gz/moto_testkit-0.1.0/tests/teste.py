import unittest

from aws_testkit.src import S3ObjectModel, DynamoItemModel, SQSMessageModel
from aws_testkit.src.decorator import use_moto_testkit


@use_moto_testkit(auto_start=True, patch_aiobotocore=True)
class MyFullAsyncTest(unittest.IsolatedAsyncioTestCase):

    async def test_full_async(self, moto_testkit):
        # S3 (modo síncrono para evitar bug do moto + aiobotocore)
        s3_helper = moto_testkit.s3_helper()
        bucket_name = "full-bucket-async-no-with"
        file_key = "n.txt"
        file_content = b"456"

        s3_helper.create_bucket(bucket_name)
        s3_helper.put_object(S3ObjectModel(bucket=bucket_name, key=file_key, body=file_content))
        self.assertEqual(s3_helper.get_object_body(bucket_name, file_key), file_content)

        s3_client = moto_testkit.get_client("s3")
        buckets = s3_client.list_buckets()["Buckets"]
        self.assertIn(bucket_name, [b["Name"] for b in buckets])

        # DynamoDB (modo async normalmente)
        dynamo_helper = moto_testkit.dynamo_helper()
        table_name = "full-prod-no-with"
        dynamo_helper.create_table(table_name, key_name="sku")
        await dynamo_helper.put_item_async(
            DynamoItemModel(table=table_name, item={"sku": {"S": "Y"}, "price": {"N": "5"}})
        )
        self.assertEqual(
            (await dynamo_helper.get_item_async(table_name, {"sku": {"S": "Y"}}))["Item"]["price"]["N"], "5"
        )
        tables = (await (await moto_testkit.get_async_client("dynamodb")).list_tables())["TableNames"]
        self.assertIn(table_name, tables)

        # SQS (modo async normalmente)
        sqs_helper = moto_testkit.sqs_helper()
        queue_name = "full-q-async-no-with"
        queue = sqs_helper.create_queue(queue_name)
        await sqs_helper.send_message_async(SQSMessageModel(queue_url=queue["QueueUrl"], body="full-async-msg-no-with"))
        msgs = await sqs_helper.receive_messages_async(queue["QueueUrl"])
        self.assertEqual(msgs["Messages"][0]["Body"], "full-async-msg-no-with")

        queues = (await (await moto_testkit.get_async_client("sqs")).list_queues())["QueueUrls"]
        self.assertTrue(any(queue_name in url for url in queues))


@use_moto_testkit(patch_aiobotocore=True)
class TestFullIntegration(unittest.TestCase):

    def test_sync_example(self, moto_testkit):
        s3 = moto_testkit.get_client("s3")
        s3.create_bucket(Bucket="bucket-class-sync")
        self.assertIn("bucket-class-sync", [b["Name"] for b in s3.list_buckets()["Buckets"]])

    async def test_async_example(self, moto_testkit):
        s3 = await moto_testkit.get_async_client("s3")
        buckets = (await s3.list_buckets())["Buckets"]
        self.assertIsInstance(buckets, list)


import pytest


@pytest.mark.asyncio
@use_moto_testkit(auto_start=True, patch_aiobotocore=True)
async def test_async_s3_dynamo_sqs(moto_testkit):
    # S3
    s3_helper = moto_testkit.s3_helper()
    s3_helper.create_bucket("bucket_async")
    s3_helper.put_object(S3ObjectModel(bucket="bucket_async", key="async.txt", body=b"xyz"))
    assert s3_helper.get_object_body("bucket_async", "async.txt") == b"xyz"

    # DynamoDB
    dynamo_helper = moto_testkit.dynamo_helper()
    dynamo_helper.create_table("products_table", key_name="sku")
    await dynamo_helper.put_item_async(
        DynamoItemModel(table="products_table", item={"sku": {"S": "P1"}, "price": {"N": "9"}})
    )
    product_item = await dynamo_helper.get_item_async("products_table", {"sku": {"S": "P1"}})
    assert product_item["Item"]["price"]["N"] == "9"

    # SQS
    sqs_helper = moto_testkit.sqs_helper()
    created_queue = sqs_helper.create_queue("queue_async")
    await sqs_helper.send_message_async(SQSMessageModel(queue_url=created_queue["QueueUrl"], body="world"))
    received_messages = await sqs_helper.receive_messages_async(created_queue["QueueUrl"])
    assert received_messages["Messages"][0]["Body"] == "world"
