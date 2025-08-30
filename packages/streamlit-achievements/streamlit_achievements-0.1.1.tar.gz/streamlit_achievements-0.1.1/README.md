# 🏆 Streamlit Achievements

[![PyPI version](https://badge.fury.io/py/streamlit-achievements.svg)](https://badge.fury.io/py/streamlit-achievements)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.0+-red.svg)](https://streamlit.io)

A modern, customizable achievement notification component for Streamlit applications. Add beautiful animated achievement unlocks to your apps with customizable styling and behavior.

![Demo](https://via.placeholder.com/800x400/1f1f1f/ffffff?text=Streamlit+Achievements+Demo)

## ✨ Features

- **Beautiful Animations**: Smooth achievement animations
- **Floating Mode**: Display achievements as floating overlays above content
- **Customizable Styling**: Full control over colors, shadows, and appearance
- **Flexible Positioning**: Top, middle, bottom, or custom pixel positioning
- **Timing Controls**: Configure display duration and fade effects
- **Easy Integration**: One-line integration with your Streamlit apps
- **Icon Support**: Use emojis, text, or custom icons in achievements

## 📦 Installation

```bash
pip install streamlit-achievements
```

## 🚀 Quick Start

```python
import streamlit as st
from streamlit_achievements import streamlit_achievements

streamlit_achievements(
    title="Level Complete!",
    description="You finished Level 1",
    points=100,
    icon_text="🎯"
)

streamlit_achievements(
    title="Master Player",
    description="Reached 1000 Points",
    points=1000,
    icon_text="👑",
    floating=True,
    position="middle",
    background_color="#FFD700",
    icon_background_color="#FFA500"
)
```

## 📋 API Reference

### `streamlit_achievements()`

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `title` | `str` | The main title displayed on the achievement | `""` |
| `description` | `str` | The achievement description/name | `""` |
| `points` | `int` | Point value for the achievement | `0` |
| `icon_text` | `str` | Text or emoji displayed in the circular icon | `""` |
| `duration` | `int` | Duration in milliseconds for the animation | `6500` |
| `icon_background_color` | `str` | Color for the circular icon background | `"#8BC34A"` |
| `background_color` | `str` | Color for the expanding background | `"#2E7D32"` |
| `text_color` | `str` | Color for text and icon content | `"#FFFFFF"` |
| `shadow_color` | `str` | Color for shadows and depth effects | `"rgba(0,0,0,0.3)"` |
| `auto_width` | `bool` | Whether to auto-fit width to container | `True` |
| `floating` | `bool` | Whether to display as floating overlay above content | `False` |
| `position` | `str` | Vertical position when floating: 'top', 'middle', 'bottom', or pixel value like '100px' | `"top"` |
| `dissolve` | `int` | Time in milliseconds to start disappearing; if 0/omitted, it disappears ~3s after the background fully fills | `0` |
## 🎨 Styling Examples

### Classic Achievement
```python
streamlit_achievements(
    title="Achievement Unlocked!",
    description="First Steps",
    points=10,
    icon_text="🏆",
    icon_background_color="#8BC34A",
    background_color="#2E7D32",
    text_color="#FFFFFF"
)
```

### Floating Achievement with Custom Position
```python
streamlit_achievements(
    title="Floating Success!",
    description="You mastered floating mode!",
    points=75,
    icon_text="🚀",
    floating=True,
    position="100px",  # Custom position from top
    duration=6500,
    dissolve=5300,  # Disappear ~3s after background fill completes
    background_color="#9C27B0",
    icon_background_color="#E1BEE7"
)
```

## 🚀 Example App

A comprehensive example demonstrating all features, styling options, and positioning modes is provided in `example.py`. Run it with:

```sh
streamlit run example.py
```

## 🛠️ Development

### Local Development

```bash
# Clone the repository
git clone https://github.com/lejuliennn/streamlit-achievements.git
cd streamlit-achievements

# Install dependencies
pip install -r requirements.txt

# Run the example
streamlit run example.py
```

### Building

```bash
# Build the package
cd ../../..
python setup.py sdist bdist_wheel

# Install locally
pip install -e .
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- 🐛 Issues: [GitHub Issues](https://github.com/lejuliennn/streamlit-achievements/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/lejuliennn/streamlit-achievements/discussions)
