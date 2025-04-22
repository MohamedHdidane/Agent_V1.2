from mythic_container.MythicCommandBase import *
import json

class ExitArguments(TaskArguments):
    def __init__(self,command_line: str = None):
        super().__init__()
        self.args = []
        if command_line:
            self.load_args_from_string(command_line)
    async def parse_arguments(self):
        pass

class ExitCommand(CommandBase):
    cmd = "exit"
    needs_admin = False
    help_cmd = "exit"
    description = "Terminate the agent"
    version = 1
    author = "you"
    argument_class = ExitArguments
    attackmapping = []

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        return task

    async def process_response(self, response: AgentResponse):
        pass