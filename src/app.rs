//! app.rs
//! handles the main functionality of the application, including user inputs

use color_eyre::eyre::Context;
use color_eyre::Result;

use crossterm::event::{self, Event, KeyCode, KeyEvent, KeyEventKind};

use crate::tui::Tui;
use crate::ui::ui;

/// application state
#[derive(Debug, Default)]
pub struct App {
    exit: bool,
}

impl App {
    /// main application loop;
    /// draws to terminal, then handles events
    pub fn run(&mut self, terminal: &mut Tui) -> Result<()> {
        while !self.exit {
            terminal.draw(|f| ui(f, self))?;
            self.handle_events().wrap_err("failed to handle event")?;
        }
        Ok(())
    }

    /// event handler
    fn handle_events(&mut self) -> Result<()> {
        match event::read()? {
            Event::Key(key_event) if key_event.kind == KeyEventKind::Press => self
                .handle_key_event(key_event)
                .wrap_err(format!("failed to handle key event: {:?}", key_event)),
            _ => Ok(()),
        }
    }

    /// keypress handler
    fn handle_key_event(&mut self, key_event: KeyEvent) -> Result<()> {
        match key_event.code {
            KeyCode::Char('q') => self.exit(),
            _ => {}
        }
        Ok(())
    }

    // specific keypress handlers
    /// exits program
    fn exit(&mut self) {
        self.exit = true;
    }
}
