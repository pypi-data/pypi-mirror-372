import re
from transformers import AutoTokenizer

class SpaimFilter:
    """
    Filters a prompt by removing all content between the first and last special
    tokens found in the model's specific chat template.
    """
    def __init__(self, model_id):
        """
        Initializes the filter by extracting special tokens from the chat template.

        Args:
            model_id (str): The model identifier to load the correct tokenizer and template.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        if not self.tokenizer.chat_template:
            raise ValueError(f"The tokenizer for '{model_id}' does not have a chat_template.")

        # Find all unique special tokens like <|start|>, <|message|>, etc. from the template
        special_tokens_list = re.findall(r'(<\|.*?\|>)', self.tokenizer.chat_template)
        
        # Ensure the list contains only unique tokens
        self.special_tokens = sorted(list(set(special_tokens_list)), key=len, reverse=True)

        if not self.special_tokens:
            raise ValueError(f"Could not extract any special tokens in the format <|...|> from the chat template for '{model_id}'.")

        # Escape tokens for regex
        escaped_tokens = [re.escape(token) for token in self.special_tokens]
        
        # Create a "greedy" regex pattern. The `.*` will match everything (including newlines
        # and other special tokens) between the very first special token it finds and the
        # very last one in the string.
        self.pattern = re.compile(
            '(' + '|'.join(escaped_tokens) + ')' +  # Capturing group 1: the first token
            '.*' +                                  # Greedy match for all content in between
            '(' + '|'.join(escaped_tokens) + ')',   # Capturing group 2: the last token
            re.DOTALL  # Make '.' match newlines
        )

    def filter(self, spaim_message):
        """
        Strips out all text between the first and last special tokens found.

        For example, a message containing multiple sections like <|start|>...<|end|><|start|>...<|end|>
        will have the entire block from the first <|start|> to the final <|end|> removed.

        Args:
            spaim_message (SpaimMessage or str): The message to be filtered.

        Returns:
            str: The sanitized message string.
        """
        message_str = str(spaim_message)
        # Replace the entire matched pattern with an empty string to delete it.
        return self.pattern.sub('', message_str)