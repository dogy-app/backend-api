import asyncio
from dotenv import load_dotenv
import os
import json
from openai import AsyncOpenAI, AsyncAssistantEventHandler
from typing_extensions import override
from typing import Optional

# Load environment variables
load_dotenv()

dogy_id = os.getenv("DOGY_COMPANION_ID")
nutrition_assistant_id = os.getenv("NUTRITION_ASSISTANT_ID")
openai_key = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
                self.responses.append(delta.code_interpreter.input)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
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
async def retrieve_assistant(user_message: str) -> str | None:
    ASSISTANT_SELECTOR_PROMPT=f"""You are an Assistant selector. Your task is to determine the
best assistant based on the user input. Try your best to determine the best assistant to
use, if the query does not correspond to any assistant, return "none". The background
context for all of them is that they are all dog-friendly. The output should all
be in lowercase and only the name of the assistant, no punctuations or anything else.
Here are the examples for each assistant, your goal is to determine the correct assistant
based on the following information. The pattern is assistant: query_example. Here are
the examples:

nutrition_assistant: What are the essential nutrients that should be in my dog's food?
nutrition_assistant: How much protein does my dog need in their diet?
nutrition_assistant: Is grain-free dog food better for my dog?
nutrition_assistant: How do I choose a high-quality dog food?
nutrition_assistant: Can I feed my dog a vegetarian or vegan diet?
nutrition_assistant: Are raw diets safe and nutritious for dogs?
nutrition_assistant: What are the best sources of fat for my dog's diet?
nutrition_assistant: How do I know if my dog has food allergies?
nutrition_assistant: What are the signs of a nutritionally balanced dog food?
nutrition_assistant: How often should I change my dog's food?
nutrition_assistant: Is homemade dog food better than commercial dog food?
nutrition_assistant: How much calcium does my dog need?
nutrition_assistant: Can I give my dog supplements to improve their nutrition?
nutrition_assistant: What ingredients should I avoid in my dog's food?
nutrition_assistant: How can I tell if my dog is overweight or underweight?
nutrition_assistant: Are there specific diets for dogs with certain health conditions?
nutrition_assistant: How much water should my dog drink daily?
nutrition_assistant: Can puppies and adult dogs eat the same food?
nutrition_assistant: What is the best diet for senior dogs?
nutrition_assistant: How do I transition my dog to a new type of food?
    """

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": ASSISTANT_SELECTOR_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )
    assistant = response.choices[0].message.content
    print(f"choices: {response}")
    print(assistant)
    print(type(assistant))
    if assistant == "none":
        return dogy_id
    elif assistant == "nutrition_assistant":
        return nutrition_assistant_id
    else:
        return ""

# Main function for ask dogy
async def ask_dogy(
    user_message: str,
    user_name: str,
    assistant_id: Optional[str],
    thread_id: Optional[str]
) -> str:
    await client.beta.threads.messages.create(
        thread_id=thread_id,
        role='user',
        content=f'{user_message}. Address me as {user_name}'
    )

    event_handler = EventHandler()

    async with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        event_handler=event_handler,
    ) as stream:
        await stream.until_done()

    # Skip the first response (assuming it's the duplicate "Hi")
    # return "".join([str(response) for response in event_handler.responses[1:]])
    return "".join([str(response) for response in event_handler.responses])

# Main function to run the ask_dogy function
if __name__ == "__main__":
    client = AsyncOpenAI(api_key=openai_key)
    # response = asyncio.run(ask_dogy(client, "Hello, how are you?", "Paul"))
    response = asyncio.run(ask_dogy(client, "Hello, how are you?", "Sheape", "THREAD_ID"))
    print(response)
