"""Test cases for AssasDatabaseHandler using a mocked MongoDB client.

This module contains unit tests for the AssasDatabaseHandler class,
which interacts with a MongoDB database.
"""

import unittest
import logging
import HtmlTestRunner
import pandas as pd

from unittest.mock import patch
from pathlib import Path
from uuid import uuid4
from unittest.mock import MagicMock
from pymongo.collection import Collection
from pymongo.database import Database
from logging.handlers import RotatingFileHandler

from assasdb import AssasDatabaseHandler
from assasdb import AssasDocumentFile

# Configure rotating file logging
log_dir = Path(__file__).parent / "log"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / (Path(__file__).stem + ".log")
log_handler = RotatingFileHandler(
    log_file,
    maxBytes=1024 * 1024,
    backupCount=3,  # 1MB per file, 3 backups
)
log_format = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
log_handler.setFormatter(log_format)
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[log_handler, logging.StreamHandler()],  # Log to file and console
)


class MockMongoClient:
    """Mock MongoDB client for testing AssasDatabaseHandler."""

    def __init__(self) -> None:
        """Initialize the mock MongoDB client."""
        # Mock the database and collection
        self.mock_db = MagicMock(spec=Database)
        self.mock_collection = MagicMock(spec=Collection)

        # Configure the database to return the mocked collection
        self.mock_db.__getitem__.return_value = self.mock_collection

    def __getitem__(self, name: str) -> MagicMock:
        """Return the mocked collection for the given name.

        Args:
            name (str): The name of the collection to retrieve.

        Returns:
            MagicMock: The mocked collection.

        """
        # Return the mocked database
        return self.mock_db


class AssasDatabaseHandlerTest(unittest.TestCase):
    """Unit tests for the AssasDatabaseHandler class."""

    @patch("pymongo.MongoClient")
    def setUp(self, mock_mongo_client: MagicMock) -> None:
        """Set up the test environment for AssasDatabaseHandler.

        This includes creating a mock MongoDB client, setting up the backup directory,
        and initializing the AssasDatabaseHandler with test parameters.

        Args:
            mock_mongo_client (MagicMock): The mocked MongoDB client.

        """
        # Create a backup directory for test logs
        backup_directory = Path(__file__).parent / "data" / "backup"
        backup_directory.mkdir(parents=True, exist_ok=True)

        # Replace the real MongoClient with the mock
        self.mock_client = MockMongoClient()
        mock_mongo_client.return_value = self.mock_client

        # Initialize the AssasDatabaseHandler with test parameters
        # Ensure the MongoDB server is running and accessible
        self.database_handler = AssasDatabaseHandler(
            client=self.mock_client,
            backup_directory=backup_directory,
            database_name="test_assas",
            file_collection_name="test_files",
        )

        self.database_handler.drop_file_collection()

    def tearDown(self) -> None:
        """Clean up after each test case."""
        self.database_handler = None

    def test_insert_file_document(self) -> None:
        """Test case to insert a document into the mocked database."""
        # Mock document
        document = {"system_uuid": "123e4567-e89b-12d3-a456-426614174000"}

        # Simulate insert operation
        self.database_handler.insert_file_document(document)

        # Assert that the mocked collection's insert_one was called
        collection = self.mock_client.mock_collection
        collection.insert_one.assert_called_once_with(document)

    def test_database_handler_insert_and_find(self) -> None:
        """Test case to insert a document into the mocked database and retrieve it."""
        # Step 1: Create a test document
        test_document = AssasDocumentFile.get_test_document_file()

        # Step 2: Configure the mock to return the test document for find_one
        self.mock_client.mock_collection.find_one.return_value = test_document

        # Step 3: Insert the document into the mocked database
        self.database_handler.insert_file_document(test_document)

        # Step 4: Retrieve the document by UUID
        found_document = self.database_handler.get_file_document_by_uuid(
            test_document["system_uuid"]
        )

        # Step 5: Assert that the retrieved document matches the test document
        self.assertEqual(test_document, found_document)

    def test_insert_and_delete_document_with_mock(self) -> None:
        """Test case to verify the insert and delete operations.

        This test case uses a mocked MongoDB client to simulate the database operations.

        Steps:
            1. Insert a document into the mocked database.
            2. Verify the document exists in the mocked database.
            3. Delete the document by its UUID.
            4. Verify the document no longer exists in the mocked database.
        """
        # Step 1: Create a test document
        new_upload_uuid = uuid4()
        test_document = AssasDocumentFile.get_test_document_file(
            system_upload_uuid=str(new_upload_uuid)
        )

        # Configure the mock to simulate the insert operation
        self.mock_client.mock_collection.insert_one.return_value = MagicMock()

        # Configure the mock to simulate the find operation
        self.mock_client.mock_collection.find_one.side_effect = lambda query: (
            test_document
            if query.get("system_upload_uuid") == str(new_upload_uuid)
            else None
        )

        # Step 2: Insert the document into the mocked database
        self.database_handler.insert_file_document(test_document)
        self.mock_client.mock_collection.insert_one.assert_called_once_with(
            test_document
        )

        # Step 3: Verify the document exists in the mocked database
        found_document = self.database_handler.get_file_document_by_upload_uuid(
            new_upload_uuid
        )
        self.assertEqual(test_document, found_document)

        # Step 4: Configure the mock to simulate the delete operation
        self.mock_client.mock_collection.delete_one.return_value = MagicMock()

        # Delete the document by its UUID
        self.database_handler.delete_file_document_by_upload_uuid(new_upload_uuid)
        self.mock_client.mock_collection.delete_one.assert_called_once_with(
            {"system_upload_uuid": str(new_upload_uuid)}
        )

        # Update the mock to simulate the document being deleted
        self.mock_client.mock_collection.find_one.side_effect = lambda query: None

        # Step 5: Verify the document no longer exists in the mocked database
        found_document = self.database_handler.get_file_document_by_upload_uuid(
            new_upload_uuid
        )
        self.assertIsNone(found_document)

    def test_get_file_document_by_uuid_with_mock(self) -> None:
        """Test case to verify the get_file_document_by_uuid function.

        This test case uses a mocked MongoDB client to simulate the find operation.

        Steps:
            1. Create a test document.
            2. Configure the mock to simulate the find operation.
            3. Retrieve the document by UUID.
            4. Verify the retrieved document matches the test document.
            5. Verify the find operation was called with the correct query.
        """
        # Step 1: Create a test document
        test_document = AssasDocumentFile.get_test_document_file()
        uuid = test_document["system_uuid"]

        # Step 2: Configure the mock to simulate the find operation
        self.mock_client.mock_collection.find_one.return_value = test_document

        # Step 3: Retrieve the document by UUID
        found_document = self.database_handler.get_file_document_by_uuid(uuid)

        # Step 4: Verify the retrieved document matches the test document
        self.assertEqual(test_document, found_document)

        # Step 5: Verify the find operation was called with the correct query
        self.mock_client.mock_collection.find_one.assert_called_once_with(
            {"system_uuid": uuid}
        )

    def test_delete_file_document_by_upload_uuid_with_mock(self) -> None:
        """Test case to verify the delete_file_document_by_upload_uuid function.

        This test case uses a mocked MongoDB client to simulate the delete operation.

        Steps:
            1. Create a test document.
            2. Configure the mock to simulate the delete operation.
            3. Delete the document by its upload UUID.
            4. Verify the delete operation was called with the correct query.
        """
        # Step 1: Create a test document with a unique upload UUID
        test_document = AssasDocumentFile.get_test_document_file()
        upload_uuid = test_document["system_upload_uuid"]

        # Step 2: Configure the mock to simulate the delete operation
        self.mock_client.mock_collection.delete_one.return_value = MagicMock()

        # Step 3: Delete the document by its upload UUID
        self.database_handler.delete_file_document_by_upload_uuid(upload_uuid)

        # Step 4: Verify the delete operation was called with the correct query
        self.mock_client.mock_collection.delete_one.assert_called_once_with(
            {"system_upload_uuid": str(upload_uuid)}
        )

    def test_dump_collections_with_mock(self) -> None:
        """Test case to verify the dump_collections function.

        This test case uses a mocked MongoDB client to simulate the find operation.

        Steps:
            1. Configure the mock to simulate the find operation.
            2. Call the dump_collections function.
            3. Verify the find operation was called on the correct collection.
        """
        # Step 1: Configure the mock to simulate the find operation
        self.mock_client.mock_collection.find.return_value = [
            {"_id": "1", "data": "test1"},
            {"_id": "2", "data": "test2"},
        ]

        # Step 2: Call the dump_collections function
        self.database_handler.dump_collections(["test_collection"])

        # Step 3: Verify the find operation was called on the correct collection
        self.mock_client.mock_collection.find.assert_called_once()

    def test_restore_collections_with_mock(self) -> None:
        """Test case to verify the restore_collections function.

        This test case uses a mocked MongoDB client to simulate the insert operation.

        Steps:
            1. Configure the mock to simulate the insert operation.
            2. Call the restore_collections function.
            3. Verify the insert operation was called for each document.
        """
        # Step 1: Configure the mock to simulate the insert operation
        self.mock_client.mock_collection.insert_many.return_value = MagicMock()

        # Step 2: Call the restore_collections function
        self.database_handler.restore_collections()

        # Step 3: Verify the insert operation was called for each document
        self.mock_client.mock_collection.replace_one.assert_called()

    @unittest.skip("Skipping test_restore_collection_from_backup for now.")
    def test_restore_collection_from_backup(self) -> None:
        """Test case to verify the restore_collection_from_backup function."""
        database_handler = AssasDatabaseHandler(
            database_name="assas_dev",
        )
        data_frame = pd.DataFrame(list(database_handler.get_file_collection().find()))

        database_handler_compare = AssasDatabaseHandler()
        data_frame_compare = pd.DataFrame(
            list(database_handler_compare.get_file_collection().find())
        )

        (
            self.assertEqual(data_frame.size, data_frame_compare.size),
            "Data frames should have the same size",
        )
        (
            self.assertEqual(data_frame.shape, data_frame_compare.shape),
            "Data frames should have the same shape",
        )
        (
            self.assertEqual(
                data_frame.columns.tolist(), data_frame_compare.columns.tolist()
            ),
            "Data frames should have the same columns",
        )
        (
            self.assertTrue(data_frame.equals(data_frame_compare)),
            "Data frames should be equal",
        )

    def test_close_resources(self) -> None:
        """Test that MongoClient.close() is called."""
        mock_client = MagicMock()
        handler = AssasDatabaseHandler(client=mock_client)

        # Call the close method
        handler.close()

        # Assert that close was called on the mock client
        mock_client.close.assert_called_once()


if __name__ == "__main__":
    unittest.main(
        testRunner=HtmlTestRunner.HTMLTestRunner(
            output="test_reports",  # Directory for HTML reports
            report_title="AssasDatabaseHandler Test Report",
            descriptions=True,
        )
    )
