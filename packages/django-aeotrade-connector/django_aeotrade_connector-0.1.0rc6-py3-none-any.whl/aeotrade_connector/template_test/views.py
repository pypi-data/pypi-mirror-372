from aeotrade_connector.exceptions import MethodNotAllowed
from aeotrade_connector.utils import APIResponse
from rest_framework.decorators import api_view


@api_view(["POST"])
def connector_account_check(request):
    return APIResponse()


@api_view(["POST"])
def task_create(request):
    return APIResponse()


@api_view(["POST"])
def task_update(request, task_id: str):
    return APIResponse()


@api_view(["DELETE"])
def task_delete(request, task_id: str):
    return APIResponse()


@api_view(["POST"])
def task_start(request):
    return APIResponse()


@api_view(["POST"])
def task_stop(request):
    return APIResponse()


def task_update_or_delete(request, task_id):
    if request.method == "POST":
        return task_update(request, task_id)
    elif request.method == "DELETE":
        return task_delete(request, task_id)
    else:
        raise MethodNotAllowed
