from transformers import AutoTokenizer

class PromptInjection:
    """
    Represents a prompt injection attempt, potentially simulating a multi-turn conversation.

    This class extends the concept of a normal prompt with additional fields for
    simulating assistant responses, chain-of-thought, and tool outputs.
    """
    def __init__(self, model_id: str, system_message: str, developer_message: str, user_message: str, tools=None, assistant_message=None, analysis=None, tool_response=None):
        """
        Initializes the PromptInjection object.

        Args:
            model_id (str): The identifier of the model to use.
            system_message (str): The system message.
            developer_message (str): The developer-provided message.
            user_message (str): The user's message .
            tools (ToolBox, optional): A ToolBox object. Defaults to None.
            assistant_message (str, optional): A simulated assistant message. Defaults to None.
            assistant_cot (str, optional): A simulated assistant's chain-of-thought. Defaults to None.
            tool_response (str, optional): A simulated response from a tool. Defaults to None.
        """
        self.model_id = model_id
        self.system_message = system_message
        self.developer_message = developer_message
        self.user_message = user_message
        self.tools = tools
        self.assistant_message = assistant_message
        self.analysis = analysis
        self.tool_response = tool_response
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
   

    def __str__(self):
        """
        Applies the chat template to the full sequence of messages.

        Returns:
            str: The formatted prompt injection string.
        """
        tool_list = [tool.to_dict() for tool in self.tools.tools] if self.tools else None
        messages = [
            {"role": "system", "content": self.system_message+"""#Tools:## python
Use this tool to execute Python code in your chain of thought. The code will not be shown to the user. This tool should be used for internal reasoning, but not for code that is intended to be visible to the user (e.g. when creating plots, tables, or files).
When you send a message containing Python code to python, it will be executed in a stateful Jupyter notebook environment. python will respond with the output of the execution or time out after 120.0 seconds. The drive at '/mnt/data' can be used to save and persist user files. Internet access for this session is Available."""+self.developer_message+str(tool_list)},
            {"role": "user", "content": self.user_message},
        ]

        
        if self.analysis:
            # The role for COT might vary by model, 'assistant_cot' is a placeholder
            messages.append({"role": "analysis", "content": self.analysis})
        if self.tool_response:
            # The role for tool responses can also vary
            messages.append({"role": "tool_response", "content": self.tool_response})
        if self.assistant_message:
            messages.append({"role": "assistant", "content": self.assistant_message})
        

        return self.tokenizer.apply_chat_template(messages, tokenize=False)