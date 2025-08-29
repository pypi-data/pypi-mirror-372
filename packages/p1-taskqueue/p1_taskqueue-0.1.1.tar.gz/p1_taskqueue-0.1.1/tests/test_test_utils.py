from unittest.mock import MagicMock
from unittest.mock import patch

from libs.test_utils import celery_worker_burst
from libs.test_utils import clear_all_celery_queues


class TestClearAllCeleryQueues:

    @patch('libs.test_utils.current_app')
    def test_clear_all_celery_queues_given_multiple_queues_expect_all_purged(self, mock_current_app):
        mock_queue1 = MagicMock()
        mock_queue2 = MagicMock()
        mock_queue_factory1 = MagicMock(return_value=mock_queue1)
        mock_queue_factory2 = MagicMock(return_value=mock_queue2)

        mock_current_app.amqp.queues.keys.return_value = ['queue1', 'queue2']
        mock_current_app.amqp.queues = {
            'queue1': mock_queue_factory1,
            'queue2': mock_queue_factory2
        }

        mock_conn = MagicMock()
        mock_chan = MagicMock()
        mock_current_app.connection_for_read.return_value.__enter__.return_value = mock_conn
        mock_conn.channel.return_value.__enter__.return_value = mock_chan

        clear_all_celery_queues()

        mock_queue_factory1.assert_called_once_with(mock_chan)
        mock_queue_factory2.assert_called_once_with(mock_chan)
        mock_queue1.purge.assert_called_once()
        mock_queue2.purge.assert_called_once()

    @patch('libs.test_utils.current_app')
    def test_clear_all_celery_queues_given_empty_queues_expect_no_purge_calls(self, mock_current_app):
        mock_current_app.amqp.queues.keys.return_value = []
        mock_current_app.amqp.queues = {}

        mock_conn = MagicMock()
        mock_chan = MagicMock()
        mock_current_app.connection_for_read.return_value.__enter__.return_value = mock_conn
        mock_conn.channel.return_value.__enter__.return_value = mock_chan

        clear_all_celery_queues()

        mock_conn.channel.assert_called_once()


class TestCeleryWorkerBurst:

    @patch('libs.test_utils.current_app')
    @patch('libs.test_utils.loads')
    def test_celery_worker_burst_given_matching_function_executor_expect_execution(self, mock_loads, mock_current_app):
        mock_task = MagicMock()
        mock_current_app.tasks = {
            'taskqueue.cmanager.dynamic_function_executor': mock_task}

        mock_message = MagicMock()
        mock_message.headers = {
            'task': 'taskqueue.cmanager.dynamic_function_executor'}
        mock_message.body = b'mock_body'
        mock_message.content_type = 'application/json'
        mock_message.content_encoding = 'utf-8'
        mock_message.acknowledged = False

        mock_loads.return_value = [
            ['module.submodule', 'test_function', [], {}], {}]

        mock_queue = MagicMock()
        mock_queue.get.side_effect = [mock_message, None]
        mock_queue_factory = MagicMock(return_value=mock_queue)
        mock_current_app.amqp.queues = {'default': mock_queue_factory}

        mock_conn = MagicMock()
        mock_chan = MagicMock()
        mock_current_app.connection_for_read.return_value.__enter__.return_value = mock_conn
        mock_conn.channel.return_value.__enter__.return_value = mock_chan

        with patch('libs.test_utils.logger') as mock_logger:
            celery_worker_burst(['module.submodule.test_function'])

            mock_logger.info.assert_any_call(
                "Executing task: module.submodule.test_function")
            mock_logger.info.assert_any_call(
                "Successfully executed task: module.submodule.test_function")

        mock_message.ack.assert_called_once()
        mock_task.apply.assert_called_once_with(
            args=['module.submodule', 'test_function', [], {}],
            kwargs={}
        )

    @patch('libs.test_utils.current_app')
    @patch('libs.test_utils.loads')
    def test_celery_worker_burst_given_matching_class_method_executor_expect_execution(self, mock_loads, mock_current_app):
        mock_task = MagicMock()
        mock_current_app.tasks = {
            'taskqueue.cmanager.dynamic_class_method_executor': mock_task}

        mock_message = MagicMock()
        mock_message.headers = {
            'task': 'taskqueue.cmanager.dynamic_class_method_executor'}
        mock_message.body = b'mock_body'
        mock_message.content_type = 'application/json'
        mock_message.content_encoding = 'utf-8'
        mock_message.acknowledged = False

        mock_loads.return_value = [
            ['module.submodule', 'TestClass', 'test_method', [], {}], {}]

        mock_queue = MagicMock()
        mock_queue.get.side_effect = [mock_message, None]
        mock_queue_factory = MagicMock(return_value=mock_queue)
        mock_current_app.amqp.queues = {'default': mock_queue_factory}

        mock_conn = MagicMock()
        mock_chan = MagicMock()
        mock_current_app.connection_for_read.return_value.__enter__.return_value = mock_conn
        mock_conn.channel.return_value.__enter__.return_value = mock_chan

        with patch('libs.test_utils.logger') as mock_logger:
            celery_worker_burst(['module.submodule.TestClass.test_method'])

            mock_logger.info.assert_any_call(
                "Executing task: module.submodule.TestClass.test_method")
            mock_logger.info.assert_any_call(
                "Successfully executed task: module.submodule.TestClass.test_method")

        mock_message.ack.assert_called_once()
        mock_task.apply.assert_called_once_with(
            args=['module.submodule', 'TestClass', 'test_method', [], {}],
            kwargs={}
        )

    @patch('libs.test_utils.current_app')
    @patch('libs.test_utils.loads')
    def test_celery_worker_burst_given_non_matching_function_expect_skip(self, mock_loads, mock_current_app):
        mock_task = MagicMock()
        mock_current_app.tasks = {
            'taskqueue.cmanager.dynamic_function_executor': mock_task}

        mock_message = MagicMock()
        mock_message.headers = {
            'task': 'taskqueue.cmanager.dynamic_function_executor'}
        mock_message.body = b'mock_body'
        mock_message.content_type = 'application/json'
        mock_message.content_encoding = 'utf-8'
        mock_message.acknowledged = False

        mock_loads.return_value = [
            ['module.submodule', 'other_function', [], {}], {}]

        mock_queue = MagicMock()
        mock_queue.get.side_effect = [mock_message, None]
        mock_queue_factory = MagicMock(return_value=mock_queue)
        mock_current_app.amqp.queues = {'default': mock_queue_factory}

        mock_conn = MagicMock()
        mock_chan = MagicMock()
        mock_current_app.connection_for_read.return_value.__enter__.return_value = mock_conn
        mock_conn.channel.return_value.__enter__.return_value = mock_chan

        celery_worker_burst(['module.submodule.test_function'])

        mock_message.ack.assert_called_once()
        mock_task.apply.assert_not_called()

    @patch('libs.test_utils.current_app')
    def test_celery_worker_burst_given_invalid_task_name_expect_warning_and_skip(self, mock_current_app):
        mock_current_app.tasks = {}

        mock_message = MagicMock()
        mock_message.headers = {'task': 'invalid.task.name'}
        mock_message.body = b'mock_body'
        mock_message.content_type = 'application/json'
        mock_message.content_encoding = 'utf-8'
        mock_message.acknowledged = False

        mock_queue = MagicMock()
        mock_queue.get.side_effect = [mock_message, None]
        mock_queue_factory = MagicMock(return_value=mock_queue)
        mock_current_app.amqp.queues = {'default': mock_queue_factory}

        mock_conn = MagicMock()
        mock_chan = MagicMock()
        mock_current_app.connection_for_read.return_value.__enter__.return_value = mock_conn
        mock_conn.channel.return_value.__enter__.return_value = mock_chan

        with patch('libs.test_utils.logger') as mock_logger:
            celery_worker_burst(['some.function'])

            mock_logger.warning.assert_called_once_with(
                "Invalid task 'invalid.task.name'. Skipping.")
            mock_message.ack.assert_called_once()

    @patch('libs.test_utils.current_app')
    def test_celery_worker_burst_given_no_messages_expect_no_processing(self, mock_current_app):
        mock_queue = MagicMock()
        mock_queue.get.return_value = None
        mock_queue_factory = MagicMock(return_value=mock_queue)
        mock_current_app.amqp.queues = {'default': mock_queue_factory}

        mock_conn = MagicMock()
        mock_chan = MagicMock()
        mock_current_app.connection_for_read.return_value.__enter__.return_value = mock_conn
        mock_conn.channel.return_value.__enter__.return_value = mock_chan

        celery_worker_burst(['some.function'])

        mock_queue.get.assert_called_once_with(no_ack=False)

    @patch('libs.test_utils.current_app')
    @patch('libs.test_utils.loads')
    def test_celery_worker_burst_given_custom_channel_expect_correct_queue_used(self, mock_loads, mock_current_app):
        mock_task = MagicMock()
        mock_current_app.tasks = {
            'taskqueue.cmanager.dynamic_function_executor': mock_task}

        mock_message = MagicMock()
        mock_message.headers = {
            'task': 'taskqueue.cmanager.dynamic_function_executor'}
        mock_message.body = b'mock_body'
        mock_message.content_type = 'application/json'
        mock_message.content_encoding = 'utf-8'
        mock_message.acknowledged = False

        mock_loads.return_value = [
            ['module.submodule', 'test_function', [], {}], {}]

        mock_queue = MagicMock()
        mock_queue.get.side_effect = [mock_message, None]
        mock_queue_factory = MagicMock(return_value=mock_queue)
        mock_current_app.amqp.queues = {'custom_queue': mock_queue_factory}

        mock_conn = MagicMock()
        mock_chan = MagicMock()
        mock_current_app.connection_for_read.return_value.__enter__.return_value = mock_conn
        mock_conn.channel.return_value.__enter__.return_value = mock_chan

        with patch('libs.test_utils.logger') as mock_logger:
            celery_worker_burst(
                ['module.submodule.test_function'], channel='custom_queue')

            mock_logger.info.assert_any_call(
                "Executing task: module.submodule.test_function")
            mock_logger.info.assert_any_call(
                "Successfully executed task: module.submodule.test_function")

        mock_queue_factory.assert_called_once_with(mock_chan)

    @patch('libs.test_utils.current_app')
    @patch('libs.test_utils.loads')
    def test_celery_worker_burst_given_task_processing_error_expect_error_logged_and_ack(self, mock_loads, mock_current_app):
        mock_task = MagicMock()
        mock_task.apply.side_effect = Exception("Task execution failed")
        mock_current_app.tasks = {
            'taskqueue.cmanager.dynamic_function_executor': mock_task}

        mock_message = MagicMock()
        mock_message.headers = {
            'task': 'taskqueue.cmanager.dynamic_function_executor'}
        mock_message.body = b'mock_body'
        mock_message.content_type = 'application/json'
        mock_message.content_encoding = 'utf-8'

        # Mock the acknowledged property to simulate ack behavior
        def get_acknowledged():
            return mock_message.ack.called
        type(mock_message).acknowledged = property(
            lambda self: get_acknowledged())

        mock_loads.return_value = [
            ['module.submodule', 'test_function', [], {}], {}]

        mock_queue = MagicMock()
        mock_queue.get.side_effect = [mock_message, None]
        mock_queue_factory = MagicMock(return_value=mock_queue)
        mock_current_app.amqp.queues = {'default': mock_queue_factory}

        mock_conn = MagicMock()
        mock_chan = MagicMock()
        mock_current_app.connection_for_read.return_value.__enter__.return_value = mock_conn
        mock_conn.channel.return_value.__enter__.return_value = mock_chan

        with patch('libs.test_utils.logger') as mock_logger:
            celery_worker_burst(['module.submodule.test_function'])

            mock_logger.info.assert_any_call(
                "Executing task: module.submodule.test_function")
            mock_logger.error.assert_called_once_with(
                "Failed to process task taskqueue.cmanager.dynamic_function_executor: Exception: Task execution failed"
            )
            mock_message.ack.assert_called_once()
