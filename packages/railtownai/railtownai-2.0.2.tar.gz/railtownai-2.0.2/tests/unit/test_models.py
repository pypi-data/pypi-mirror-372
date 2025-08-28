#   ---------------------------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------
"""Tests for the models module."""

from __future__ import annotations

import datetime
import json

import pytest

from railtownai.models import Breadcrumb, RailtownPayload


class TestRailtownPayload:
    """Test the RailtownPayload model."""

    def test_railtown_payload_creation(self):
        """Test creating a RailtownPayload instance."""
        payload = RailtownPayload(
            Message="Test message",
            Level="info",
            OrganizationId="org123",
            ProjectId="proj456",
            EnvironmentId="env789",
            Runtime="python-test",
            Exception="",
            TimeStamp="2023-01-01T00:00:00",
            Properties={"key": "value"},
        )

        assert payload.Message == "Test message"
        assert payload.Level == "info"
        assert payload.OrganizationId == "org123"
        assert payload.ProjectId == "proj456"
        assert payload.EnvironmentId == "env789"
        assert payload.Runtime == "python-test"
        assert payload.Exception == ""
        assert payload.TimeStamp == "2023-01-01T00:00:00"
        assert payload.Properties == {"key": "value"}

    def test_railtown_payload_with_breadcrumbs(self):
        """Test RailtownPayload with breadcrumbs in properties."""
        breadcrumbs = [{"message": "test", "level": "info"}]
        payload = RailtownPayload(
            Message="Test message",
            Level="error",
            OrganizationId="org123",
            ProjectId="proj456",
            EnvironmentId="env789",
            Runtime="python-test",
            Exception="Test exception",
            TimeStamp="2023-01-01T00:00:00",
            Properties={"Breadcrumbs": breadcrumbs},
        )

        assert payload.Properties["Breadcrumbs"] == breadcrumbs
        assert len(payload.Properties["Breadcrumbs"]) == 1

    def test_railtown_payload_model_dump(self):
        """Test RailtownPayload.model_dump() method."""
        payload = RailtownPayload(
            Message="Test message",
            Level="error",
            OrganizationId="org123",
            ProjectId="proj456",
            EnvironmentId="env789",
            Runtime="python-test",
            Exception="Test exception",
            TimeStamp="2023-01-01T00:00:00",
            Properties={"key": "value", "number": 42},
        )

        dumped = payload.model_dump()

        assert isinstance(dumped, dict)
        assert dumped["Message"] == "Test message"
        assert dumped["Level"] == "error"
        assert dumped["OrganizationId"] == "org123"
        assert dumped["ProjectId"] == "proj456"
        assert dumped["EnvironmentId"] == "env789"
        assert dumped["Runtime"] == "python-test"
        assert dumped["Exception"] == "Test exception"
        assert dumped["TimeStamp"] == "2023-01-01T00:00:00"
        assert dumped["Properties"] == {"key": "value", "number": 42}

    def test_railtown_payload_model_dump_json(self):
        """Test RailtownPayload.model_dump_json() method."""
        payload = RailtownPayload(
            Message="Test message",
            Level="error",
            OrganizationId="org123",
            ProjectId="proj456",
            EnvironmentId="env789",
            Runtime="python-test",
            Exception="Test exception",
            TimeStamp="2023-01-01T00:00:00",
            Properties={"key": "value", "number": 42},
        )

        json_str = payload.model_dump_json()

        assert isinstance(json_str, str)

        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["Message"] == "Test message"
        assert parsed["Level"] == "error"
        assert parsed["OrganizationId"] == "org123"
        assert parsed["ProjectId"] == "proj456"
        assert parsed["EnvironmentId"] == "env789"
        assert parsed["Runtime"] == "python-test"
        assert parsed["Exception"] == "Test exception"
        assert parsed["TimeStamp"] == "2023-01-01T00:00:00"
        assert parsed["Properties"] == {"key": "value", "number": 42}

    def test_railtown_payload_json_dumps_model_dump(self):
        """Test json.dumps(RailtownPayload().model_dump()) - current approach."""
        payload = RailtownPayload(
            Message="Test message",
            Level="error",
            OrganizationId="org123",
            ProjectId="proj456",
            EnvironmentId="env789",
            Runtime="python-test",
            Exception="Test exception",
            TimeStamp="2023-01-01T00:00:00",
            Properties={"key": "value", "number": 42},
        )

        json_str = json.dumps(payload.model_dump())

        assert isinstance(json_str, str)

        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["Message"] == "Test message"
        assert parsed["Level"] == "error"
        assert parsed["OrganizationId"] == "org123"
        assert parsed["ProjectId"] == "proj456"
        assert parsed["EnvironmentId"] == "env789"
        assert parsed["Runtime"] == "python-test"
        assert parsed["Exception"] == "Test exception"
        assert parsed["TimeStamp"] == "2023-01-01T00:00:00"
        assert parsed["Properties"] == {"key": "value", "number": 42}

    def test_railtown_payload_direct_json_dumps_fails(self):
        """Test that json.dumps(RailtownPayload()) fails - direct serialization doesn't work."""
        payload = RailtownPayload(
            Message="Test message",
            Level="error",
            OrganizationId="org123",
            ProjectId="proj456",
            EnvironmentId="env789",
            Runtime="python-test",
            Exception="Test exception",
            TimeStamp="2023-01-01T00:00:00",
            Properties={"key": "value"},
        )

        with pytest.raises(TypeError, match="Object of type RailtownPayload is not JSON serializable"):
            json.dumps(payload)

    def test_railtown_payload_str_wrapping_fails(self):
        """Test that str(json.dumps(RailtownPayload())) also fails."""
        payload = RailtownPayload(
            Message="Test message",
            Level="error",
            OrganizationId="org123",
            ProjectId="proj456",
            EnvironmentId="env789",
            Runtime="python-test",
            Exception="Test exception",
            TimeStamp="2023-01-01T00:00:00",
            Properties={"key": "value"},
        )

        with pytest.raises(TypeError, match="Object of type RailtownPayload is not JSON serializable"):
            str(json.dumps(payload))

    def test_serialization_approaches_comparison(self):
        """Test and compare different serialization approaches."""
        payload = RailtownPayload(
            Message="Test message",
            Level="error",
            OrganizationId="org123",
            ProjectId="proj456",
            EnvironmentId="env789",
            Runtime="python-test",
            Exception="Test exception",
            TimeStamp="2023-01-01T00:00:00",
            Properties={"key": "value", "number": 42, "nested": {"inner": "value"}},
        )

        # Approach 1: model_dump_json() - Pydantic built-in
        json1 = payload.model_dump_json()

        # Approach 2: json.dumps(model_dump()) - Current approach
        json2 = json.dumps(payload.model_dump())

        # Both should be valid JSON strings
        assert isinstance(json1, str)
        assert isinstance(json2, str)

        # Both should parse to the same data
        parsed1 = json.loads(json1)
        parsed2 = json.loads(json2)

        assert parsed1 == parsed2

        # Verify the content is correct
        assert parsed1["Message"] == "Test message"
        assert parsed1["Level"] == "error"
        assert parsed1["Properties"]["nested"]["inner"] == "value"

        # model_dump_json() is typically more compact (no extra spaces)
        assert len(json1) <= len(json2)

    def test_serialization_with_complex_properties(self):
        """Test serialization with complex nested properties."""
        complex_properties = {
            "user": {
                "id": 12345,
                "name": "John Doe",
                "email": "john@example.com",
                "preferences": {"theme": "dark", "notifications": True, "languages": ["en", "es"]},
            },
            "session": {"id": "sess-123", "started_at": "2023-01-01T00:00:00", "active": True},
            "breadcrumbs": [
                {"message": "User logged in", "level": "info"},
                {"message": "Page loaded", "level": "debug"},
            ],
        }

        payload = RailtownPayload(
            Message="Complex test message",
            Level="info",
            OrganizationId="org123",
            ProjectId="proj456",
            EnvironmentId="env789",
            Runtime="python-test",
            Exception="",
            TimeStamp="2023-01-01T00:00:00",
            Properties=complex_properties,
        )

        # Test both serialization approaches
        json1 = payload.model_dump_json()
        json2 = json.dumps(payload.model_dump())

        # Both should be valid JSON
        parsed1 = json.loads(json1)
        parsed2 = json.loads(json2)

        # Verify complex nested structures are preserved
        assert parsed1["Properties"]["user"]["preferences"]["languages"] == ["en", "es"]
        assert parsed1["Properties"]["session"]["active"] is True
        assert len(parsed1["Properties"]["breadcrumbs"]) == 2
        assert parsed1["Properties"]["breadcrumbs"][0]["message"] == "User logged in"

        # Both approaches should produce identical data
        assert parsed1 == parsed2

    def test_serialization_api_format_compliance(self):
        """Test that serialized output matches expected API format."""
        payload = RailtownPayload(
            Message="API format test",
            Level="error",
            OrganizationId="bb77b0a0-1cc8-403f-a358-4fabfedde558",
            ProjectId="43450b21-fd60-43f7-90ac-6784feaadfb7",
            EnvironmentId="fc5b3374-6937-4c30-9ba0-82dda7ed9746",
            Runtime="python-traceback",
            Exception="TestException: Something went wrong",
            TimeStamp="2025-08-27T19:17:46.4391418+00:00",
            Properties={"YourProperty1": "YourValue1", "YourProperty2": "YourValue2"},
        )

        json_str = payload.model_dump_json()

        # Verify it's a valid JSON string
        assert isinstance(json_str, str)

        # Parse and verify structure matches API spec
        parsed = json.loads(json_str)

        # Required fields from API documentation
        assert "Message" in parsed
        assert "Level" in parsed
        assert "Runtime" in parsed
        assert "Properties" in parsed
        assert "TimeStamp" in parsed
        assert "EnvironmentId" in parsed
        assert "OrganizationId" in parsed
        assert "ProjectId" in parsed
        assert "Exception" in parsed

        # Verify field types and values
        assert parsed["Message"] == "API format test"
        assert parsed["Level"] == "error"
        assert parsed["Runtime"] == "python-traceback"
        assert parsed["Exception"] == "TestException: Something went wrong"
        assert parsed["Properties"]["YourProperty1"] == "YourValue1"
        assert parsed["Properties"]["YourProperty2"] == "YourValue2"

        # Verify UUIDs are properly formatted
        assert len(parsed["OrganizationId"]) == 36  # UUID length
        assert len(parsed["ProjectId"]) == 36
        assert len(parsed["EnvironmentId"]) == 36

        # Verify timestamp format
        assert "T" in parsed["TimeStamp"]  # ISO format
        assert "+" in parsed["TimeStamp"]  # Timezone offset


class TestBreadcrumb:
    """Test the Breadcrumb class."""

    def test_breadcrumb_creation(self):
        """Test creating a basic breadcrumb."""
        breadcrumb = Breadcrumb("Test message")

        assert breadcrumb.message == "Test message"
        assert breadcrumb.level == "info"  # default
        assert breadcrumb.category is None
        assert breadcrumb.data == {}
        assert isinstance(breadcrumb.timestamp, str)

    def test_breadcrumb_with_all_parameters(self):
        """Test creating a breadcrumb with all parameters."""
        data = {"key": "value", "number": 42}
        breadcrumb = Breadcrumb(message="Test message", level="warning", category="test_category", data=data)

        assert breadcrumb.message == "Test message"
        assert breadcrumb.level == "warning"
        assert breadcrumb.category == "test_category"
        assert breadcrumb.data == data

    def test_breadcrumb_to_dict(self):
        """Test converting breadcrumb to dictionary."""
        data = {"key": "value"}
        breadcrumb = Breadcrumb(message="Test message", level="error", category="test", data=data)

        breadcrumb_dict = breadcrumb.to_dict()

        assert breadcrumb_dict["message"] == "Test message"
        assert breadcrumb_dict["level"] == "error"
        assert breadcrumb_dict["category"] == "test"
        assert breadcrumb_dict["data"] == data
        assert "timestamp" in breadcrumb_dict
        assert isinstance(breadcrumb_dict["timestamp"], str)

    def test_breadcrumb_timestamp_format(self):
        """Test that breadcrumb timestamp is in ISO format."""
        breadcrumb = Breadcrumb("Test message")

        # Verify it's a valid ISO timestamp
        datetime.datetime.fromisoformat(breadcrumb.timestamp)

        # Verify it's recent (within last minute)
        now = datetime.datetime.now()
        breadcrumb_time = datetime.datetime.fromisoformat(breadcrumb.timestamp)
        time_diff = abs((now - breadcrumb_time).total_seconds())
        assert time_diff < 60  # Should be within 60 seconds
