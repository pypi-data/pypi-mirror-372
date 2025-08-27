from spaim.prompt import Prompt
from spaim.injection import PromptInjection

class SpaimMessage:
    """
    Combines a benign prompt and a prompt injection into a single message sequence.

    This class simulates a scenario where an injection attempt follows a
    legitimate prompt, potentially over multiple conversational turns.
    """
    def __init__(self, prompt: Prompt | str, injection: PromptInjection | str, num_turns: int = 1):
        """
        Initializes the SpaimMessage.

        Args:
            prompt (Prompt): The initial, benign prompt.
            injection (PromptInjection): The injection to be appended.
            num_turns (int, optional): The number of times to append the injection. Defaults to 1.
        """
        self.prompt = prompt
        self.injection = injection
        self.num_turns = num_turns

    def __str__(self):
        """
        Constructs the final message string.

        Returns:
            str: The combined and formatted string of the prompt and repeated injection.
        """
        # Get the string representation from the prompt object
        base_prompt_str = str(self.prompt)

        # Get the string representation from the injection object
        injection_str = str(self.injection)

        # Combine the base prompt with the injection repeated num_turns times
        final_message = base_prompt_str
        for _ in range(self.num_turns):
            # A separator might be needed depending on the chat template,
            # but apply_chat_template usually handles this.
            final_message += injection_str

        return final_message
