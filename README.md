# Plastic Memories Scripts

## Description

Plastic Memories set of tools and scripts, mostly in python, to help with the traduction of the visual novel.


## Support

- python 3.8+


## Inspiration

This repo is inspired by [Python Project Boilerplate](https://github.com/keathmilligan/python-boilerplate)


## Installation and usage

### Local usage

See [Contributing](#contributing) section for instructions on how to install the project locally.

#### With User Interface

- Run the .exe file:
```	Bash
.\json-exporter.exe```

- Or run the python script directly:
```	Bash
python json-exporter.py```

#### As CLI

- Use the .exe:
```	Bash
.\json-exporter.exe --input-folder-en <your_english_input_folder> --input-folder-ja <your_japanese_input_folder> --output-folder <your_desired_output_folder>
```

- Or run the python script directly:
```	Bash
python json-exporter.py --input-folder-en <your_english_input_folder> --input-folder-ja <your_japanese_input_folder> --output-folder <your_desired_output_folder>
```

## Contributing

``` bash
# Clone the repository
git clone https://github.com/enoshima-memo-team/plamemo-vn-scripts

# Activate the virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the dependencies
pip install -r requirements.txt         # if you just want to run the tools
pip install -r requirements-dev.txt     # if you want to contribute to the project

# Deactivate the virtual environment once finished working on the project
deactivate
```

> We are working on a better way to install and run the tools, like a .exe installer or similar, maybe in the [Releases](https://github.com/enoshima-memo-team/plamemo-vn-scripts/releases) section. For now, you can use the above commands to install and run the tools locally. 

> If you need to download python or git, you can find them here:
> - [Python](https://www.python.org/downloads/)
> - [Git](https://git-scm.com/downloads)

## Contact Us

For any questions or help, you can:
- Open an issue [here](https://github.com/enoshima-memo-team/plamemo-vn-scripts/issues)
- Contact us on our [Discord server](https://discord.gg/Tz9maCVMWQ)