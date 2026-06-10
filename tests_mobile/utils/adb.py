import re
import subprocess
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass


BOUNDS_RE = re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]")


@dataclass
class AdbDevice:
    adb_path: str
    serial: str

    def run(self, *args: str, timeout: int = 30) -> str:
        command = [self.adb_path, "-s", self.serial, *args]
        try:
            result = subprocess.run(
                command,
                check=True,
                text=True,
                capture_output=True,
                timeout=timeout,
            )
        except subprocess.CalledProcessError as exc:
            raise AssertionError(
                "ADB command failed:\n"
                f"command: {' '.join(command)}\n"
                f"exit_code: {exc.returncode}\n"
                f"stdout:\n{exc.stdout}\n"
                f"stderr:\n{exc.stderr}"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise AssertionError(
                "ADB command timed out:\n"
                f"command: {' '.join(command)}\n"
                f"timeout: {timeout}s\n"
                f"stdout:\n{exc.stdout}\n"
                f"stderr:\n{exc.stderr}"
            ) from exc
        return result.stdout

    def shell(self, *args: str, timeout: int = 30) -> str:
        return self.run("shell", *args, timeout=timeout)

    def assert_connected(self) -> None:
        command = [self.adb_path, "devices"]
        try:
            output = subprocess.run(
                command,
                check=True,
                text=True,
                capture_output=True,
                timeout=10,
            ).stdout
        except FileNotFoundError as exc:
            raise AssertionError(f"ADB binary was not found: {self.adb_path}") from exc
        except subprocess.CalledProcessError as exc:
            raise AssertionError(
                "ADB devices command failed:\n"
                f"command: {' '.join(command)}\n"
                f"exit_code: {exc.returncode}\n"
                f"stdout:\n{exc.stdout}\n"
                f"stderr:\n{exc.stderr}"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise AssertionError(
                "ADB devices command timed out:\n"
                f"command: {' '.join(command)}\n"
                "timeout: 10s\n"
                f"stdout:\n{exc.stdout}\n"
                f"stderr:\n{exc.stderr}"
            ) from exc
        expected = f"{self.serial}\tdevice"
        if expected not in output:
            raise AssertionError(f"Android emulator is not connected:\n{output}")

    def clear_app(self, package: str) -> None:
        self.shell("pm", "clear", package)

    def force_stop(self, package: str) -> None:
        self.shell("am", "force-stop", package)

    def launch_app(self, package: str, activity: str) -> None:
        component = f"{package}/{activity}"
        self.shell("am", "start", "-n", component)

    def allow_permission_dialogs(self) -> None:
        allow_texts = [
            "Allow",
            "While using the app",
            "Only this time",
            "Разрешить",
            "При использовании приложения",
        ]
        for _ in range(3):
            for text in allow_texts:
                nodes = [
                    node
                    for node in self.find_nodes_by_text(text)
                    if (
                        node.attrib.get("text") == text
                        or node.attrib.get("content-desc") == text
                    )
                    and node.attrib.get("clickable") == "true"
                ]
                if nodes:
                    self.tap_node(nodes[0])
                    self.wait(seconds=1)
                    break
            else:
                return

    def wait(self, seconds: float = 1) -> None:
        time.sleep(seconds)

    def dump_ui_xml(self) -> str:
        last_output = ""
        for _ in range(5):
            output = self.run("exec-out", "uiautomator", "dump", "/dev/tty", timeout=20)
            start = output.find("<?xml")
            end = output.rfind("</hierarchy>")
            if start != -1 and end != -1:
                return output[start : end + len("</hierarchy>")]
            last_output = output
            self.wait(seconds=0.5)
        raise AssertionError(f"Could not read UI hierarchy:\n{last_output}")

    def dump_ui(self) -> ET.Element:
        return ET.fromstring(self.dump_ui_xml())

    def all_nodes(self):
        return list(self.dump_ui().iter("node"))

    def find_nodes_by_class(self, class_name: str):
        return [
            node
            for node in self.all_nodes()
            if node.attrib.get("class") == class_name
        ]

    def find_nodes_by_text(self, text: str):
        matches = []
        for node in self.all_nodes():
            node_text = node.attrib.get("text") or ""
            content_desc = node.attrib.get("content-desc") or ""
            if text in node_text or text in content_desc:
                matches.append(node)
        return matches

    def wait_for_text(self, text: str, timeout: float = 10, interval: float = 0.5):
        deadline = time.time() + timeout
        last_seen = ""
        while time.time() < deadline:
            nodes = self.find_nodes_by_text(text)
            if nodes:
                return nodes[0]
            last_seen = self.dump_ui_xml()
            time.sleep(interval)
        raise AssertionError(f"Text not found in mobile UI: {text}\n\nLast UI:\n{last_seen}")

    def wait_for_any_text(
        self, texts: list[str], timeout: float = 10, interval: float = 0.5
    ):
        deadline = time.time() + timeout
        last_seen = ""
        while time.time() < deadline:
            for text in texts:
                nodes = self.find_nodes_by_text(text)
                if nodes:
                    return nodes[0]
            last_seen = self.dump_ui_xml()
            time.sleep(interval)
        raise AssertionError(
            f"None of these texts were found in mobile UI: {texts}\n\nLast UI:\n{last_seen}"
        )

    def tap_text(self, text: str) -> None:
        node = self.wait_for_text(text)
        self.tap_node(node)

    def tap_first_visible_text(self, texts: list[str], timeout: float = 5) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            for text in texts:
                nodes = self.find_nodes_by_text(text)
                clickable_nodes = [
                    node
                    for node in nodes
                    if node.attrib.get("clickable") == "true"
                ]
                if clickable_nodes:
                    self.tap_node(clickable_nodes[0])
                    return
                if nodes:
                    self.tap_node(nodes[0])
                    return
            time.sleep(0.5)
        raise AssertionError(f"None of these texts were visible: {texts}")

    def tap_node(self, node: ET.Element) -> None:
        x, y = self.node_center(node)
        self.tap(x, y)

    def tap(self, x: int, y: int) -> None:
        self.shell("input", "tap", str(x), str(y))

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 500) -> None:
        self.shell(
            "input",
            "swipe",
            str(x1),
            str(y1),
            str(x2),
            str(y2),
            str(duration_ms),
        )

    def scroll_until_text(self, text: str, max_swipes: int = 5):
        for _ in range(max_swipes + 1):
            nodes = self.find_nodes_by_text(text)
            visible_nodes = [
                node
                for node in nodes
                if self.node_center(node)[1] < 2115
            ]
            if visible_nodes:
                return visible_nodes[0]
            self.swipe(540, 1900, 540, 900)
            self.wait(seconds=0.7)
        raise AssertionError(f"Text not found after scrolling: {text}")

    def text(self, value: str) -> None:
        self.shell("input", "text", self._escape_text(value))

    @staticmethod
    def node_center(node: ET.Element) -> tuple[int, int]:
        bounds = node.attrib.get("bounds", "")
        match = BOUNDS_RE.match(bounds)
        if not match:
            raise AssertionError(f"Node has invalid bounds: {bounds}")
        x1, y1, x2, y2 = map(int, match.groups())
        return (x1 + x2) // 2, (y1 + y2) // 2

    @staticmethod
    def _escape_text(value: str) -> str:
        return value.replace(" ", "%s")
