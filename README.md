# DigiCC

DigiCC is a Python package for controlling a camera using the digiCamControl software. Please see: http://digicamcontrol.com/ for more information.

## Features

- Control camera settings such as shutter speed, ISO, exposure compensation, aperture, focus mode, white balance, mode, compression setting, session, folder, counter, file name template, delete file after transfer, and transfer.
- Check if the camera control application is running and start it if not.
- Register event callbacks (not fully implemented, to be done in the future).
- Execute commands to the camera control application.
- Start and stop live view mode.
- Focus the camera in Live View.
- Capture an image.
- Start and stop video recording.
- Minimize and close all windows.

## Usage Examples

Here are some examples of how to use the DigiCC package. Note this list is not comprehensive:

```python
from DigiCC import Camera, TransferMode

# Create a new Camera object
camera = Camera()

# Get the current shutter speed
current_shutter_speed = camera.ShutterSpeed
# Set the shutter speed
camera.ShutterSpeed = "1/200"

# Get the current ISO
current_iso = camera.ISO
# Set the ISO
camera.ISO = "100"

# Get the current aperture
current_aperture = camera.Aperture
# Set the aperture
camera.Aperture = "f/5.6"

# Get the current focus mode
current_focus_mode = camera.FocusMode

# Get the current white balance
current_white_balance = camera.WhiteBalance
# Set the white balance
camera.WhiteBalance = "Auto"

# Get the current mode
current_mode = camera.Mode

# Get the current compression setting
current_compression = camera.Compression

# List the supported compression settings from the camera
supported_compression = camera.Compressions


# Get the current session name
current_session = camera.Session
# Set the session name
camera.Session = "MySession"

# Get the current folder
current_folder = camera.Folder
# Set the folder
camera.Folder = "MyFolder"

# Get the current counter
current_counter = camera.Counter
# Set the counter
camera.Counter = 1

# Get the current file name template
current_file_name_template = camera.FileNameTemplate

# Set the delete file after transfer setting
camera.DeleteFileAfterTransfer = True
# Get the current delete file after transfer setting
current_delete_file_after_transfer = camera.DeleteFileAfterTransfer

# Set the transfer mode to PC Only
camera.Transfer = TransferMode.PC
# Get the current transfer mode
current_transfer_mode = camera.Transfer

# Start live view mode
camera.startLiveView()

# Capture an image
camera.capture()

# Start recording video
camera.startRecording()

# Stop recording video
camera.stopRecording()

# Stop live view mode
camera.stopLiveView()

# Use the context manager to handle the start and stop of live view mode
with camera.liveView():
    # Capture an image while in live view mode
    camera.capture()

```

