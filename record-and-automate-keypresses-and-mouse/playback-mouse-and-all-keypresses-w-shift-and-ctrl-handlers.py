import time
import json
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyController, Key

# =========================
# Configuration
# =========================
EVENTS_FILE = 'events.json'  # recorded events
SPEED = 3.0                  # 1.0 = normal speed, >1 faster, <1 slower
FAST_TYPING = True            # type normal text instantly instead of key-by-key
START_DELAY = 3               # seconds before playback starts

# =========================
# Load recorded events
# =========================
with open(EVENTS_FILE) as f:
    events = json.load(f)

mouse = MouseController()
keyboard = KeyController()

# Mapping from string names to pynput Keys (special keys)
special_keys = {
    'esc': Key.esc,
    'enter': Key.enter,
    'tab': Key.tab,
    'backspace': Key.backspace,
    'space': Key.space,
    'shift': Key.shift,
    'ctrl': Key.ctrl,
    'alt': Key.alt,
    'left': Key.left,
    'right': Key.right,
    'up': Key.up,
    'down': Key.down,
    # Add more special keys if your UI uses them
}

# =========================
# Playback
# =========================
print(f"▶️ Playback starting in {START_DELAY} seconds...")
time.sleep(START_DELAY)

prev_time = 0

for e in events:
    # Calculate per-event delay and apply speed multiplier
    delay = max((e['time'] - prev_time) / SPEED, 0)
    time.sleep(delay)
    prev_time = e['time']

    # --- Mouse events ---
    if e['type'] == 'mouse_move':
        mouse.position = (e['x'], e['y'])
    elif e['type'] == 'mouse_click':
        btn = Button.left if e['button'] == 'left' else Button.right
        if e['pressed']:
            mouse.press(btn)
        else:
            mouse.release(btn)
    elif e['type'] == 'mouse_scroll':
        mouse.scroll(e['dx'], e['dy'])

    # --- Keyboard events ---
    elif e['type'] == 'key_press':
        parts = e['key'].split('+')
        mods = [p for p in parts[:-1]]  # modifier keys
        key_name = parts[-1]

        # Fast typing for normal single characters without modifiers
        if FAST_TYPING and not mods and len(key_name) == 1:
            keyboard.type(key_name)
            continue

        # Press modifiers
        for m in mods:
            if m.lower() == 'ctrl':
                keyboard.press(Key.ctrl)
            elif m.lower() == 'shift':
                keyboard.press(Key.shift)

        # Press and release main key
        k = special_keys.get(key_name, key_name)
        keyboard.press(k)
        keyboard.release(k)

        # Release modifiers
        for m in mods:
            if m.lower() == 'ctrl':
                keyboard.release(Key.ctrl)
            elif m.lower() == 'shift':
                keyboard.release(Key.shift)

print("✅ Playback complete.")
