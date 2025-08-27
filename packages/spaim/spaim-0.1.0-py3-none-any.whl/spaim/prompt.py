from transformers import AutoTokenizer

class Prompt:
    """
    Represents a single prompt to be sent to a large language model.

    This class takes various message components (system, developer, user) and
    formats them into a single string using the tokenizer's chat template
    for a specific model.
    """
    def __init__(self, model_id: str, system_message: str, developer_message: str, user_message: str, tools=None):
        """
        Initializes the Prompt object.

        Args:
            model_id (str): The identifier of the model to use (e.g., "OpenAI/gpt-oss-20b").
            system_message (str): The system message.
            developer_message (str): The developer-provided message.
            user_message (str): The user's message.
            tools (ToolBox, optional): A ToolBox object containing available tools. Defaults to None.
        """
        self.model_id = model_id
        self.system_message = system_message
        self.developer_message = developer_message
        self.user_message = user_message
        self.tools = tools
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)

    def __str__(self):
        """
        Applies the chat template to the messages and returns the formatted string.

        Returns:
            str: The fully formatted prompt string with special tokens.
        """
        messages = [
            {"role": "system", "content":self.system_message+self.developer_message+self.tools.__str__()},
            {"role": "user", "content": self.user_message},
        ]

        # Add tools to the prompt if they exist
        if self.tools:
            # This is a simplified representation.
            # The actual format will depend on the model's specific tool-use template.
            messages.append({"role": "tools", "content": str(self.tools)})

        return self.tokenizer.apply_chat_template(messages, tokenize=False)
