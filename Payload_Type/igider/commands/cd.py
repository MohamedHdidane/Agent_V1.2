from mythic_container.MythicCommandBase import *

class CdArguments(TaskArguments):
    def __init__(self, command_line: str = None):
        super().__init__()
        self.args = []
        self.add_arg(
            "args",
            CommandParameter(
                name="args",
                type=ParameterType.String,
                description="Directory to change to",
                default_value="",
                parameter_group_info=[ParameterGroupInfo(ui_position=1)]
            )
        )
        if command_line:
            self.load_args_from_string(command_line)

    async def parse_arguments(self):
        pass

class CdCommand(CommandBase):
    cmd = "cd"
    needs_admin = False
    help_cmd = "cd [directory]"
    description = "Change current directory"
    version = 1
    author = "@med"
    argument_class = CdArguments
    attributes = CommandAttributes(supported_os=[SupportedOS.Linux, SupportedOS.MacOS, SupportedOS.Windows])

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        return task

    async def process_response(self, response: AgentResponse):
        pass