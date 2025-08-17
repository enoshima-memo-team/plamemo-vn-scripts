# TODO - Quick guide to generate executables

``` bash
# Install the needed library using this
pip install pyinstaller

# Move to the folder where the json-exporter.py is located
cd <path/where/json-exporter.py/is/located>

# Generate the executable
pyinstaller --onefile json-exporter.py

# A dist folder will be created in the actual folder.
# The executable will be located in that dist folder, so lets move there.
cd dist

# =====================================================

# WINDOWS

# Move the executable to wherever you want
mv json-exporter <some\path>

# Run the executable by double clicking it or using the command line
# You can also create a direct access to the executable in the desktop
# or wherever you want
json-exporter.exe

# =====================================================

# LINUX
# Give permission to execute
chmod +x dist/json-exporter

# Move the executable to wherever you want
mv ./json-exporter <some/path>

# Run the executable
./json-exporter
