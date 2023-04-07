import pickle
import typing as t
import uuid

from aiohttp import web
from aiohttp_cors import CorsViewMixin

from server.utils import internal_error
from server.utils import validate_data
from share.log import LoggerMixin


class TaskHandler(CorsViewMixin, web.View, LoggerMixin):
    @internal_error
    async def get(self):
        """
        Get task
        ---
        summary: Get task
        tags:
          - task
        security:
          - APIGatewayAuthorizer: []
        description: Get request
        responses:
          '200':
            description: Successful operation
            content:
              application/json:
                schema:
                  $ref: "#/components/schemas/TaskResponse"
          '500':
            $ref: "#/components/responses/InternalServerError"
        """
        uid: str = self.request.get("uid", str(uuid.uuid4()))
        message = {"task": "GET"}
        result_in_bytes = await self.request.app["rabbitmq"].send_message(
            message,
            uid,
        )
        raw_results: t.Dict = pickle.loads(result_in_bytes)
        return web.json_response(raw_results)

    @internal_error
    async def post(self):
        """
        Post data
        ---
        summary: Post data
        tags:
          - camera
        security:
          - APIGatewayAuthorizer: []
        description: Post request
        requestBody:
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: string
        responses:
          '200':
            description: Successful operation
            content:
              application/json:
                schema:
                  $ref: "#/components/schemas/TaskResponse"
          '400':
             $ref: "#/components/responses/BadRequest"
          '500':
             $ref: "#/components/responses/InternalServerError"
        """
        uid: str = self.request.get("uid", str(uuid.uuid4()))
        data = await self.request.json()
        try:
            validate_data(data)
        except ValueError as e:
            self.logger.exception(f"{str(e)}")
            return web.HTTPBadRequest(text=str(e))
        message = {"task": "POST", "data": data}
        result_in_bytes = await self.request.app["rabbitmq"].send_message(
            message,
            uid,
        )
        raw_results: t.Dict = pickle.loads(result_in_bytes)
        return web.json_response(raw_results)
