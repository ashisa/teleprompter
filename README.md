# Teleprompter Application

A simple yet feature-rich teleprompter application built with Python and tkinter.

## Features

- **Dual Mode Operation**: Toggle between Edit and Display modes
- **Customizable Font Size**: Adjust from 8 to 72 points using the slider
- **Variable Scroll Speed**: Control auto-scrolling speed from 0.1x to 5.0x
- **Auto-positioning**: Opens at center-top of screen (350x400px)
- **Professional Display**: Black background with white text in Display mode
- **Easy Controls**: All controls conveniently located at the bottom

## How to Use

### Installation
1. Ensure Python 3.x is installed on your system
2. No additional packages required - uses built-in tkinter

### Running the Application
```bash
python teleprompter.py
```

### Usage Instructions

#### Edit Mode
- **Default mode** when the application starts
- Type or paste your script in the text area
- Use the scrollable text area to enter long scripts
- Adjust font size and scroll speed as needed

#### Display Mode
- Click "Edit Mode" button to switch to "Display Mode"
- Text appears with white text on black background for better visibility
- Use "Start Scrolling" to begin auto-scroll
- Click "Stop Scrolling" to pause
- Scrolling automatically stops when reaching the end

#### Controls
- **Font Size Slider**: Adjust text size (8-72 points)
- **Scroll Speed Slider**: Control auto-scroll speed (0.1x-5.0x)
- **Mode Toggle Button**: Switch between Edit and Display modes
- **Scroll Control Button**: Start/stop auto-scrolling (Display mode only)

## Tips for Best Results

1. **Font Size**: Choose a size that's comfortable to read from your distance
2. **Scroll Speed**: Start slow and adjust based on your reading pace
3. **Script Preparation**: Use Edit mode to prepare and format your script
4. **Display Setup**: Use Display mode during recording or presentation
5. **Position**: The window opens at center-top - adjust monitor accordingly

## Keyboard Shortcuts

- **Alt+F4**: Close application (Windows)
- **Cmd+Q**: Quit application (macOS)
- **Ctrl+A**: Select all text (Edit mode)
- **Ctrl+C/V**: Copy/Paste text (Edit mode)

## System Requirements

- Python 3.x
- Operating System: Windows, macOS, or Linux
- Display: Any resolution (optimized for 1920x1080 and above)

## Troubleshooting

If you encounter any issues:

1. **Application won't start**: Ensure Python and tkinter are properly installed
2. **Scrolling too fast/slow**: Adjust the scroll speed slider
3. **Text too small/large**: Use the font size slider
4. **Window positioning**: The app centers itself at screen top automatically

For Linux users who don't have tkinter installed:
```bash
sudo apt-get install python3-tk
```

## License
This project is open source and available for personal and educational use.
