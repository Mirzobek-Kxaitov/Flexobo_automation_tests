import os

import pytest
from dotenv import load_dotenv

from tests_mobile.utils.adb import AdbDevice

load_dotenv()


APP_PACKAGE = os.getenv("MOBILE_APP_PACKAGE", "uz.globalmove.flexobo")
APP_ACTIVITY = os.getenv("MOBILE_APP_ACTIVITY", ".MainActivity")
ADB_PATH = os.getenv(
    "ADB_PATH",
    "/Users/mirzobek/Library/Android/sdk/platform-tools/adb",
)
ANDROID_SERIAL = os.getenv("ANDROID_SERIAL", "emulator-5554")
MOBILE_REQUIRE_DEVICE = os.getenv("MOBILE_REQUIRE_DEVICE", "").lower() in {
    "1",
    "true",
    "yes",
}


@pytest.fixture(scope="session")
def mobile_device():
    device = AdbDevice(adb_path=ADB_PATH, serial=ANDROID_SERIAL)
    try:
        device.assert_connected()
    except AssertionError as exc:
        if MOBILE_REQUIRE_DEVICE:
            raise
        pytest.skip(str(exc))
    return device


@pytest.fixture
def fresh_mobile_app(mobile_device):
    mobile_device.force_stop(APP_PACKAGE)
    mobile_device.clear_app(APP_PACKAGE)
    mobile_device.launch_app(APP_PACKAGE, APP_ACTIVITY)
    mobile_device.wait(seconds=2)
    mobile_device.allow_permission_dialogs()
    try:
        yield mobile_device
    finally:
        try:
            mobile_device.force_stop(APP_PACKAGE)
        except AssertionError:
            pass
