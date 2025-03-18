@echo off
echo Building Opti-WebP...
pyinstaller --noconfirm --onefile --windowed --icon=opti_webp.ico --add-data "opti_webp.ico;." --add-data "opti_webp.py;." --name "Opti-WebP" opti_webp_gui.py
echo Build complete!
pause 