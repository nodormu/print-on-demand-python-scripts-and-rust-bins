use rdev::{listen, Event, EventType, Button, Key};
use serde::Serialize;
use std::fs::File;
use std::sync::{Arc, Mutex};
use std::time::Instant;

#[derive(Serialize, Debug)]
struct RecordedEvent {
    event_type: String,
    time: f64,
    x: Option<f64>,
    y: Option<f64>,
    dx: Option<f64>,
    dy: Option<f64>,
    button: Option<String>,
    pressed: Option<bool>,
    key: Option<String>,
}

// Map rdev Key + shift to actual character
fn key_to_char(key: Key, shift: bool) -> Option<String> {
    let c = match key {
        Key::KeyA => if shift { "A" } else { "a" },
        Key::KeyB => if shift { "B" } else { "b" },
        Key::KeyC => if shift { "C" } else { "c" },
        Key::KeyD => if shift { "D" } else { "d" },
        Key::KeyE => if shift { "E" } else { "e" },
        Key::KeyF => if shift { "F" } else { "f" },
        Key::KeyG => if shift { "G" } else { "g" },
        Key::KeyH => if shift { "H" } else { "h" },
        Key::KeyI => if shift { "I" } else { "i" },
        Key::KeyJ => if shift { "J" } else { "j" },
        Key::KeyK => if shift { "K" } else { "k" },
        Key::KeyL => if shift { "L" } else { "l" },
        Key::KeyM => if shift { "M" } else { "m" },
        Key::KeyN => if shift { "N" } else { "n" },
        Key::KeyO => if shift { "O" } else { "o" },
        Key::KeyP => if shift { "P" } else { "p" },
        Key::KeyQ => if shift { "Q" } else { "q" },
        Key::KeyR => if shift { "R" } else { "r" },
        Key::KeyS => if shift { "S" } else { "s" },
        Key::KeyT => if shift { "T" } else { "t" },
        Key::KeyU => if shift { "U" } else { "u" },
        Key::KeyV => if shift { "V" } else { "v" },
        Key::KeyW => if shift { "W" } else { "w" },
        Key::KeyX => if shift { "X" } else { "x" },
        Key::KeyY => if shift { "Y" } else { "y" },
        Key::KeyZ => if shift { "Z" } else { "z" },

        Key::Num1 => if shift { "!" } else { "1" },
        Key::Num2 => if shift { "@" } else { "2" },
        Key::Num3 => if shift { "#" } else { "3" },
        Key::Num4 => if shift { "$" } else { "4" },
        Key::Num5 => if shift { "%" } else { "5" },
        Key::Num6 => if shift { "^" } else { "6" },
        Key::Num7 => if shift { "&" } else { "7" },
        Key::Num8 => if shift { "*" } else { "8" },
        Key::Num9 => if shift { "(" } else { "9" },
        Key::Num0 => if shift { ")" } else { "0" },

        Key::Space => " ".into(),
        Key::Return => "\n".into(),
        Key::Tab => "\t".into(),
        Key::Backspace => "<Backspace>".into(),

        _ => return None,
    };
    Some(c.into())
}

fn main() {
    let events = Arc::new(Mutex::new(Vec::<RecordedEvent>::new()));
    let start_time = Instant::now();

    // Track modifiers
    let ctrl_pressed = Arc::new(Mutex::new(false));
    let shift_pressed = Arc::new(Mutex::new(false));
    let alt_pressed = Arc::new(Mutex::new(false));
    let meta_pressed = Arc::new(Mutex::new(false));
    let last_pos = Arc::new(Mutex::new((0.0, 0.0)));

    println!("🎙️ Recording started. Press ESC or right-click to stop...");

    let events_clone = events.clone();
    let ctrl_clone = ctrl_pressed.clone();
    let shift_clone = shift_pressed.clone();
    let alt_clone = alt_pressed.clone();
    let meta_clone = meta_pressed.clone();
    let last_pos_clone = last_pos.clone();

    let callback = move |event: Event| {
        let mut events = events_clone.lock().unwrap();
        let mut ctrl = ctrl_clone.lock().unwrap();
        let mut shift = shift_clone.lock().unwrap();
        let mut alt = alt_clone.lock().unwrap();
        let mut meta = meta_clone.lock().unwrap();
        let mut last_pos = last_pos_clone.lock().unwrap();

        let elapsed = start_time.elapsed().as_secs_f64();

        match event.event_type {
            EventType::KeyPress(key) => {
                if key == Key::Escape {
                    let file = File::create("events.json").unwrap();
                    serde_json::to_writer_pretty(file, &*events).unwrap();
                    println!("✅ Recording complete. Events saved to 'events.json'.");
                    std::process::exit(0);
                }

                // Track modifiers
                match key {
                    Key::ShiftLeft | Key::ShiftRight => { *shift = true; return; }
                    Key::ControlLeft | Key::ControlRight => { *ctrl = true; return; }
                    Key::Alt => { *alt = true; return; }
                    Key::MetaLeft | Key::MetaRight => { *meta = true; return; }
                    _ => {}
                }

                if let Some(text) = key_to_char(key, *shift) {
                    let mut recorded_key = text;
                    let mut mods = Vec::new();
                    if *ctrl { mods.push("Ctrl"); }
                    if *alt { mods.push("Alt"); }
                    if *meta { mods.push("Meta"); }
                    if !mods.is_empty() {
                        recorded_key = mods.join("+") + "+" + &recorded_key;
                    }

                    events.push(RecordedEvent {
                        event_type: "text".into(),
                        time: elapsed,
                        x: None,
                        y: None,
                        dx: None,
                        dy: None,
                        button: None,
                        pressed: None,
                        key: Some(recorded_key),
                    });
                }
            }

            EventType::KeyRelease(key) => {
                match key {
                    Key::ShiftLeft | Key::ShiftRight => *shift = false,
                    Key::ControlLeft | Key::ControlRight => *ctrl = false,
                    Key::Alt => *alt = false,
                    Key::MetaLeft | Key::MetaRight => *meta = false,
                    _ => {}
                }
            }

            EventType::ButtonPress(btn) | EventType::ButtonRelease(btn) => {
                let pressed = matches!(event.event_type, EventType::ButtonPress(_));
                let button_name = match btn {
                    Button::Left => "left",
                    Button::Right => "right",
                    Button::Middle => "middle",
                    _ => "unknown",
                }.to_string();

                events.push(RecordedEvent {
                    event_type: "mouse_click".into(),
                    time: elapsed,
                    x: Some(last_pos.0),
                    y: Some(last_pos.1),
                    dx: None,
                    dy: None,
                    button: Some(button_name.clone()),
                    pressed: Some(pressed),
                    key: None,
                });

                if button_name == "right" && !pressed {
                    let file = File::create("events.json").unwrap();
                    serde_json::to_writer_pretty(file, &*events).unwrap();
                    println!("✅ Recording complete. Events saved to 'events.json'.");
                    std::process::exit(0);
                }
            }

            EventType::MouseMove { x, y } => {
                *last_pos = (x, y);
                events.push(RecordedEvent {
                    event_type: "mouse_move".into(),
                    time: elapsed,
                    x: Some(x),
                    y: Some(y),
                    dx: None,
                    dy: None,
                    button: None,
                    pressed: None,
                    key: None,
                });
            }

            EventType::Wheel { delta_x, delta_y } => {
                events.push(RecordedEvent {
                    event_type: "mouse_scroll".into(),
                    time: elapsed,
                    x: Some(last_pos.0),
                    y: Some(last_pos.1),
                    dx: Some(delta_x as f64),
                    dy: Some(delta_y as f64),
                    button: None,
                    pressed: None,
                    key: None,
                });
            }
        }
    };

    if let Err(error) = listen(callback) {
        eprintln!("Error: {:?}", error);
    }
}
