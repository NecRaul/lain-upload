# lain-upload

A simple CLI file uploader for multiple file-hosting services, with optional clipboard copy.

## Installation

### Via PyPI (Recommended)

You have the option to choose between the standard version (lain-upload) or the desktop version (lain-upload[clipboard]), which adds clipboard support for auto-copying links.

> [!NOTE]
> For brevity, the examples below use the desktop version.

#### With pip (Basic)

```sh
pip install "lain-upload[clipboard]"
```

#### With pipx (Isolated)

```sh
pipx install "lain-upload[clipboard]"
```

#### With uv (Best)

The most efficient way to install or run the uploader.

```sh
# Permanent isolated installation
uv tool install "lain-upload[clipboard]"

# Run once without installing
uvx --with "lain-upload[clipboard]" lain-upload <file1> <file2> <file3>

# Run in scripts or ad-hoc environments
uv run --with "lain-upload[clipboard]" lain-upload <file1> <file2> <file3>
```

### From Source (Development)

```sh
# Clone the repository and navigate to it
git clone git@github.com:NecRaul/lain-upload.git
cd lain-upload

# Install environment and all development dependencies (mandatory and optional)
uv sync --dev

# Install pre-commit hook
uv run pre-commit install

# Optional: Run all linters and type checkers manually
uv run pre-commit run --all-files

# Run the local version
uv run lain-upload <file1> <file2> <file3>

# Run tests
uv run pytest tests
```

## Usage

Simply provide the path to the file or files you wish to upload.

```sh
# Upload a single file (default host: catbox)
lain-upload kuroneko.png

# Upload multiple files from different directories
lain-upload /path/to/kuroneko.png /path/to/another/directory/shironeko.png yamineko.png ../kamineko.png

# Select a specific host
lain-upload --host uguu kuroneko.png

# Use host authentication when supported
lain-upload --host mixdrop --auth necraul@kuroneko.dev:generated_api_key kuroneko.png

# Set temporary file expiration when supported (e.g. 1h, 12h, 24h, 72h, etc.)
lain-upload --host litterbox --expire-after 24h kuroneko.png

# Enable longer generated filenames when supported
lain-upload --host 0x0 --long-filenames -- kuroneko.png shironeko.png

# Display help and version
lain-upload -h
lain-upload -v
```

## Supported Hosts

- [catbox](https://catbox.moe/) - Support for user authentication with userhashes.
- [litterbox](https://litterbox.catbox.moe/) - Support for custom expiration time and longer upload filenames.
- [pomf](https://pomf.lain.la/) - No extra options (_deprecated_).
- [uguu](https://uguu.se/) - No extra options.
- [fileditch](https://fileditch.com/) - No extra options.
- [0x0](https://0x0.st/) - Support for custom expiration time and longer upload filenames.
- [gofile](https://gofile.io/) - Support for user authentication with bearer API tokens.
- [pixeldrain](https://pixeldrain.com/) - Support for user authentication with API keys (**Required**).
- [buzzheavier](https://buzzheavier.com/) - No extra options.
- [mixdrop](https://mixdrop.ag/) - Support for user authentication with mail and API keys (**Required**).

## Dependencies

- [requests](https://github.com/psf/requests): send the API request for uploading.
- [requests-toolbelt](https://github.com/requests/toolbelt): enable memory-efficient streaming and progress tracking for large uploads.

### Optional

- [pyperclip](https://github.com/asweigart/pyperclip): copy the uploaded files' URLs to the clipboard.

## How it works

Supported services expose upload endpoints via multipart `POST` requests.

This tool automates uploads and adds safety checks and quality-of-life features.

### The Manual Way

```sh
curl -F "file=@kuroneko.png" https://example-upload-service.tld/upload-endpoint
```

### The lain-upload way

- Batch Processing: Upload multiple files in a single command execution, saving time over individual manual requests.
- Validation: Checks file constraints before uploading (service-specific rules are enforced per host).
- API Request: Sends multipart `POST` requests via `requests` and `requests-toolbelt`, with streaming support for large files.
- Normalization: Parses server responses into clean, shareable URLs.
- Clipboard (Optional): If `pyperclip` is installed, the result is instantly copied to your clipboard.

## Special thanks

- To **7666** of <https://lain.la/> for running the [pomf](https://pomf.lain.la/) service that inspired this project.
- To **r/a/dio anons** for feedback and suggestions.
