import base64

import django

from immunity_python_agent import CONTEXT_TRACKER
from immunity_python_agent.common.logger import logger_config
from immunity_python_agent.context import DjangoRequest, RequestContext
from immunity_python_agent.middlewares.base_middleware import BaseMiddleware
from immunity_python_agent.setting import const
from immunity_python_agent.utils import scope

logger = logger_config("python_agent")


class ImmunityDjangoMiddleware(BaseMiddleware):
    def __init__(self, get_response=None):
        self.get_response = get_response

        super(ImmunityDjangoMiddleware, self).__init__(
            {"name": const.CONTAINER_DJANGO, "version": django.get_version()}
        )

    def __call__(self, request):
        # agent paused
        if self.setting.is_agent_paused():
            return self.get_response(request)

        context = RequestContext(DjangoRequest(request))
        with CONTEXT_TRACKER.lifespan(context):
            return self.process_response(context, request)

    def process_response(self, context, request):
        response = self.get_response(request)

        self.process_response_data(context, response)

        context = CONTEXT_TRACKER.current()
        context.detail["pool"] = context.pool
        self.openapi.async_report_upload(self.executor, context.detail)

        return response

    @scope.with_scope(scope.SCOPE_AGENT)
    def process_response_data(self, context, response):
        if (
            not response.streaming
            and response.content
            and isinstance(response.content, bytes)
        ):
            http_res_body = base64.b64encode(response.content).decode("utf-8")
        else:
            http_res_body = ""

        if hasattr(response, "headers"):
            # django >= 3.2
            # https://docs.djangoproject.com/en/3.2/releases/3.2/#requests-and -responses
            resp_header = dict(response.headers)
        else:
            # django < 3.2
            resp_header = dict(
                (key, value) for key, value in response._headers.values()
            )

        context.extract_response(resp_header, response.status_code, http_res_body)
