# Crowdin

## Custom File Format importer/exporter (CFF)

Crowdin provides the `Custom File Format` (`CFF`) parser, which enables to import and export json files with a custom structure. These files can include both the original text and its translations.

`translations-manager` scripts generate the files to be imported by the `CFF` parser, an also can import the files exporte by the `CFF` parser too.

`CFF` parser needs the following files, both should be written in `JavaScript`:
  - **Importer code**: code located in the `custom-file-importer.js` file
  - **Exporter code**: code located in the `custom-file-exporter.js` file

`CFF` can be enabled at [Project - Settings - Parser configuration > Custom File Format](https://crowdin.com/project/plastic-memories-vn/settings#parsers)

### Reference and docs

- [Crowdin Store - Custom File Format](https://store.crowdin.com/cff)
- [Crowdin Store - Custom File Format - Strings array structure](https://support.crowdin.com/developer/crowdin-apps-module-custom-file-format/#strings-array-structure)

---

## Crowdin CLI

Crowdin CLI is used to automate the following operations:

- **Import string files**: upload `translations-manager` generated json files that can be ingested by the `CFF importer script`
- **Export string files**: download json files that that can be ingested back by the `translations-manager` scripts


### Setup and config

- Follow the installation instructions [here](https://crowdin.github.io/crowdin-cli/installation)

- Add a `crowdin.yml` file with the root of the repository
- `project_id`, `base_url` and `api_token` configs are mandatory
- `api_token` shouldn't be added to the repo `crowdin.yml` file. Add it to the user's `crowdin.yml` file instead
- Personal Access Tokens can be created at account level (not at project level) at [Settings > API](https://crowdin.com/settings#api-key)

- Then use the following commands to `setup` and validate the configuration:

``` bash
# check global config
cat ~/.crowdin.yml

# setup and check config
crowdin init
crowdin status
crowdin language list
```

### Work with strings and translations

``` bash
# upload (if enabled, uses CFF import script)
crowdin upload sources --verbose
crowdin upload translations --import-eq-suggestions  --verbose

# download (if enabled, uses CFF export script)
crowdin download sources --verbose
crowdin download translations --verbose

# list uploaded source files
crowdin file list --verbose
crowdin file list --tree --verbose
crowdin file download <file> -l=en -d=output --verbose

# list uploaded source files, including lang path
crowdin config sources --tree --verbose
```

### Reference and docs

- [Crowdin - crowdin.yml File structure](https://support.crowdin.com/developer/configuration-file)
- [Crowdin CLI - Configuration](https://crowdin.github.io/crowdin-cli/configuration)
- [Crowdin CLI - Split Project Configuration and API Credentials](https://crowdin.github.io/crowdin-cli/configuration#split-project-configuration-and-api-credentials)
- [Crowdin CLI - Languages mapping configuration](https://crowdin.github.io/crowdin-cli/advanced#languages-mapping-configuration)
- [Crowdin - Official Custom File Format GPT](https://chatgpt.com/g/g-sswU8ps5H-custom-file-format-for-crowdin-code-writer)
