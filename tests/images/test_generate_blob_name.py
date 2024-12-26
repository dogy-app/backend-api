import os
import uuid
from unittest.mock import patch

import pytest

from app.images.crud import generate_blob_name


@pytest.mark.parametrize(
    "file_name, custom_name, expected_base",
    [
        ("example.png", None, "example"),
        ("example with spaces.png", None, "example_with_spaces"),
        ("example.png", "custom name", "custom_name"),
        ("example.png", "custom_name", "custom_name"),
    ],
)

@patch("uuid.uuid4")
def test_generate_blob_name(mock_uuid, file_name, custom_name, expected_base):
    """
    Test that the blob name is correctly generated with proper formatting.
    """
    # Mock the unique ID
    mock_uuid.return_value = uuid.UUID("12345678123456781234567812345678")

    # Call the function
    blob_name = generate_blob_name(file_name, custom_name)

    # Extract the file extension and unique ID
    file_extension = os.path.splitext(file_name)[1]

    # Expected blob name
    expected_blob_name = f"{expected_base}_12345678-1234-5678-1234-567812345678{file_extension}"

    assert blob_name == expected_blob_name


def test_generate_blob_name_with_empty_file_extension():
    """
    Test generating a blob name when the file name has no extension.
    """
    test_uuid = uuid.UUID("87654321876543218765432187654321")
    with patch("uuid.uuid4", return_value=test_uuid):
        file_name = "example"
        custom_name = None
        blob_name = generate_blob_name(file_name, custom_name)

        expected_blob_name = f"example_{test_uuid}"
        assert blob_name == expected_blob_name


def test_generate_blob_name_with_long_file_name():
    """
    Test handling of long file names.
    """
    test_uuid = uuid.UUID("abcdefabcdefabcdefabcdefabcdef12")
    with patch("uuid.uuid4", return_value=test_uuid):
        file_name = "a" * 255 + ".png"  # Maximum typical file name length
        custom_name = None
        blob_name = generate_blob_name(file_name, custom_name)

        expected_blob_name = f"{'a' * 255}_{test_uuid}.png"
        assert blob_name == expected_blob_name


@pytest.mark.parametrize(
    "file_name, custom_name, expected_error",
    [
        ("", None, ValueError),
        (None, None, TypeError),
    ],
)
def test_generate_blob_name_invalid_input(file_name, custom_name, expected_error):
    """
    Test that invalid inputs raise the correct exceptions.
    """
    with pytest.raises(expected_error):
        generate_blob_name(file_name, custom_name)


@patch("uuid.uuid4")
def test_generate_blob_name_uuid_is_called(mock_uuid):
    """
    Test that uuid.uuid4 is called during blob name generation.
    """
    mock_uuid.return_value = uuid.UUID("12345678123456781234567812345678")

    file_name = "example.png"
    custom_name = None
    generate_blob_name(file_name, custom_name)

    # Ensure uuid4 is called once
    mock_uuid.assert_called_once()
