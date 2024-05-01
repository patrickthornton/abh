//! ui.rs
//! handles the draw to the terminal every frame

use ratatui::{
    prelude::*,
    widgets::{block::*, *},
};

use crate::app::App;

/// renders a single frame 'f' of app 'app'
pub fn ui(f: &mut Frame, _app: &App) {
    let layout = Layout::new(
        Direction::Vertical,
        vec![Constraint::Min(0), Constraint::Length(3)],
    );
    let chunks = layout.split(f.size());

    let par = Paragraph::new("demo")
        .block(
            Block::default()
                .borders(Borders::ALL)
                .border_type(BorderType::Rounded),
        )
        .wrap(Wrap { trim: true });
    f.render_widget(par, chunks[0]);

    let status_bar = Block::default()
        .title("status")
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded);
    f.render_widget(status_bar, chunks[1]);
}
