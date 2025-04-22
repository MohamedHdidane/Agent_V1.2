from mythic_container.MythicCommandBase import *

class NetstatArguments(TaskArguments):
    def __init__(self, command_line: str = None):
        super().__init__()
        self.args = []
        if command_line:
            self.load_args_from_string(command_line)

    async def parse_arguments(self):
        pass

class NetstatCommand(CommandBase):
    cmd = "netstat"
    needs_admin = False
    help_cmd = "netstat"
    description = "Show network connections"
    version = 1
    author = "@med"
    argument_class = NetstatArguments
    attributes = CommandAttributes(supported_os=[SupportedOS.Linux, SupportedOS.MacOS, SupportedOS.Windows])

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        return task

    async def process_response(self, response: AgentResponse):
        pass