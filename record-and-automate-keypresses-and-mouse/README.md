Are you tired of old outdated UIs that a long overdue to be updated due to repetitively having to type and do the same mouse clicks over and over.
Try this out.

I used Ubuntu 24.04 LTS, but this should run on any OS with python installed that has a GUI and pynput installed.

Dependencies:

System:
- python3
- python3-pip
- Desktop GUI session (X11 recommended)

Python:
- pynput

Install:
sudo apt install python3 python3-pip
pip install pynput

Notes:
- Must run in a desktop GUI session (X11/Wayland)
- Scripts do not require Chrome, Selenium, or any browser driver
- Recorder creates 'events.json', playback reads from it
- Adjust SPEED in playback for faster or slower automation
- FAST_TYPING mode types normal text instantly for efficiency
