//! tui.rs
//! helper module for setting up and tearing down the terminal

use std::io::{stdout, Stdout};

use color_eyre::Result;

use crossterm::{execute, terminal::*};
use ratatui::prelude::*;

/// type alias for the terminal type used in this application
pub type Tui = Terminal<CrosstermBackend<Stdout>>;

/// initialize terminal
pub fn init() -> Result<Tui> {
    execute!(stdout(), EnterAlternateScreen)?;
    enable_raw_mode()?;
    Ok(Terminal::new(CrosstermBackend::new(stdout()))?)
}

/// restore terminal to original state
pub fn restore() -> Result<()> {
    execute!(stdout(), LeaveAlternateScreen)?;
    disable_raw_mode()?;
    Ok(())
}
