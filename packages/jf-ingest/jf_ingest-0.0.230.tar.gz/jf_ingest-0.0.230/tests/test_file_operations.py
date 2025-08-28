import json
from contextlib import contextmanager
from datetime import datetime
from unittest.mock import patch

import pytest
import requests
import requests_mock

from jf_ingest.config import IngestionConfig, IngestionType
from jf_ingest.file_operations import IngestIOHelper, SubDirectory
from jf_ingest.utils import RetryLimitExceeded


class TestIngestIOHelper:
    company_slug = "test_company"
    timestamp = "20231205_123456"
    local_file_path = "/tmp"
    api_token = "test_token"
    S3_URL = "https://jellyfish-agent-upload.s3.amazonaws.com/"
    ingest_io_helper = None
    S3_OBJ_PATH_PATH = None

    def _get_ingest_io_helper(self) -> IngestIOHelper:
        return IngestIOHelper(ingest_config=self._get_ingest_config())

    def _get_ingest_config(self):
        return IngestionConfig(
            company_slug=self.company_slug,
            timestamp=self.timestamp,
            local_file_path=self.local_file_path,
            jellyfish_api_token=self.api_token,
        )

    def setup_method(self):
        self.ingest_io_helper = self._get_ingest_io_helper()

        self.S3_OBJ_PATH_PATH = f"{self.company_slug}/{self.timestamp}/jira/"

    @contextmanager
    def _mock_local_and_s3_upload_function(self):
        with (
            patch.object(
                self.ingest_io_helper, 'write_json_data_to_local', return_value=None
            ) as local_mocker,
            patch.object(
                self.ingest_io_helper, 'write_json_data_to_s3', return_value=None
            ) as s3_mocker,
        ):
            yield (local_mocker, s3_mocker)

    def test_json_serializer_helper_function(self):
        json_data = {"str": "str", "int": 1, "datetime": datetime(year=2023, day=29, month=3)}
        # Serialize data to bytes
        serialized_json_data = self.ingest_io_helper._serialize_json_to_bytes(
            json_data=json_data, indent_level=0
        )
        # Deserialize data back
        decoded_data = json.loads(serialized_json_data)

        assert json_data['str'] == decoded_data['str']
        assert json_data['datetime'] == datetime.fromisoformat(decoded_data['datetime'])
        assert json_data['int'] == decoded_data['int']

    def test_write_json_to_local_or_s3_local_only(self):
        with self._mock_local_and_s3_upload_function() as (local_mocker, s3_mocker):
            self.ingest_io_helper.write_json_to_local_or_s3(
                'test', {}, SubDirectory.JIRA, save_locally=True, upload_to_s3=False
            )
            local_mocker.assert_called_once()
            s3_mocker.assert_not_called()

    def test_write_json_to_local_or_s3_s3_only(self):
        with self._mock_local_and_s3_upload_function() as (local_mocker, s3_mocker):
            self.ingest_io_helper.write_json_to_local_or_s3(
                'test', {}, SubDirectory.JIRA, save_locally=False, upload_to_s3=True
            )
            local_mocker.assert_not_called()
            s3_mocker.assert_called_once()

    def test_write_json_to_local_or_s3_both(self):
        with self._mock_local_and_s3_upload_function() as (local_mocker, s3_mocker):
            self.ingest_io_helper.write_json_to_local_or_s3(
                'test', {}, SubDirectory.JIRA, save_locally=True, upload_to_s3=True
            )
            local_mocker.assert_called_once()
            s3_mocker.assert_called_once()

    def test_write_json_to_local_test_error_handling(self):
        """We want to assert that errors are always bubbled up if an upload or save fails"""
        with self._mock_local_and_s3_upload_function() as (local_mocker, s3_mocker):
            local_mocker.side_effect = Exception('test')
            s3_mocker.side_effect = Exception('test')
            # First, assert that when the functions are NOT called they DO NOT raise any exceptions
            self.ingest_io_helper.write_json_to_local_or_s3(
                'test', {}, SubDirectory.JIRA, save_locally=False, upload_to_s3=False
            )
            local_mocker.assert_not_called()
            s3_mocker.assert_not_called()

            # Then, assert that when they do get called they do raise errors
            with pytest.raises(Exception):
                self.ingest_io_helper.write_json_to_local_or_s3(
                    'test', {}, SubDirectory.JIRA, save_locally=True, upload_to_s3=True
                )
            with pytest.raises(Exception):
                self.ingest_io_helper.write_json_to_local_or_s3(
                    'test', {}, SubDirectory.JIRA, save_locally=True, upload_to_s3=False
                )
            with pytest.raises(Exception):
                self.ingest_io_helper.write_json_to_local_or_s3(
                    'test', {}, SubDirectory.JIRA, save_locally=False, upload_to_s3=True
                )

    def test_write_and_read_file(self):
        self.ingest_io_helper.write_json_data_to_local(
            "jira_test_data", {"test": "data"}, SubDirectory.JIRA
        )

        with open("/tmp/jira/jira_test_data.json", "r") as f:
            data = json.load(f)
            assert data == {"test": "data"}

    def test_write_file_error_raising(self):
        with patch.object(
            self.ingest_io_helper, '_write_file', return_value=None
        ) as write_file_mocker:
            write_file_mocker.side_effect = Exception(f'Exception happened writing file')
            # Assert that errors bubble up
            with pytest.raises(Exception):
                self.ingest_io_helper.write_json_data_to_local(
                    "jira_test_data", {"test": "data"}, SubDirectory.JIRA
                )

    @contextmanager
    def _mock_jellyfish_signed_url_endpoint(
        self,
        filepath: str,
        trigger_error_on_jellyfish_upload: bool = False,
        trigger_error_on_s3_upload: bool = False,
    ):
        print(type(filepath))
        json_resp = {
            "signed_urls": {
                f'{filepath}.gz': {
                    's3_path': f'{self.S3_OBJ_PATH_PATH}/{filepath}',
                    "url": {
                        "url": self.S3_URL,
                        "fields": {
                            "key": f"{self.company_slug}/{self.timestamp}/jira/{filepath}.gz",
                            "AWSAccessKeyId": "PLACEHOLDER",
                            "x-amz-security-token": "PLACEHOLDER",
                        },
                    },
                },
            },
        }
        with requests_mock.Mocker() as m:
            m: requests_mock.Mocker = m
            jellyfish_endpoint_status = 500 if trigger_error_on_jellyfish_upload else 200
            m.register_uri(
                method="POST",
                url=f"https://app.jellyfish.co/endpoints/ingest/signed-url?timestamp={self.timestamp}",
                json=json_resp,
                status_code=jellyfish_endpoint_status,
            )

            s3_upload_status = 500 if trigger_error_on_s3_upload else 200
            m.register_uri(method="POST", url=self.S3_URL, status_code=s3_upload_status)
            yield m

    def _test_signed_url_helper(self, ingestion_type: IngestionType):
        filename = "jira_test_data.json"
        self.ingest_io_helper.ingest_config.ingest_type = ingestion_type
        with self._mock_jellyfish_signed_url_endpoint(filename) as m:
            s3_path, url, fields = self.ingest_io_helper.get_signed_url(filename)
            assert m.last_request.json()["ingestType"] == ingestion_type.value
            assert url == self.S3_URL
            assert s3_path == f'{self.S3_OBJ_PATH_PATH}/{filename}'
            assert type(fields) == dict

    def test_get_signed_url_for_direct_connect(self):
        self._test_signed_url_helper(ingestion_type=IngestionType.DIRECT_CONNECT)

    def test_get_signed_url_for_agent(self):
        self._test_signed_url_helper(ingestion_type=IngestionType.AGENT)

    def test_upload_data_to_s3(self):
        object_name = "test_data"
        filename = "jira/test_data.json"
        json_data = {"test": "data"}
        with self._mock_jellyfish_signed_url_endpoint(filename) as m:
            self.ingest_io_helper.write_json_data_to_s3(
                object_name=object_name, json_data=json_data, subdirectory=SubDirectory.JIRA
            )
            request_strs = [str(r) for r in m.request_history]
            assert (
                f"POST https://app.jellyfish.co/endpoints/ingest/signed-url?timestamp={self.timestamp}"
                in request_strs
            )
            assert f"POST {self.S3_URL}" in request_strs

    def test_upload_data_to_s3_failure_at_jellyfish_endpoint(self):
        object_name = "test_data"
        filename = "jira/test_data.json"
        json_data = {"test": "data"}
        with self._mock_jellyfish_signed_url_endpoint(
            filename, trigger_error_on_jellyfish_upload=True
        ) as m, patch('time.sleep', return_value=0):
            with pytest.raises(RetryLimitExceeded):
                self.ingest_io_helper.write_json_data_to_s3(
                    object_name=object_name, json_data=json_data, subdirectory=SubDirectory.JIRA
                )

    def test_upload_data_to_s3_failure_at_s3_endpoint(self):
        object_name = "test_data"
        filename = "jira/test_data.json"
        json_data = {"test": "data"}
        with self._mock_jellyfish_signed_url_endpoint(
            filename, trigger_error_on_s3_upload=True
        ) and patch("jf_ingest.utils.time.sleep", return_value=0):
            with pytest.raises(RetryLimitExceeded):
                self.ingest_io_helper.write_json_data_to_s3(
                    object_name=object_name, json_data=json_data, subdirectory=SubDirectory.JIRA
                )
