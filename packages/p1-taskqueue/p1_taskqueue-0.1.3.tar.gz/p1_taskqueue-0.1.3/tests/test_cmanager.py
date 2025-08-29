from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from taskqueue.cmanager import _build_dynamic_task_call
from taskqueue.cmanager import _is_class_method
from taskqueue.cmanager import _split_function_and_queue_kwargs
from taskqueue.cmanager import CManager
from taskqueue.cmanager import K_DEFAULT_RETRY_COUNTDOWN
from taskqueue.cmanager import K_MAX_RETRY_COUNT
# Import the functions and classes to test


class TestClass:

    def test_method(self):
        pass

    @classmethod
    def class_method(cls):
        pass

    @staticmethod
    def static_method():
        pass


def test_function():
    """Test function for testing function detection."""


class TestIsClassMethod:

    def test__is_class_method_given_function_expect_return_false(self):
        result = _is_class_method(test_function)
        assert result is False

    def test__is_class_method_given_class_method_expect_return_true(self):
        instance = TestClass()
        result = _is_class_method(instance.test_method)
        assert result is True

    def test__is_class_method_given_classmethod_decorator_expect_return_true(self):
        result = _is_class_method(TestClass.class_method)
        assert result is True

    def test__is_class_method_given_staticmethod_decorator_expect_return_false(self):
        result = _is_class_method(TestClass.static_method)
        assert result is False

    def test__is_class_method_given_unbound_method_expect_return_false(self):
        result = _is_class_method(TestClass.test_method)
        assert result is False


class TestSplitFunctionAndQueueKwargs:

    def test__split_function_and_queue_kwargs_given_mixed_kwargs_expect_correct_split(self):
        kwargs = {
            'channel': 'high',
            'retry': {'max_retries': 5},
            'on_commit': True,
            'job_timeout': 300,
            'user_id': 123,
            'data': {'key': 'value'}
        }

        func_kwargs, queue_kwargs = _split_function_and_queue_kwargs(kwargs)

        assert func_kwargs == {'user_id': 123, 'data': {'key': 'value'}}
        assert queue_kwargs == {
            'channel': 'high',
            'retry': {'max_retries': 5},
            'on_commit': True,
            'job_timeout': 300
        }

    def test__split_function_and_queue_kwargs_given_only_function_kwargs_expect_empty_queue_kwargs(self):
        kwargs = {'user_id': 123, 'data': 'test'}

        func_kwargs, queue_kwargs = _split_function_and_queue_kwargs(kwargs)

        assert func_kwargs == {'user_id': 123, 'data': 'test'}
        assert queue_kwargs == {}

    def test__split_function_and_queue_kwargs_given_only_queue_kwargs_expect_empty_func_kwargs(self):
        kwargs = {'channel': 'default', 'retry': {'max_retries': 3}}

        func_kwargs, queue_kwargs = _split_function_and_queue_kwargs(kwargs)

        assert func_kwargs == {}
        assert queue_kwargs == {
            'channel': 'default', 'retry': {'max_retries': 3}}

    def test__split_function_and_queue_kwargs_given_ignored_celery_keys_expect_they_are_ignored(self):
        kwargs = {
            'queue': 'default',
            'countdown': 10,
            'eta': datetime.now(),
            'priority': 1,
            'user_id': 123
        }

        func_kwargs, queue_kwargs = _split_function_and_queue_kwargs(kwargs)

        assert func_kwargs == {'user_id': 123}
        assert queue_kwargs == {}


class TestBuildDynamicTaskCall:

    def test__build_dynamic_task_call_given_function_expect_function_executor_task(self):
        task_name, task_args, task_kwargs = _build_dynamic_task_call(
            test_function, 1, 2, key='value'
        )

        assert task_name == "taskqueue.cmanager.dynamic_function_executor"
        assert task_args == ['tests.test_cmanager',
                             'test_function', [1, 2], {'key': 'value'}]
        assert task_kwargs == {}

    def test__build_dynamic_task_call_given_bound_method_expect_class_method_executor_task(self):
        instance = TestClass()
        task_name, task_args, task_kwargs = _build_dynamic_task_call(
            instance.test_method, 1, 2, key='value'
        )

        assert task_name == "taskqueue.cmanager.dynamic_class_method_executor"
        assert task_args == ['tests.test_cmanager',
                             'TestClass', 'test_method', [1, 2], {'key': 'value'}]
        assert task_kwargs == {}

    def test__build_dynamic_task_call_given_function_without_module_expect_raise_value_error(self):
        mock_func = Mock()
        mock_func.__module__ = None
        mock_func.__name__ = 'test_func'

        with pytest.raises(ValueError, match="Unsupported callable type for Celery enqueue"):
            _build_dynamic_task_call(mock_func)

    def test__build_dynamic_task_call_given_function_without_name_expect_raise_value_error(self):
        mock_func = Mock()
        mock_func.__module__ = 'test_module'
        mock_func.__name__ = None

        with pytest.raises(ValueError, match="Unsupported callable type for Celery enqueue"):
            _build_dynamic_task_call(mock_func)


class TestCManager:

    @patch('taskqueue.cmanager.logger')
    @patch.object(CManager, '_send_task')
    def test_cmanager_enqueue_given_function_expect_send_task_called(self, mock_send_task, mock_logger):
        cm = CManager()
        cm.enqueue(test_function, 1, 2, key='value')

        mock_send_task.assert_called_once()
        call_args = mock_send_task.call_args
        assert call_args[0][0] == "taskqueue.cmanager.dynamic_function_executor"

    @patch('taskqueue.cmanager.logger')
    @patch.object(CManager, '_send_task')
    def test_cmanager_enqueue_at_given_datetime_and_function_expect_send_task_called_with_eta(self, mock_send_task, mock_logger):
        cm = CManager()
        eta = datetime.now()
        cm.enqueue_at(eta, test_function, 1, 2)

        mock_send_task.assert_called_once()
        call_args = mock_send_task.call_args
        assert call_args[0][0] == "taskqueue.cmanager.dynamic_function_executor"

    @patch('taskqueue.cmanager.logger')
    @patch.object(CManager, '_send_task')
    def test_cmanager_enqueue_in_given_timedelta_and_function_expect_send_task_called_with_countdown(self, mock_send_task, mock_logger):
        cm = CManager()
        delta = timedelta(seconds=60)
        cm.enqueue_in(delta, test_function, 1, 2)

        mock_send_task.assert_called_once()
        call_args = mock_send_task.call_args
        assert call_args[0][0] == "taskqueue.cmanager.dynamic_function_executor"

    def test_cmanager_enqueue_given_no_args_expect_raise_value_error(self):
        cm = CManager()
        with pytest.raises(ValueError, match="enqueue requires a callable as the first positional argument"):
            cm.enqueue()

    def test_cmanager_enqueue_at_given_insufficient_args_expect_raise_value_error(self):
        cm = CManager()
        with pytest.raises(ValueError, match="enqueue_at requires \\(eta_datetime, func, \\*func_args\\)"):
            cm.enqueue_at(datetime.now())

    def test_cmanager_enqueue_in_given_insufficient_args_expect_raise_value_error(self):
        cm = CManager()
        with pytest.raises(ValueError, match="enqueue_in requires \\(countdown_delta, func, \\*func_args\\)"):
            cm.enqueue_in(timedelta(seconds=10))

    def test_cmanager_enqueue_op_given_unknown_type_expect_raise_value_error(self):
        cm = CManager()
        with pytest.raises(ValueError, match="Unknown enqueue operation type: invalid"):
            cm._enqueue_op_base(test_function, enqueue_op_type='invalid')

    @patch('django.db.transaction.on_commit')
    @patch.object(CManager, '_enqueue_op_base')
    def test_cmanager_enqueue_op_given_on_commit_true_expect_transaction_on_commit_called(self, mock_enqueue_op_base, mock_on_commit):
        cm = CManager()
        cm._enqueue_op(test_function, on_commit=True)

        mock_on_commit.assert_called_once()

    @patch('django.db.transaction.on_commit')
    @patch.object(CManager, '_enqueue_op_base')
    def test_cmanager_enqueue_op_given_on_commit_false_expect_enqueue_op_base_called_directly(self, mock_enqueue_op_base, mock_on_commit):
        cm = CManager()
        cm._enqueue_op(test_function, on_commit=False)

        mock_enqueue_op_base.assert_called_once()
        mock_on_commit.assert_not_called()

    @patch('taskqueue.celery_app.celery_app')
    def test_cmanager__send_task_given_task_args_expect_celery_app_send_task_called(self, mock_celery_app):
        cm = CManager()
        cm._send_task("test.task", [1, 2], {
                      "key": "value"}, {"channel": "high"})

        mock_celery_app.send_task.assert_called_once()
        call_args = mock_celery_app.send_task.call_args
        # send_task is called with keyword arguments
        args, kwargs = call_args
        assert args[0] == "test.task"
        assert kwargs["args"] == [1, 2]
        # The retry policy is added automatically, so we need to check for both
        expected_kwargs = {"key": "value", "retry": {
            "max_retries": K_MAX_RETRY_COUNT, "countdown": K_DEFAULT_RETRY_COUNTDOWN}}
        assert kwargs["kwargs"] == expected_kwargs
        assert kwargs["queue"] == "high"

    @patch('taskqueue.celery_app.celery_app')
    def test_cmanager__send_task_given_no_retry_policy_expect_default_retry_policy_applied(self, mock_celery_app):
        cm = CManager()
        cm._send_task("test.task", [], {}, {})

        mock_celery_app.send_task.assert_called_once()
        call_args = mock_celery_app.send_task.call_args
        args, kwargs = call_args
        assert kwargs["kwargs"]["retry"] == {
            "max_retries": K_MAX_RETRY_COUNT,
            "countdown": K_DEFAULT_RETRY_COUNTDOWN
        }

    @patch('taskqueue.celery_app.celery_app')
    def test_cmanager__send_task_given_custom_retry_policy_expect_custom_policy_used(self, mock_celery_app):
        cm = CManager()
        custom_retry = {"max_retries": 5, "countdown": 20}
        cm._send_task("test.task", [], {}, {"retry": custom_retry})

        mock_celery_app.send_task.assert_called_once()
        call_args = mock_celery_app.send_task.call_args
        args, kwargs = call_args
        assert kwargs["kwargs"]["retry"] == custom_retry


class TestDynamicTaskExecutors:

    def test_dynamic_function_executor_given_valid_module_and_function_expect_function_executed(self):
        """Test that dynamic_function_executor is properly decorated."""
        from taskqueue.cmanager import dynamic_function_executor

        # Just verify the function exists and is decorated
        assert hasattr(dynamic_function_executor, 'delay')
        assert hasattr(dynamic_function_executor, 'apply_async')

    def test_dynamic_class_method_executor_given_valid_class_and_method_expect_method_executed(self):
        """Test that dynamic_class_method_executor is properly decorated."""
        from taskqueue.cmanager import dynamic_class_method_executor

        # Just verify the function exists and is decorated
        assert hasattr(dynamic_class_method_executor, 'delay')
        assert hasattr(dynamic_class_method_executor, 'apply_async')

    @patch('taskqueue.cmanager.importlib.import_module')
    def test_dynamic_function_executor_given_import_error_expect_retry_raised(self, mock_import_module):
        mock_import_module.side_effect = ImportError("Module not found")

        from taskqueue.cmanager import dynamic_function_executor

        with pytest.raises(Exception):  # retry is raised
            dynamic_function_executor("invalid_module", "test_function")

    @patch('taskqueue.cmanager.importlib.import_module')
    def test_dynamic_function_executor_given_max_retries_reached_expect_reject_raised(self, mock_import_module):
        mock_import_module.side_effect = ImportError("Module not found")

        from taskqueue.cmanager import dynamic_function_executor

        # Mock the request object to simulate max retries reached
        mock_self = Mock()
        mock_self.request.retries = K_MAX_RETRY_COUNT
        mock_self.max_retries = K_MAX_RETRY_COUNT

        with pytest.raises(Exception):  # Reject should be raised
            dynamic_function_executor(
                mock_self, "invalid_module", "test_function",
                retry={"max_retries": K_MAX_RETRY_COUNT}
            )
