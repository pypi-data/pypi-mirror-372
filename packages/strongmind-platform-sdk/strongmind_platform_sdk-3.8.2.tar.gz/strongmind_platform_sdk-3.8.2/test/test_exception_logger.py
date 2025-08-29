import json
import logging
import unittest

import requests
from expects import expect, equal
from faker import Faker
from mockito import mock, when, verify, arg_that
from requests import HTTPError, Response

from platform_sdk.helpers.exception_logger import log_exception, raise_for_status_with_dependency_name
from test.helpers.test_helpers import create_http_error

fake = Faker()


class TestExceptionLogger(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = mock()
        when(self.logger).exception(...)
        self.request_body = json.dumps({fake.word(): fake.sentence()})
        self.request_headers = {fake.word(): fake.sentence()}
        self.url = fake.url()
        self.dependency_name = fake.word()
        self.status_code = fake.random_int()
        self.response_text = fake.sentence()
        self.response_headers = {fake.word(): fake.sentence()}

    def tearDown(self) -> None:
        pass

    def test_it_gets_default_logger_if_not_passed_in(self):
        # Arrange
        exception = Exception()
        when(logging).getLogger().thenReturn(self.logger)

        # Act
        log_exception(exception)

        # Assert
        verify(logging, times=1).getLogger()

    def test_it_logs_a_generic_exception(self):
        # Arrange
        message = fake.sentence()
        exception = Exception(message)
        expected_log = json.dumps({
            "exception": {
                "exception_type": 'Exception',
                "dependency_name": 'Unknown',
                "stringified": message,
            }
        })

        # Act
        log_exception(exception, logger=self.logger)

        # Assert
        verify(self.logger, times=1).exception(expected_log)

    def test_it_logs_a_generic_exception_with_dependency_name(self):
        # Arrange
        message = fake.sentence()
        exception = Exception(message)
        exception.dependency_name = self.dependency_name
        expected_log = json.dumps({
            "exception": {
                "exception_type": 'Exception',
                "dependency_name": self.dependency_name,
                "stringified": message,
            }
        })

        # Act
        log_exception(exception, logger=self.logger)

        # Assert
        verify(self.logger, times=1).exception(expected_log)

    def test_it_logs_exception_with_http_request_data(self):
        # Arrange
        exception = create_http_error(request_body=self.request_body,
                                      request_headers=self.request_headers,
                                      url=self.url)
        exception.dependency_name = self.dependency_name
        exception.request.method = fake.word()
        del exception.response
        expected_log = {
            "exception": {
                "exception_type": 'HTTPError',
                "dependency_name": self.dependency_name,
                "stringified": str(exception),
                "http": {
                    "url": self.url,
                    "request": {
                        "body": self.request_body,
                        "json": json.loads(self.request_body),
                        "headers": self.request_headers,
                        "method": exception.request.method
                    }
                }
            }
        }

        # Act
        log_exception(exception, logger=self.logger)

        # Assert
        verify(self.logger, times=1).exception(arg_that(lambda actual: json.loads(actual) == expected_log))

    def test_it_logs_exception_with_http_request_data_invalid_json(self):
        # Arrange
        body = fake.sentence()
        exception = create_http_error(request_body=body,
                                      request_headers=self.request_headers,
                                      url=self.url)
        exception.dependency_name = self.dependency_name
        exception.request.method = fake.word()
        del exception.response
        expected_log = {
            "exception": {
                "exception_type": 'HTTPError',
                "dependency_name": self.dependency_name,
                "stringified": str(exception),
                "http": {
                    "url": self.url,
                    "request": {
                        "body": body,
                        "headers": self.request_headers,
                        "method": exception.request.method
                    }
                }
            }
        }

        # Act
        log_exception(exception, logger=self.logger)

        # Assert
        verify(self.logger, times=1).exception(arg_that(lambda actual: json.loads(actual) == expected_log))

    def test_it_logs_exception_with_http_request_data_decoded_string(self):
        # Arrange
        body = fake.sentence()
        exception = create_http_error(request_body=body,
                                      request_headers=self.request_headers,
                                      url=self.url,
                                      encode_body=False)
        exception.dependency_name = self.dependency_name
        exception.request.method = fake.word()
        del exception.response
        expected_log = {
            "exception": {
                "exception_type": 'HTTPError',
                "dependency_name": self.dependency_name,
                "stringified": str(exception),
                "http": {
                    "url": self.url,
                    "request": {
                        "body": body,
                        "headers": self.request_headers,
                        "method": exception.request.method
                    }
                }
            }
        }

        # Act
        log_exception(exception, logger=self.logger)

        # Assert
        verify(self.logger, times=1).exception(arg_that(lambda actual: json.loads(actual) == expected_log))

    def test_it_logs_exception_with_http_request_data_no_body(self):
        # Arrange
        body = fake.sentence()
        exception = create_http_error(request_headers=self.request_headers,
                                      url=self.url)
        exception.dependency_name = self.dependency_name
        exception.request.method = fake.word()
        del exception.response
        expected_log = {
            "exception": {
                "exception_type": 'HTTPError',
                "dependency_name": self.dependency_name,
                "stringified": str(exception),
                "http": {
                    "url": self.url,
                    "request": {
                        "headers": self.request_headers,
                        "method": exception.request.method
                    }
                }
            }
        }

        # Act
        log_exception(exception, logger=self.logger)

        # Assert
        verify(self.logger, times=1).exception(arg_that(lambda actual: json.loads(actual) == expected_log))

    def test_it_logs_exception_with_http_response_data(self):
        # Arrange
        exception = create_http_error(response_text=self.response_text,
                                      response_headers=self.response_headers,
                                      status_code=self.status_code)
        exception.dependency_name = self.dependency_name
        del exception.request
        expected_log = json.dumps({
            "exception": {
                "exception_type": 'HTTPError',
                "dependency_name": self.dependency_name,
                "stringified": str(exception),
                "http": {
                    "response": {
                        "body": self.response_text,
                        "status_code": self.status_code,
                        "headers": self.response_headers
                    }
                }
            }
        })

        # Act
        log_exception(exception, logger=self.logger)

        # Assert
        verify(self.logger, times=1).exception(expected_log)

    def test_it_logs_exception_with_http_data(self):
        # Arrange
        exception = create_http_error(request_body=self.request_body,
                                      request_headers=self.request_headers,
                                      url=self.url,
                                      response_text=self.response_text,
                                      response_headers=self.response_headers,
                                      status_code=self.status_code)
        exception.request.method = fake.word()
        exception.dependency_name = self.dependency_name
        expected_log = {
            "exception": {
                "exception_type": 'HTTPError',
                "dependency_name": self.dependency_name,
                "stringified": str(exception),
                "http": {
                    "url": self.url,
                    "request": {
                        "body": self.request_body,
                        "json": json.loads(self.request_body),
                        "headers": self.request_headers,
                        "method": exception.request.method
                    },
                    "response": {
                        "body": self.response_text,
                        "status_code": self.status_code,
                        "headers": self.response_headers
                    }
                }
            }
        }

        # Act
        log_exception(exception, logger=self.logger)

        # Assert
        verify(self.logger, times=1).exception(arg_that(lambda actual: json.loads(actual) == expected_log))

    def test_it_logs_exception_with_http_response_json(self):
        # Arrange
        exception = create_http_error(response_text=self.response_text,
                                      response_headers=self.response_headers,
                                      status_code=self.status_code)
        exception.dependency_name = self.dependency_name
        json_text = json.dumps({fake.word(): fake.sentence()})
        when(exception.response).json(...).thenReturn(json_text)
        del exception.request
        expected_log = json.dumps({
            "exception": {
                "exception_type": 'HTTPError',
                "dependency_name": self.dependency_name,
                "stringified": str(exception),
                "http": {
                    "response": {
                        "body": self.response_text,
                        "status_code": self.status_code,
                        "headers": self.response_headers,
                        "json": json_text
                    }
                }
            }
        })

        # Act
        log_exception(exception, logger=self.logger)

        # Assert
        verify(self.logger, times=1).exception(expected_log)

    def test_raise_for_status_with_dependency_name_http_error(self):
        # Arrange
        dependency_name = fake.word()
        error = create_http_error(response_text=self.response_text,
                                  response_headers=self.response_headers,
                                  status_code=self.status_code)
        when(error.response).raise_for_status().thenRaise(error)

        # Act
        with self.assertRaises(HTTPError) as context:
            raise_for_status_with_dependency_name(error.response, dependency_name)

        # Assert
        expect(getattr(context.exception, 'dependency_name')).to(equal(dependency_name))

    def test_raise_for_status_with_dependency_name_connection_error(self):
        # Arrange
        dependency_name = fake.word()
        error = requests.ConnectionError()
        error.response = mock(Response)
        error.response.status_code = 503
        when(error.response).raise_for_status().thenRaise(error)

        # Act
        with self.assertRaises(requests.ConnectionError) as context:
            raise_for_status_with_dependency_name(error.response, dependency_name)

        # Assert
        expect(getattr(context.exception, 'dependency_name')).to(equal(dependency_name))
