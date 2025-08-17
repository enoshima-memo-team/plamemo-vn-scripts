# Plastic Memories Scripts

## Description

This repo is comprised of a set tools and scripts, mostly written in `Python`, to help with the translation of the [Plastic Memories Visual Novel](https://vndb.org/v19441).


## Support

- python 3.8+


## Installation and usage

### Local usage

See [Contributing](#contributing) section for instructions on how to install the project locally.

#### JSON exporter [alpha-version]

Exports and merge the game texts to a more parseable JSON that can be imported to traslations tools (like [Crowdin](https://crowdin.com/))

```	bash
python json-exporter.py \
  --input-folder-en <path_to_en_folder> \
  --input-folder-ja <path_to_jap_folder> \
  --output-folder <path_to_output_folder>
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

> We are working on a better way to install and run the tools, like using executables files or. Maybe we'll be putting some builds in the [Releases](https://github.com/enoshima-memo-team/plamemo-vn-scripts/releases) section. For now, you can use the above commands to install and run the tools locally.

> If you need to download python or git, you can find them here:
> - [Python](https://www.python.org/downloads/)
> - [Git](https://git-scm.com/downloads)

## Contact Us

For any questions or help, you can:
- Open an issue [here](https://github.com/enoshima-memo-team/plamemo-vn-scripts/issues)
- Contact us on our [Discord server](https://discord.gg/B4nxw5JjJd)
