import json
from IPython.display import display, HTML
import markdown

import google.generativeai as genai
from google.generativeai.types import Tool, FunctionDeclaration

# TODO : not finished

class Tools:
    def __init__(self):
        self.tools = {}
        self.functions = {}

    def add_tool(self, function, description):
        self.tools[function.__name__] = description
        self.functions[function.__name__] = function

    def get_tools(self):
        # 轉換成 Gemini 的 Tool 格式
        return [
            Tool(
                function_declarations=[
                    FunctionDeclaration(
                        name=fn_name,
                        description=desc,
                        parameters=self._infer_params(self.functions[fn_name])
                    )
                ]
            )
            for fn_name, desc in self.tools.items()
        ]

    def _infer_params(self, fn):
        from inspect import signature
        sig = signature(fn)
        props = {}
        for name, param in sig.parameters.items():
            props[name] = {
                "type": "string",
                "description": f"{name} argument"
            }
        return {
            "type": "object",
            "properties": props,
            "required": list(props.keys())
        }

    def function_call(self, tool_call):
        function_name = tool_call.function_call.name
        arguments = json.loads(tool_call.function_call.args)
        f = self.functions[function_name]
        result = f(**arguments)

        return {
            "function_response": {
                "name": function_name,
                "response": result,
            },
            "tool_request_id": tool_call.tool_request_id,
        }


def shorten(text, max_length=50):
    return text if len(text) <= max_length else text[:max_length - 3] + "..."


class ChatInterface:
    def input(self):
        return input("You: ")

    def display(self, message):
        print(message)

    def display_function_call(self, entry, result):
        call_html = f"""
        <details>
        <summary>Function call: <tt>{entry.function_call.name}({shorten(entry.function_call.args)})</tt></summary>
        <div>
            <b>Call</b>
            <pre>{entry}</pre>
        </div>
        <div>
            <b>Output</b>
            <pre>{json.dumps(result['function_response']['response'], indent=2)}</pre>
        </div>
        </details>
        """
        display(HTML(call_html))

    def display_response(self, entry):
        if entry.text:
            response_html = markdown.markdown(entry.text)
            html = f"""
            <div>
                <div><b>Assistant:</b></div>
                <div>{response_html}</div>
            </div>
            """
            display(HTML(html))


class ChatAssistant:
    def __init__(self, tools, developer_prompt, chat_interface, client):
        self.tools = tools
        self.developer_prompt = developer_prompt
        self.chat_interface = chat_interface
        self.client = client
        self.history = []

    def gpt(self, chat_messages, tool_responses=None):
        return self.client.generate_content(
            chat_messages,
            tools=self.tools.get_tools(),
            tool_config={"function_calling_config": "AUTO"},
            tool_responses=tool_responses or [],
            stream=False,
        )

    def run(self):
        chat_messages = [self.developer_prompt]

        while True:
            question = self.chat_interface.input()
            if question.strip().lower() == 'stop':
                self.chat_interface.display("Chat ended.")
                break

            chat_messages.append({"role": "user", "parts": [question]})
            tool_responses = []

            while True:
                response = self.gpt(chat_messages, tool_responses=tool_responses)
                parts = response.candidates[0].content.parts

                tool_calls = []
                has_message = False

                for part in parts:
                    if part.function_call:
                        tool_calls.append(part)
                    elif part.text:
                        self.chat_interface.display_response(part)
                        chat_messages.append({"role": "model", "parts": [part]})
                        has_message = True

                if tool_calls:
                    for tool_call in tool_calls:
                        result = self.tools.function_call(tool_call)
                        self.chat_interface.display_function_call(tool_call, result)
                        tool_responses.append(result)

                if has_message:
                    break
