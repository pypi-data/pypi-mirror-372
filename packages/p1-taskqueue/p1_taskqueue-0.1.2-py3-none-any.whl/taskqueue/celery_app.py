"""
Celery application setup for TaskQueue.
Reads configuration from Django settings and auto-configures queues with DLQ.
"""
from celery import Celery
from kombu import Exchange
from kombu import Queue


def get_django_settings():
    """Get Django settings, fail fast if not properly configured."""
    try:
        from django.conf import settings
        return settings
    except ImportError:
        raise ImportError("[TaskQueue] Django settings not found.")


def create_celery_app():
    """Create and configure the Celery application."""
    settings = get_django_settings()

    app_name = getattr(settings, 'TASKQUEUE_APP_NAME', 'taskqueue')
    app = Celery(app_name)

    celery_config = {
        'broker_url': getattr(settings, 'CELERY_BROKER_URL', 'amqp://localhost:5672//'),
        'result_backend': getattr(settings, 'CELERY_RESULT_BACKEND', 'rpc://localhost:5672//'),
        'task_serializer': getattr(settings, 'CELERY_TASK_SERIALIZER', 'pickle'),
        'result_serializer': getattr(settings, 'CELERY_RESULT_SERIALIZER', 'pickle'),
        'accept_content': getattr(settings, 'CELERY_ACCEPT_CONTENT', ['pickle']),
        'timezone': getattr(settings, 'CELERY_TIMEZONE', 'UTC+7'),
        'task_track_started': getattr(settings, 'CELERY_TASK_TRACK_STARTED', True),
        'task_time_limit': getattr(settings, 'CELERY_TASK_TIME_LIMIT', 30 * 60),
        'task_soft_time_limit': getattr(settings, 'CELERY_TASK_SOFT_TIME_LIMIT', 25 * 60),
        'task_always_eager': getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False),
        'task_eager_propagates': getattr(settings, 'CELERY_TASK_EAGER_PROPAGATES', True),
        'task_acks_late': True,
        'task_reject_on_worker_lost': True,
        'worker_prefetch_multiplier': 1,
        'worker_max_tasks_per_child': 1000,
    }

    setup_queues(app, settings, celery_config)
    app.conf.update(celery_config)
    app.autodiscover_tasks(['taskqueue'])

    return app


def setup_queues(app, settings, celery_config):
    app_name = getattr(settings, 'TASKQUEUE_APP_NAME', 'taskqueue')
    queue_names = getattr(settings, 'TASKQUEUE_QUEUES',
                          ['default', 'high', 'low'])
    if queue_names is None:
        queue_names = ['default', 'high', 'low']
    dlq_name_prefix = getattr(settings, 'TASKQUEUE_DLQ_NAME_PREFIX', 'dlq')

    # Create exchanges
    main_exchange = Exchange(app_name, type='direct')
    dlx_exchange = Exchange(f'{app_name}.dlx', type='direct')

    queues = []

    for queue_name in queue_names:
        dlq_name = f'{dlq_name_prefix}.{queue_name}'

        queue = Queue(
            queue_name,
            main_exchange,
            routing_key=queue_name,
            queue_arguments={
                'x-dead-letter-exchange': f'{app_name}.dlx',
                'x-dead-letter-routing-key': dlq_name
            }
        )
        queues.append(queue)

    for queue_name in queue_names:
        dlq_name = f'{dlq_name_prefix}.{queue_name}'
        dlq = Queue(dlq_name, dlx_exchange, routing_key=dlq_name)
        queues.append(dlq)

    celery_config.update({
        'task_default_queue': 'default',
        'task_default_exchange': app_name,
        'task_default_exchange_type': 'direct',
        'task_queues': tuple(queues),
    })


celery_app = create_celery_app()
