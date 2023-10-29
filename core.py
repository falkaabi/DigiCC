import subprocess
import os
import time
from enum import Enum
import logging
from contextlib import contextmanager
from typing import Dict, Union, Callable


class CommandError(Exception):
    pass

# Enum for Transfer Modes
class TransferMode(Enum):
    PC = "Save_to_PC_only"
    CAMERA = "Save_to_camera_only"
    BOTH = "Save_to_PC_and_camera"

# Main Camera Class
class Camera:
    '''
    Class to control the camera using digiCamControl software
    '''
    def __init__(self, 
                 digicamcontrol_path: str = "C:\\Program Files (x86)\\digiCamControl", 
                 timeout: int = 5, 
                 AutoFocus: bool = True):
        from pathlib import Path
        self.app_path = str(Path(digicamcontrol_path) / "CameraControl.exe")
        self.remote_utility = str(Path(digicamcontrol_path) / "CameraControlRemoteCmd.exe")
        logging.basicConfig(level=logging.INFO)
        
        self.timeout = timeout
        self.callbacks = {}
        self.inLiveViewMode:bool = False
        self.AutoFocus:bool = AutoFocus

        if not os.path.exists(self.app_path):
            raise ValueError(f"Invalid CameraControl application path: {self.digicamcontrol_path}")

        if not self._is_running("CameraControl.exe"):
            self._start_app()

    def on(self, event_name: str, callback: Callable):
        """Register event callbacks."""
        self.callbacks[event_name] = callback

    def _is_running(self, process_name: str) -> bool:
        try:
            output = subprocess.check_output('tasklist', shell=True).decode()
            return process_name in output
        except subprocess.CalledProcessError:
            logging.error("Error checking running tasks.")
            return False

    def _start_app(self):
        try:
            subprocess.Popen([self.app_path])
            time.sleep(self.timeout)
        except Exception as e:
            logging.error(f"Error starting CameraControl application: {e}")

    def _execute(self, command):
        cmd = [self.remote_utility, "/c", command]
        try:
            result = subprocess.check_output(cmd).decode()
            logging.info(f"Command Execution Details:\n"
                        f"---------------------------\n"
                        f"Command: {' '.join(cmd)}\n"
                        f"Result: \n{result}"
                        f"---------------------------")
            return result
        except subprocess.CalledProcessError as e:
            logging.error(f"Error executing command: {cmd}. Error: {e}")
            return ""
            raise

    @property
    def ShutterSpeeds(self):
        return self._list("shutterspeed")

    @property
    def ShutterSpeed(self):
        return self._get("shutterspeed")

    @ShutterSpeed.setter
    def ShutterSpeed(self, value):
        self._set("shutterspeed", value)

    @property
    def ISOs(self):
        # Assume 'list iso' returns list of ISOs
        return self._list("iso")

    @property
    def ISO(self):
        return self._get("iso")

    @ISO.setter
    def ISO(self, value):
        self._set("iso", value)

    @property
    def ExposureComps(self):
        return self._list("exposurecompensation")

    @property
    def ExposureComp(self):
        return self._get("exposurecompensation")

    @ExposureComp.setter
    def ExposureComp(self, value):
        self._set("exposurecompensation", value)

    @property
    def Apertures(self):
        return self._list("aperture")

    @property
    def Aperture(self):
        return self._get("aperture")

    @Aperture.setter
    def Aperture(self, value):
        self._set("aperture", value)

    @property
    def FocusModes(self):
        return self._list("focusmode")

    @property
    def FocusMode(self):
        return self._get("focusmode")

    @FocusMode.setter
    def FocusMode(self, value):
        self._set("focusmode", value)

    @property
    def WhiteBalances(self):
        return self._list("whitebalance")

    @property
    def WhiteBalance(self):
        return self._get("whitebalance")

    @WhiteBalance.setter
    def WhiteBalance(self, value):
        self._set("whitebalance", value)

    @property
    def Modes(self):
        return self._list("mode")

    @property
    def Mode(self):
        return self._get("mode")

    @Mode.setter
    def Mode(self, value):
        self._set("mode", value)

    @property
    def Compressions(self):
        return self._list("compressionsetting")

    @property
    def Compression(self):
        return self._get("compressionsetting")

    @Compression.setter
    def Compression(self, value):
        self._set("compressionsetting", value)

    @property
    def Session(self):
        return self._get("session.name")

    @Session.setter
    def Session(self, value):
        self._set("session.name", value)

    @property
    def Folder(self):
        return self._get("session.folder")

    @Folder.setter
    def Folder(self, value):
        self._set("session.folder", value)

    @property
    def Counter(self):
        return self._get("session.counter")

    @Counter.setter
    def Counter(self, value):
        self._set("session.counter", value)

    @property
    def FileNameTemplate(self):
        return self._get("session.filenametemplate")
    
    @FileNameTemplate.setter
    def FileNameTemplate(self, value):
        """
        Set the file name template. The template can include the following placeholders:
        - [Counter x digit]: The session counter value with total length of X character filled with leading 0
        - [Camera Counter X digit]: The capture camera counter value with total length of X character filled with leading 0
        - [Session Name]: The name of the current session
        - [Capture Name]: The value can be set in main window session tab
        - [Series 4 digit]: Another value which can be set on main window, if used with focus stacking after every stack the series will be incremented automatically
        - [File format]: File format of the captured file, jpg or raw
        - [Barcode]: The barcode value scanned in Barcode window
        - [Camera Name]: The camera name set in Camera property window
        Folders can also be defined using backslash \ character. Ex: [Date yyyy-MM-dd]\[Date yyyy-MM-dd-hh-mm-ss]
        """
        self._set("session.filenametemplate", value)

    @property
    def DeleteFileAfterTransfer(self):
        return self._get("session.deletefileaftertransfer")

    @DeleteFileAfterTransfer.setter
    def DeleteFileAfterTransfer(self, value: bool):
        self._set("session.deletefileaftertransfer", value)

    @property
    def Transfer(self):
        mode = self._get("transfer")
        return TransferMode(mode.replace(' ', '_'))

    @Transfer.setter
    def Transfer(self, mode: TransferMode):
        self._set("transfer", mode.value)

    @property
    def LastCaptured(self):
        response = self._execute("get lastcaptured")
        if 'error' in response:
            error_message = response.split('message:')[1].strip('\r\n')
            logging.error(f"Error executing get lastcaptured command: {error_message}")
            return None
        value = response.split('response:')[1].strip('";\r\n')
        return value

    # Common methods to get value, set value and get list
    def _get(self, param):
        # Execute the get command and get the response
        response = self._execute(f"get {param}")
        
        # Check if the response contains an error
        if 'error' in response:
            # Extract the error message and log it
            error_message = response.split('message:')[1].strip('\r\n')
            logging.error(f"Error executing get command: {error_message}")
            return None
        
        # If there is no error, extract the value from the response
        value = response.split('response:')[1].strip('";\r\n')
        
        # Return the value
        return value

    def _set(self, param, value):
        # Execute the set command and get the response
        response = self._execute(f"set {param} {value}")
        
        # Check if the response contains an error
        if 'error' in response:
            # Extract the error message and log it
            error_message = response.split('message:')[1].strip('\r\n')
            logging.error(f"Error executing set command: {error_message}")
            return None
        
        # If there is no error, extract the value from the response
        value = response.split('response:')[1].strip('";\r\n')
        
        # Return the value
        return value

    def _list(self, param):
        # Execute the list command and get the response
        response = self._execute(f"list {param}")
        
        # Check if the response contains an error
        if 'error' in response:
            # Extract the error message and log it
            error_message = response.split('message:')[1].strip('\r\n')
            logging.error(f"Error executing list command: {error_message}")
            return []
        
        # If there is no error, extract the list from the response
        response_list = response.split('response:')[1].strip('[];\r\n').replace('"','').split(',')
        
        # Return the list
        return response_list
        
    def singleLineCommand(self, command_type:str):
        """ Not used yet ! ref:https://github.com/dukus/digiCamControl/blob/5785e2b3ec29de153ad894e3b925ddeddb4ef76e/CameraControl.Application/WebServer/browse.html#L29
        Executes a single line command based on the provided command type.
        :param command_type: The type of command to execute. Can be 'get', 'set', 'list', 'capture', or 'do'.
        """
        valid_commands = ['get', 'set', 'list', 'capture', 'do']
        if command_type not in valid_commands:
            logging.error(f"Invalid command type: {command_type}. Valid commands are {valid_commands}.")
            return None
        else:
            response = self._execute(command_type)
            return response

    def startLiveView(self):
        """
        Starts the live view mode on the camera.
        """
        self.inLiveViewMode = True
        self._execute("do LiveViewWnd_Show")
        # Minimize all windows
        self.minimizeAll()

    def stopLiveView(self):
        """
        Stops the live view mode on the camera.
        """
        self.inLiveViewMode = False
        self._execute("do LiveViewWnd_Hide")

    def focus(self):
        """
        Focuses the camera.
        Only works if the camera is in live view mode.
        """
        if self.inLiveViewMode:
            self._execute("do LiveView_Focus")
        else:
            logging.error("Error: Camera is not in live view mode. Cannot execute focus command.")
            # raise CommandError("Camera is not in live view mode. Cannot execute focus command.")

    def capture(self, location:str=None):
        """
        Captures an image. If the camera is in live view mode, it will use the live view capture command.
        If a location is provided, it will be appended to the command.
        :param location: The location where the image will be saved.
        """
        capturecmd = "Capture" if self.AutoFocus else "CaptureNoAf"
        command = "do LiveView_Capture" if self.inLiveViewMode else capturecmd
        if location:
            command += f" {location}"
        response = self._execute(command)
        if 'error' in response:
            error_message = response.split('message:')[1].strip('\r\n')
            logging.error(f"Error executing capture command: {error_message}")
            return None
        else:
            time.sleep(1)
            return self.LastCaptured

    def startRecording(self):
        """
        Starts recording video.
        If the camera is in live view mode, it will use the live view start record command.
        Some cameras may not support video recording unless in live view mode.
        """
        command = "do LiveViewWnd_StartRecord" if self.inLiveViewMode else "do StartRecord"
        response = self._execute(command)

        # extract the response from the command execution
        response_text = response.split('response:')[1].strip('";\r\n')

        # check if the response text is empty, indicating a successful command execution
        if response_text == "":
            # if the response text is empty, return True to indicate that the recording started
            return True
        else:
            # if the response text is not empty, it contains an error message
            logging.error(f"Error starting video recording: {response_text}")
            # return False to indicate that the recording did not start
            return False


    def stopRecording(self):
        """
        Stops recording video.
        If the camera is in live view mode, it will use the live view stop record command.
        """
        command = "do LiveViewWnd_StopRecord" if self.inLiveViewMode else "do StopRecord"
        self._execute(command)

    def minimizeAll(self):
        """
        Minimizes all windows.
        """
        self._execute("do All_Minimize")

    def closeAll(self):
        """
        Closes all windows and quits digiCamControl application.
        """
        self._execute("do All_Close")

    @contextmanager
    def liveView(self):
        """
        Context manager for handling the start and stop of live view mode.
        """
        self.startLiveView()
        try:
            yield
        finally:
            self.stopLiveView()

