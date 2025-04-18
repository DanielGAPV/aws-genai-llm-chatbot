import os
import json
import uuid
import boto3
import asyncio
from datetime import datetime
from genai_core.registry import registry
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType
from aws_lambda_powertools.utilities.batch.exceptions import BatchProcessingError
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext

import adapters  # noqa: F401 Needed to register the adapters
from genai_core.utils.websocket import send_to_client
from genai_core.types import ChatbotAction
from genai_core.langchain import DynamoDBChatMessageHistory

from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage

processor = BatchProcessor(event_type=EventType.SQS)
tracer = Tracer()
logger = Logger()

AWS_REGION = os.environ["AWS_REGION"]
API_KEYS_SECRETS_ARN = os.environ["API_KEYS_SECRETS_ARN"]

sequence_number = 0
bedrock_agent_client=boto3.client(
            service_name="bedrock-agent", region_name='ap-southeast-1'
        )
runtime_client=boto3.client(
            service_name="bedrock-agent-runtime", region_name='ap-southeast-1'
        )

def on_llm_new_token(
    user_id, session_id, self, token, run_id, chunk, parent_run_id, *args, **kwargs
):
    if self.disable_streaming:
        logger.debug("Streaming is disabled, ignoring token")
        return
    if isinstance(token, list):
        # When using the newer Chat objects from Langchain.
        # Token is not a string
        text = ""
        for t in token:
            if "text" in t:
                text = text + t.get("text")
    else:
        text = token
    if text is None or len(text) == 0:
        return
    global sequence_number
    sequence_number += 1
    run_id = str(run_id)

    send_to_client(
        {
            "type": "text",
            "action": ChatbotAction.LLM_NEW_TOKEN.value,
            "userId": user_id,
            "timestamp": str(int(round(datetime.now().timestamp()))),
            "data": {
                "sessionId": session_id,
                "token": {
                    "runId": run_id,
                    "sequenceNumber": sequence_number,
                    "value": text,
                },
            },
        }
    )


def handle_heartbeat(record):
    user_id = record["userId"]
    session_id = record["data"]["sessionId"]

    send_to_client(
        {
            "type": "text",
            "action": ChatbotAction.HEARTBEAT.value,
            "timestamp": str(int(round(datetime.now().timestamp()))),
            "userId": user_id,
            "data": {
                "sessionId": session_id,
            },
        }
    )


async def handle_run(record):
    user_id = record["userId"]
    user_groups = record["userGroups"]
    data = record["data"]
    provider = data["provider"]
    model_id = data["modelName"]
    mode = data["mode"]
    prompt = data["text"]
    workspace_id = data.get("workspaceId", None)
    session_id = data.get("sessionId")
    images = data.get("images", [])
    documents = data.get("documents", [])
    videos = data.get("videos", [])
    system_prompts = record.get("systemPrompts", {})
    if not session_id:
        session_id = str(uuid.uuid4())

    # adapter = registry.get_adapter(f"{provider}.{model_id}")

    # adapter.on_llm_new_token = lambda *args, **kwargs: on_llm_new_token(
    #     user_id, session_id, *args, **kwargs
    # )

    # model = adapter(
    #     model_id=model_id,
    #     mode=mode,
    #     session_id=session_id,
    #     user_id=user_id,
    #     model_kwargs=data.get("modelKwargs", {}),
    # )

    # response = model.run(
    #     prompt=prompt,
    #     workspace_id=workspace_id,
    #     user_groups=user_groups,
    #     images=images,
    #     documents=documents,
    #     videos=videos,
    #     system_prompts=system_prompts,
    # )

    # logger.debug(response)

    # send_to_client(
    #     {
    #         "type": "text",
    #         "action": ChatbotAction.FINAL_RESPONSE.value,
    #         "timestamp": str(int(round(datetime.now().timestamp()))),
    #         "userId": user_id,
    #         "userGroups": user_groups,
    #         "data": response,
    #     }
    # )

    #Get DynamoDB Sessions Table
    chat_history = DynamoDBChatMessageHistory(
        table_name=os.environ["SESSIONS_TABLE_NAME"],
        session_id=session_id,
        user_id=user_id,
    )

    response = runtime_client.invoke_agent(
            agentId='SWGKKAR9A5',
            agentAliasId="RWNGZ3XZV4",
            sessionId=session_id,
            inputText=prompt,
        )
    
    logger.debug(response)
    print("Agent response", response)

    completion = ""

    for event in response.get("completion"):
        chunk = event["chunk"]
        completion += chunk["bytes"].decode()
    
    print("Completion", completion)

    #Add user prompt and chatbot response to DynamoDB
    chat_history.add_message(HumanMessage(prompt))
    chat_history.add_message(AIMessage(completion))
    
    response = {
        "sessionId": session_id,
        "type": "text",
        "content": completion,
    }
    
    send_to_client(
        {
            "type": "text",
            "action": ChatbotAction.FINAL_RESPONSE.value,
            "timestamp": str(int(round(datetime.now().timestamp()))),
            "userId": user_id,
            "userGroups": user_groups,
            "data": response,
        }
    )

    """ return response """


@tracer.capture_method
def record_handler(record: SQSRecord):
    payload: str = record.body
    message: dict = json.loads(payload)
    detail: dict = json.loads(message["Message"])
    logger.debug(detail)
    logger.info("details", detail=detail)

    if detail["action"] == ChatbotAction.RUN.value:
        data = asyncio.run(handle_run(detail))
        print("data", data)
        send_to_client(
            {
                "type": "text",
                "action": ChatbotAction.FINAL_RESPONSE.value,
                "userId": detail["userId"],
                "userGroups": detail["userGroups"],
                "timestamp": str(int(round(datetime.now().timestamp()))),
                "data": data
            }
        )
    elif detail["action"] == ChatbotAction.HEARTBEAT.value:
        handle_heartbeat(detail)


def handle_failed_records(records):
    for triplet in records:
        status, error, record = triplet
        payload: str = record.body
        message: dict = json.loads(payload)
        detail: dict = json.loads(message["Message"])
        user_id = detail["userId"]
        data = detail.get("data", {})
        session_id = data.get("sessionId", "")

        message = "⚠️ *Something went wrong*"
        if (
            "An error occurred (ValidationException)" in error
            and "The provided image must have dimensions in set [1280x720]" in error
        ):
            # At this time only one input size is supported by the Nova reel model.
            message = "⚠️ *The provided image must have dimensions of 1280x720.*"
        elif (
            "An error occurred (ValidationException)" in error
            and "The width of the provided image must be within range [320, 4096]"
            in error
        ):
            # At this time only this size is supported by the Nova canvas model.
            message = "⚠️ *The width of the provided image must be within range 320 and 4096 pixels.*"  # noqa
        elif (
            "An error occurred (AccessDeniedException)" in error
            and "You don't have access to the model with the specified model ID"
            in error
        ):
            message = (
                "*This model is not enabled. "
                "Please try again later or contact "
                "an administrator*"
            )
        else:
            logger.error("Unable to process request", error=error)

        send_to_client(
            {
                "type": "text",
                "action": "error",
                "direction": "OUT",
                "userId": user_id,
                "timestamp": str(int(round(datetime.now().timestamp()))),
                "data": {
                    "sessionId": session_id,
                    # Log a vague message because the error can contain
                    # internal information
                    "content": message,
                    "type": "text",
                },
            }
        )


@logger.inject_lambda_context(log_event=False)
@tracer.capture_lambda_handler
def handler(event, context: LambdaContext):
    batch = event["Records"]

    api_keys = parameters.get_secret(API_KEYS_SECRETS_ARN, transform="json")
    for key in api_keys:
        os.environ[key] = api_keys[key]

    try:
        with processor(records=batch, handler=record_handler):
            processed_messages = processor.process()
    except BatchProcessingError as e:
        logger.error(e)

    for message in processed_messages:
        logger.info(
            "Request compelte with status " + message[0],
            status=message[0],
            cause=message[1],
        )
    handle_failed_records(
        message for message in processed_messages if message[0] == "fail"
    )

    return processor.response()
