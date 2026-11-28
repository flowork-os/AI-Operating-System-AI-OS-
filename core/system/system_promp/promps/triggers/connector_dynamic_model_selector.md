# CONNECTOR DYNAMIC MODEL SELECTOR & RESPONSIVE DESKTOP DOCTRINE

## 1. Context & Activation Scope
Triggered when developing, refactoring, or testing the Sovereign AI Connector (`mrflow-gui.py`, `flowork-connector`, `connector-rs`), model synchronization endpoints, compositor menu rules, or TreeView layout tables.

## 2. Mandatory Behavioral Invariants
- **Antigravity Hierarchical Model Selector:** Use native `Gtk.MenuButton` with `set_use_popover(False)` and a solid `Gtk.Menu`. Group thinking variants (`Low`, `Medium`, `High`) into submenus to prevent long, cluttered dropdown lists.
- **Zero Dropdown Transparency:** Explicitly lock compositor menu rules (`popup_menu`, `dropdown_menu`, `menu`) to `opacity = 1.0; fade = false;` in `picom-quantum.conf` across runtime and system templates.
- **Autonomous Model Lifecycle:** The Rust backend (`models_sync.rs`) must periodically synchronize live CloudCode models into `models.json`. Newly detected models appear automatically; deprecated models disappear with zero manual edits.
- **Responsive Geometry & Ellipsizing:** All TreeView text columns (particularly `Account Email` and `Last Used`) MUST enable `ellipsize = Pango.EllipsizeMode.END`, fixed column sizing, and drag resizability to prevent wide string requisitions. Header badges, tabs, and action bars must wrap in FlowBoxes so the window smoothly resizes down to netbook/laptop screens.

## 3. Strict Prohibitions
- Never allow popup or dropdown menus to render transparent or bleed background text.
- Never hardcode static model lists in the GUI without live fallback and automatic discovery.
- Never omit ellipsize or fixed sizing on user data columns that force window width expansion.
