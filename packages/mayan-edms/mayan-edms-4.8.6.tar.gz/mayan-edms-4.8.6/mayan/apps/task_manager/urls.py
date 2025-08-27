from django.urls import re_path

from .views import QueueTaskTypeListView, WorkerListView, WorkerQueueListView

urlpatterns_queues = [
    re_path(
        route=r'^queues/(?P<queue_name>\w+)/task_types/$',
        view=QueueTaskTypeListView.as_view(), name='queue_task_type_list'
    )
]

urlpatterns_workers = [
    re_path(
        route=r'^workers/$', view=WorkerListView.as_view(),
        name='worker_list'
    ),
    re_path(
        route=r'^workers/(?P<worker_name>\w+)/queues/$',
        view=WorkerQueueListView.as_view(), name='worker_queue_list'
    )
]

urlpatterns = []
urlpatterns.extend(urlpatterns_queues)
urlpatterns.extend(urlpatterns_workers)
