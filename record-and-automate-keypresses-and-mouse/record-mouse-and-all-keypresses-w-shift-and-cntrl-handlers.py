import time
import json
from pynput import mouse, keyboard

EVENTS_FILE = 'events.json'
events = []
start_time = None

# Modifier state
ctrl_pressed = False
shift_pressed = False


def record_delay():
    return round(time.time() - start_time, 4)


# =========================
# Mouse Event Handlers
# =========================
def on_click(x, y, button, pressed):
    events.append({
        'type': 'mouse_click',
        'time': record_delay(),
        'x': x,
        'y': y,
        'button': button.name,
        'pressed': pressed
    })

    # Stop recording on right-click release
    if not pressed and button == mouse.Button.right:
        return False


def on_move(x, y):
    events.append({
        'type': 'mouse_move',
        'time': record_delay(),
        'x': x,
        'y': y
    })


def on_scroll(x, y, dx, dy):
    events.append({
        'type': 'mouse_scroll',
        'time': record_delay(),
        'x': x,
        'y': y,
        'dx': dx,
        'dy': dy
    })


# =========================
# Keyboard Event Handlers
# =========================
def on_press(key):
    global ctrl_pressed, shift_pressed

    # ESC = stop recording (do NOT record it)
    if key == keyboard.Key.esc:
        return False

    # Modifier tracking
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        ctrl_pressed = True
        return

    if key in (keyboard.Key.shift, keyboard.Key.shift_r):
        shift_pressed = True
        return

    # Determine key name
    try:
        key_name = key.char  # already includes Shift for characters
    except AttributeError:
        key_name = str(key).replace('Key.', '')

    key_name = key_name.lower()

    # Build modifier list
    modifiers = []
    if ctrl_pressed:
        modifiers.append("Ctrl")
    if shift_pressed:
        modifiers.append("Shift")

    recorded_key = (
        '+'.join(modifiers + [key_name])
        if modifiers else key_name
    )

    events.append({
        'type': 'key_press',
        'time': record_delay(),
        'key': recorded_key
    })


def on_release(key):
    global ctrl_pressed, shift_pressed

    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        ctrl_pressed = False

    if key in (keyboard.Key.shift, keyboard.Key.shift_r):
        shift_pressed = False


# =========================
# Recording Controller
# =========================
def record():
    global start_time
    print("🎙️ Recording started. Press ESC or right-click to stop...")
    start_time = time.time()

    with mouse.Listener(
        on_click=on_click,
        on_move=on_move,
        on_scroll=on_scroll
    ) as m_listener, keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    ) as k_listener:
        m_listener.join()
        k_listener.join()

    with open(EVENTS_FILE, 'w') as f:
        json.dump(events, f, indent=2)

    print(f"✅ Recording complete. Events saved to '{EVENTS_FILE}'.")


if __name__ == '__main__':
    record()
