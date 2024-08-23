import asyncio
import json
import os
from typing import AsyncGenerator, Optional

from azure.appconfiguration.provider import load
from dotenv import load_dotenv
from assistants.threads import create_thread
from openai import AsyncAssistantEventHandler, AsyncOpenAI
from typing_extensions import override

from assistants.types import UserMessage

# Load environment variables
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_key_value(key):
    config = load(
        connection_string=os.getenv("AZURE_APPCONFIGURATION_CONNECTION_STRING")
    )
    try:
        value = config[key]
        return value
    except Exception as ex:
        print(f"Error retrieving key {key}: {ex}")
        return None


# async def ask_nutrition_assistant(user_message: str):
#     print("Ask dogy will use ask_nutrition_assistant to determine the response for nutrition in dog foods.")
#     with open("nutrition_assistant_prompt.txt", "r") as file:
#         prompt = file.read()
#         response = await client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": prompt},
#                 {"role": "user", "content": user_message}
#             ]
#         )
#         print(type(response.choices[0]))
#         return response.choices[0]


# Define an event handler class
class EventHandler(AsyncAssistantEventHandler):
    def __init__(self):
        super().__init__()
        self.responses = []

    @override
    async def on_event(self, event) -> None:
        if event.event == "thread.run.requires_action":
            run_id = event.data.id
            await self.handle_requires_action(event.data, run_id)

    @override
    async def on_text_created(self, text) -> None:
        print(f"\nassistant > {text.value}\n", end="", flush=True)
        self.responses.append(text.value)

    @override
    async def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)
        self.responses.append(delta.value)

    async def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    async def on_tool_call_delta(self, delta, snapshot):
        if delta.type == "code_interpreter":
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
                self.responses.append(delta.code_interpreter.input)
            if delta.code_interpreter.outputs:
                print("\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)
                        self.responses.append(output.logs)

    async def handle_requires_action(self, data, run_id):
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "get_current_temperature":
                # Define your get_current_temperature here
                function_args = json.loads(tool.function.arguments)
                print("get_current_temperature triggered")
                print(f"function_args: {function_args}")
                tool_outputs.append({"tool_call_id": tool.id, "output": "57"})
            # elif tool.function.name == "ask_nutrition_assistant":
            #     # Define your ask_nutrition_assistant here
            #     function_args = json.loads(tool.function.arguments)
            #     response = await ask_nutrition_assistant(function_args["user_message"])
            #     print("ask_nutrition_assistant triggered")
            #     print(f"function_args: {function_args}")
            #     tool_outputs.append({"tool_call_id": tool.id, "output": response})

        print(tool_outputs)
        await self.submit_tool_outputs(tool_outputs, run_id)

    async def submit_tool_outputs(self, tool_outputs, run_id):
        # Use the submit_tool_outputs_stream helper
        async with client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(),
        ) as stream:
            async for text in stream.text_deltas:
                # print(text, end="", flush=True)
                self.responses.append(text)


# Assistant Selector
async def retrieve_assistant(user_message: str) -> str:
    dogy_id = os.getenv("DOGY_COMPANION_ID")
    nutrition_assistant_id = os.getenv("NUTRITION_ASSISTANT_ID")
    ASSISTANT_SELECTOR_PROMPT = get_key_value("ASSISTANT_SELECTOR_PROMPT")

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": ASSISTANT_SELECTOR_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    assistant = response.choices[0].message.content
    print(f"choices: {response}")
    print(assistant)

    if assistant == "none":
        assistant_id = dogy_id
    elif assistant == "nutrition_assistant":
        assistant_id = nutrition_assistant_id

    return assistant_id


# Main function for ask dogy
async def ask_dogy_sse(
    user_message: str,
    user_name: str,
    assistant_id: Optional[str],
    thread_id: Optional[str],
) -> AsyncGenerator[str, None]:
    await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=f"{user_message}. Address me as {user_name}",
    )

    event_handler = EventHandler()

    async with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        event_handler=event_handler,
    ) as stream:
        async for text in stream.text_deltas:
            yield f"data: {text}\n"
        # await stream.until_done()

    # Skip the first response (assuming it's the duplicate "Hi")
    # return "".join([str(response) for response in event_handler.responses])


# Main function for ask dogy
async def ask_dogy(
    user_message: str,
    user_name: str,
    assistant_id: Optional[str],
    thread_id: Optional[str],
) -> str:
    await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=f"{user_message}. Address me as {user_name}",
    )

    event_handler = EventHandler()

    async with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        event_handler=event_handler,
    ) as stream:
        await stream.until_done()

    # Skip the first response (assuming it's the duplicate "Hi")
    return "".join([str(response) for response in event_handler.responses[1:]])
    # return "".join([str(response) for response in event_handler.responses])


async def inference_completion(user_message: UserMessage):
    """
    This function is used to test the completion of the model.

    Args:
        user_message (`str`): The user message

    Returns:
        response (`str`): The response from Dogy
    """

    assistant_id = await retrieve_assistant(user_message.user_message)
    await client.beta.assistants.retrieve(assistant_id=assistant_id)

    if not user_message.thread_id:
        ids = await create_thread()
        user_message.thread_id = ids["thread_id"]

    response = await ask_dogy(
        user_message.user_message,
        user_message.user_name,
        assistant_id,
        user_message.thread_id,
    )

    return response


async def inference_completion_sse(user_message: UserMessage):
    """
    This function is used to test the completion of the model.

    Args:
        user_message (`str`): The user message

    Returns:
        response (`str`): The response from Dogy
    """

    assistant_id = await retrieve_assistant(user_message.user_message)
    await client.beta.assistants.retrieve(assistant_id=assistant_id)

    if not user_message.thread_id:
        ids = await create_thread()
        user_message.thread_id = ids["thread_id"]

    async for response in ask_dogy_sse(
        user_message.user_message,
        user_message.user_name,
        assistant_id,
        user_message.thread_id,
    ):
        yield response


# Main function to run the ask_dogy function
if __name__ == "__main__":
    client = AsyncOpenAI(api_key=openai_key)
    # response = asyncio.run(ask_dogy(client, "Hello, how are you?", "Paul"))
    response = asyncio.run(ask_dogy_sse(client, "Hello, how are you?", "Sheape"))
    print(response)
