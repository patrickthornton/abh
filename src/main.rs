//! main.rs
//! runs the program

use color_eyre::Result;

mod app;
mod errors;
mod tui;
mod ui;
use crate::app::App;

/// run the app!
fn main() -> Result<()> {
    errors::install_hooks()?;
    let mut terminal = tui::init()?;
    let app_result = App::default().run(&mut terminal);
    tui::restore()?;
    app_result
}
