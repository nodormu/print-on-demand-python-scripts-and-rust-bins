use rdev::{simulate, Button, EventType, Key};
use serde::Deserialize;
use std::fs::File;
use std::io::BufReader;
use std::thread;
use std::time::{Duration, Instant};

#[derive(Deserialize, Debug)]
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

// Convert recorded button name to rdev Button
fn button_from_name(name: &str) -> Option<Button> {
    match name {
        "left" => Some(Button::Left),
        "right" => Some(Button::Right),
        "middle" => Some(Button::Middle),
        _ => None,
    }
}

// Map character to rdev key + shift flag
// Map a single character to rdev::Key + Shift flag
fn char_to_key_shift(c: &str) -> Option<(Key, bool)> {
    match c {
        // Lowercase letters
        "a" => Some((Key::KeyA, false)), "b" => Some((Key::KeyB, false)),
        "c" => Some((Key::KeyC, false)), "d" => Some((Key::KeyD, false)),
        "e" => Some((Key::KeyE, false)), "f" => Some((Key::KeyF, false)),
        "g" => Some((Key::KeyG, false)), "h" => Some((Key::KeyH, false)),
        "i" => Some((Key::KeyI, false)), "j" => Some((Key::KeyJ, false)),
        "k" => Some((Key::KeyK, false)), "l" => Some((Key::KeyL, false)),
        "m" => Some((Key::KeyM, false)), "n" => Some((Key::KeyN, false)),
        "o" => Some((Key::KeyO, false)), "p" => Some((Key::KeyP, false)),
        "q" => Some((Key::KeyQ, false)), "r" => Some((Key::KeyR, false)),
        "s" => Some((Key::KeyS, false)), "t" => Some((Key::KeyT, false)),
        "u" => Some((Key::KeyU, false)), "v" => Some((Key::KeyV, false)),
        "w" => Some((Key::KeyW, false)), "x" => Some((Key::KeyX, false)),
        "y" => Some((Key::KeyY, false)), "z" => Some((Key::KeyZ, false)),

        // Uppercase letters (Shift needed)
        "A" => Some((Key::KeyA, true)), "B" => Some((Key::KeyB, true)),
        "C" => Some((Key::KeyC, true)), "D" => Some((Key::KeyD, true)),
        "E" => Some((Key::KeyE, true)), "F" => Some((Key::KeyF, true)),
        "G" => Some((Key::KeyG, true)), "H" => Some((Key::KeyH, true)),
        "I" => Some((Key::KeyI, true)), "J" => Some((Key::KeyJ, true)),
        "K" => Some((Key::KeyK, true)), "L" => Some((Key::KeyL, true)),
        "M" => Some((Key::KeyM, true)), "N" => Some((Key::KeyN, true)),
        "O" => Some((Key::KeyO, true)), "P" => Some((Key::KeyP, true)),
        "Q" => Some((Key::KeyQ, true)), "R" => Some((Key::KeyR, true)),
        "S" => Some((Key::KeyS, true)), "T" => Some((Key::KeyT, true)),
        "U" => Some((Key::KeyU, true)), "V" => Some((Key::KeyV, true)),
        "W" => Some((Key::KeyW, true)), "X" => Some((Key::KeyX, true)),
        "Y" => Some((Key::KeyY, true)), "Z" => Some((Key::KeyZ, true)),

        // Numbers
        "0" => Some((Key::Num0, false)), "1" => Some((Key::Num1, false)),
        "2" => Some((Key::Num2, false)), "3" => Some((Key::Num3, false)),
        "4" => Some((Key::Num4, false)), "5" => Some((Key::Num5, false)),
        "6" => Some((Key::Num6, false)), "7" => Some((Key::Num7, false)),
        "8" => Some((Key::Num8, false)), "9" => Some((Key::Num9, false)),

        // Shifted symbols above numbers
        "!" => Some((Key::Num1, true)), "@" => Some((Key::Num2, true)),
        "#" => Some((Key::Num3, true)), "$" => Some((Key::Num4, true)),
        "%" => Some((Key::Num5, true)), "^" => Some((Key::Num6, true)),
        "&" => Some((Key::Num7, true)), "*" => Some((Key::Num8, true)),
        "(" => Some((Key::Num9, true)), ")" => Some((Key::Num0, true)),

        // Common punctuation
        " " => Some((Key::Space, false)), "\n" => Some((Key::Return, false)),
        "-" => Some((Key::Minus, false)), "_" => Some((Key::Minus, true)),
        "=" => Some((Key::Equal, false)), "+" => Some((Key::Equal, true)),
        "[" => Some((Key::LeftBracket, false)), "{" => Some((Key::LeftBracket, true)),
        "]" => Some((Key::RightBracket, false)), "}" => Some((Key::RightBracket, true)),
        "\\" => Some((Key::BackSlash, false)), "|" => Some((Key::BackSlash, true)),
        ";" => Some((Key::SemiColon, false)), ":" => Some((Key::SemiColon, true)),
        "'" => Some((Key::Quote, false)), "\"" => Some((Key::Quote, true)),
        "," => Some((Key::Comma, false)), "<" => Some((Key::Comma, true)),
        "." => Some((Key::Dot, false)), ">" => Some((Key::Dot, true)),
        "/" => Some((Key::Slash, false)), "?" => Some((Key::Slash, true)),
        "`" => Some((Key::BackQuote, false)), "~" => Some((Key::BackQuote, true)),

        _ => None, // Anything unsupported
    }
}

fn main() {
    let file = File::open("events.json").expect("Failed to open events.json");
    let reader = BufReader::new(file);
    let events: Vec<RecordedEvent> = serde_json::from_reader(reader).expect("Failed to parse JSON");

    println!("▶️ Playback started...");

    let start_time = Instant::now();

    for event in events {
        // Wait until correct time
        let elapsed = start_time.elapsed().as_secs_f64();
        if event.time > elapsed {
            thread::sleep(Duration::from_secs_f64(event.time - elapsed));
        }

        match event.event_type.as_str() {
            "mouse_move" => {
                if let (Some(x), Some(y)) = (event.x, event.y) {
                    simulate(&EventType::MouseMove { x, y }).unwrap();
                }
            }
            "mouse_click" => {
                if let (Some(button_name), Some(pressed)) = (&event.button, event.pressed) {
                    if let Some(btn) = button_from_name(button_name) {
                        let evt = if pressed { EventType::ButtonPress(btn) } else { EventType::ButtonRelease(btn) };
                        simulate(&evt).unwrap();
                    }
                }
            }
            "mouse_scroll" => {
                if let (Some(dx), Some(dy)) = (event.dx, event.dy) {
                    simulate(&EventType::Wheel { delta_x: dx as i64, delta_y: dy as i64 }).unwrap();
                }
            }

            "text" => {
                if let Some(text) = &event.key {
                    if let Some((key, shift)) = char_to_key_shift(text) {
                        // Press Shift if needed
                        if shift {
                            simulate(&EventType::KeyPress(Key::ShiftLeft)).unwrap();
                        }

                        simulate(&EventType::KeyPress(key)).unwrap();
                        simulate(&EventType::KeyRelease(key)).unwrap();

                        if shift {
                            simulate(&EventType::KeyRelease(Key::ShiftLeft)).unwrap();
                        }
                    } else {
                        // fallback for unsupported characters
                        print!("{}", text);
                    }
                }
            }
            _ => {}
        }
    }

    println!("✅ Playback finished.");
}
