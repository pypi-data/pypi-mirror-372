import json

class Tool:
    """Represents a single tool that a model can use."""
    def __init__(self, tool_name: str, tool_description: str, tool_params):
        self.name = tool_name
        self.description = tool_description
        self.parameters = {"type": "object", "properties": {}}
        for param in tool_params:
            param_name = list(param.keys())[0]
            param_type = list(param.values())[0]
            self.parameters["properties"][param_name] = {"type": param_type}

    def to_dict(self):
        """Converts the tool to a dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }

class ToolBox:
    """Manages a collection of tools available to the model."""
    def __init__(self, tools_list, include_builtin_tools=False, model_id=None):
        self.tools = tools_list if tools_list else []

        if include_builtin_tools and model_id:
            self._add_builtin_tools(model_id)

    def _add_builtin_tools(self, model_id):
        """Adds model-specific built-in tools."""
        # This check is now more robust and not case-sensitive.
        if "gpt-oss-20b" in model_id.lower():
            browser_tool = Tool(
                tool_name="browser",
                tool_description="Browse the web to find information.",
                tool_params=[{"query": "string"}]
            )
            python_interpreter = Tool(
                tool_name="python",
                tool_description="""Use this tool to execute Python code in your chain of thought. 
                The code will not be shown to the user. 
                This tool should be used for internal reasoning, but not for code that is intended to be visible to the user (e.g. when creating plots, tables, or files).
                When you send a message containing Python code to python, it will be executed in a stateful Jupyter notebook environment. 
                python will respond with the output of the execution or time out after 120.0 seconds. 
                The drive at '/mnt/data' can be used to save and persist user files. 
                Internet access for this session is Available. """,
                tool_params=[{"code": "string"}]
            )
            self.tools.extend([browser_tool, python_interpreter])
        # Add other models and their tools here
        # elif "some-other-model" in model_id.lower():
        #     ...

    def __str__(self):
        """
        Returns a JSON string representation of the tools.
        The exact format may need to be adjusted based on the target model's API.
        """
        return json.dumps([tool.to_dict() for tool in self.tools], indent=2)