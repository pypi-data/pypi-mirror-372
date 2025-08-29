"""Tests for the celery_app module."""
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from taskqueue.celery_app import create_celery_app
from taskqueue.celery_app import get_django_settings
from taskqueue.celery_app import setup_queues


class TestGetDjangoSettings:

    def test_get_django_settings_given_django_available_expect_return_settings(self):
        with patch('django.conf.settings') as mock_settings:
            result = get_django_settings()
            assert result == mock_settings

    def test_get_django_settings_given_django_not_available_expect_raise_import_error(self):
        with patch('builtins.__import__', side_effect=ImportError("No module named 'django'")):
            with pytest.raises(ImportError, match="\\[TaskQueue\\] Django settings not found\\."):
                get_django_settings()


class TestCreateCeleryApp:

    @patch('taskqueue.celery_app.setup_queues')
    @patch('taskqueue.celery_app.get_django_settings')
    @patch('taskqueue.celery_app.Celery')
    def test_create_celery_app_given_valid_settings_expect_celery_app_created(
        self, mock_celery_class, mock_get_settings, mock_setup_queues
    ):
        mock_settings = MagicMock()
        mock_settings.TASKQUEUE_APP_NAME = 'testapp'
        mock_settings.CELERY_BROKER_URL = 'redis://localhost:6379/0'
        mock_settings.CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
        mock_settings.CELERY_TASK_SERIALIZER = 'pickle'
        mock_settings.CELERY_RESULT_SERIALIZER = 'pickle'
        mock_settings.CELERY_ACCEPT_CONTENT = ['pickle']
        mock_settings.CELERY_TIMEZONE = 'UTC'
        mock_settings.CELERY_TASK_TRACK_STARTED = True
        mock_settings.CELERY_TASK_TIME_LIMIT = 1800
        mock_settings.CELERY_TASK_SOFT_TIME_LIMIT = 1500
        mock_settings.CELERY_TASK_ALWAYS_EAGER = False
        mock_settings.CELERY_TASK_EAGER_PROPAGATES = True

        mock_get_settings.return_value = mock_settings
        mock_app = MagicMock()
        mock_celery_class.return_value = mock_app

        result = create_celery_app()

        mock_celery_class.assert_called_once_with('testapp')
        mock_setup_queues.assert_called_once()
        mock_app.conf.update.assert_called_once()
        mock_app.autodiscover_tasks.assert_called_once_with(['taskqueue'])
        assert result == mock_app

    @patch('taskqueue.celery_app.setup_queues')
    @patch('taskqueue.celery_app.get_django_settings')
    @patch('taskqueue.celery_app.Celery')
    def test_create_celery_app_given_missing_settings_expect_defaults_used(
        self, mock_celery_class, mock_get_settings, mock_setup_queues
    ):
        mock_settings = MagicMock()
        del mock_settings.TASKQUEUE_APP_NAME
        del mock_settings.CELERY_BROKER_URL
        del mock_settings.CELERY_RESULT_BACKEND
        del mock_settings.CELERY_TASK_SERIALIZER
        del mock_settings.CELERY_RESULT_SERIALIZER
        del mock_settings.CELERY_ACCEPT_CONTENT
        del mock_settings.CELERY_TIMEZONE
        del mock_settings.CELERY_TASK_TRACK_STARTED
        del mock_settings.CELERY_TASK_TIME_LIMIT
        del mock_settings.CELERY_TASK_SOFT_TIME_LIMIT
        del mock_settings.CELERY_TASK_ALWAYS_EAGER
        del mock_settings.CELERY_TASK_EAGER_PROPAGATES

        mock_get_settings.return_value = mock_settings
        mock_app = MagicMock()
        mock_celery_class.return_value = mock_app

        result = create_celery_app()

        mock_celery_class.assert_called_once_with('taskqueue')
        assert result == mock_app


class TestSetupQueues:
    """Test setup_queues function."""

    def test_setup_queues_given_valid_settings_expect_queues_configured(self):
        """Test that setup_queues configures queues and DLQs correctly."""
        mock_app = MagicMock()
        mock_settings = MagicMock()
        mock_settings.TASKQUEUE_APP_NAME = 'testapp'
        mock_settings.TASKQUEUE_QUEUES = ['default', 'high', 'low']
        mock_settings.TASKQUEUE_DLQ_NAME_PREFIX = 'dlq'

        celery_config = {}

        setup_queues(mock_app, mock_settings, celery_config)

        # Assertions
        assert celery_config['task_default_queue'] == 'default'
        assert celery_config['task_default_exchange'] == 'testapp'
        assert celery_config['task_default_exchange_type'] == 'direct'
        assert len(celery_config['task_queues']) == 6

        main_queues = [q for q in celery_config['task_queues']
                       if not q.name.startswith('dlq.')]
        assert len(main_queues) == 3
        assert any(q.name == 'default' for q in main_queues)
        assert any(q.name == 'high' for q in main_queues)
        assert any(q.name == 'low' for q in main_queues)

        dlq_queues = [q for q in celery_config['task_queues']
                      if q.name.startswith('dlq.')]
        assert len(dlq_queues) == 3
        assert any(q.name == 'dlq.default' for q in dlq_queues)
        assert any(q.name == 'dlq.high' for q in dlq_queues)
        assert any(q.name == 'dlq.low' for q in dlq_queues)

    def test_setup_queues_given_missing_settings_expect_defaults_used(self):
        mock_app = MagicMock()
        mock_settings = MagicMock()
        del mock_settings.TASKQUEUE_APP_NAME
        del mock_settings.TASKQUEUE_QUEUES
        del mock_settings.TASKQUEUE_DLQ_NAME_PREFIX

        celery_config = {}

        setup_queues(mock_app, mock_settings, celery_config)

        assert celery_config['task_default_queue'] == 'default'
        assert celery_config['task_default_exchange'] == 'taskqueue'
        assert celery_config['task_default_exchange_type'] == 'direct'
        assert len(celery_config['task_queues']) == 6

    def test_setup_queues_given_single_queue_expect_correct_configuration(self):
        mock_app = MagicMock()
        mock_settings = MagicMock()
        mock_settings.TASKQUEUE_APP_NAME = 'singleapp'
        mock_settings.TASKQUEUE_QUEUES = ['single']
        mock_settings.TASKQUEUE_DLQ_NAME_PREFIX = 'dead'

        celery_config = {}

        setup_queues(mock_app, mock_settings, celery_config)

        assert len(celery_config['task_queues']) == 2

        main_queue = next(
            q for q in celery_config['task_queues'] if q.name == 'single')
        assert main_queue.queue_arguments['x-dead-letter-exchange'] == 'singleapp.dlx'
        assert main_queue.queue_arguments['x-dead-letter-routing-key'] == 'dead.single'

        dlq = next(
            q for q in celery_config['task_queues'] if q.name == 'dead.single')
        assert dlq.exchange.name == 'singleapp.dlx'


class TestCeleryAppIntegration:
    """Integration tests for the celery_app module."""

    @patch('taskqueue.celery_app.get_django_settings')
    def test_celery_app_import_given_django_configured_expect_app_created(self, mock_get_settings):
        mock_settings = MagicMock()
        mock_settings.TASKQUEUE_APP_NAME = 'testapp'
        mock_settings.CELERY_BROKER_URL = 'redis://localhost:6379/0'
        mock_settings.CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
        mock_settings.CELERY_TASK_SERIALIZER = 'pickle'
        mock_settings.CELERY_RESULT_SERIALIZER = 'pickle'
        mock_settings.CELERY_ACCEPT_CONTENT = ['pickle']
        mock_settings.CELERY_TIMEZONE = 'UTC'
        mock_settings.CELERY_TASK_TRACK_STARTED = True
        mock_settings.CELERY_TASK_TIME_LIMIT = 1800
        mock_settings.CELERY_TASK_SOFT_TIME_LIMIT = 1500
        mock_settings.CELERY_TASK_ALWAYS_EAGER = False
        mock_settings.CELERY_TASK_EAGER_PROPAGATES = True
        mock_settings.TASKQUEUE_QUEUES = ['default']
        mock_settings.TASKQUEUE_DLQ_NAME_PREFIX = 'dlq'

        mock_get_settings.return_value = mock_settings

        from taskqueue.celery_app import celery_app
        assert celery_app is not None
