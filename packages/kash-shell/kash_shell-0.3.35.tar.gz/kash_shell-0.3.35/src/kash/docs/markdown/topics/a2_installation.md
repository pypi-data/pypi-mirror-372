## Installation

### Running the Kash Shell

Kash offers a shell environment based on [xonsh](https://xon.sh/) augmented with a bunch
of enhanced commands and customizations.
If you’ve used a bash or Python shell before, it should be very intuitive.

Within the kash shell, you get a full environment with all actions and commands.
You also get intelligent auto-complete, a built-in assistant to help you perform tasks,
and enhanced tab completion.

The shell is an easy way to use Kash actions, simply calling them like other shell
commands from the command line.

But remember that’s just one way to use actions; you can also use them directly in
Python or from an MCP client.

### Current Kash Packages

The base installation of kash is the `kash-shell` package.
However, some use cases require additional libraries, like video downloading tools, PDF
handling, etc.

To keep kash dependencies more manageable, these additional utilities and actions are
packaged additional “kits”.

The examples below use video transcription from YouTube as an example.
To start with more full examples, I suggest starting with the `kash-media` kit.

### Installation Steps

These steps have mainly been tested on macOS but should work on other platforms.
These are for `kash-media` but you can use a `kash-shell` for a more basic setup.

1. **Install uv and Python:**

   Kash is easiest to use via [**uv**](https://docs.astral.sh/uv/), the new package
   manager for Python. `uv` replaces traditional use of `pyenv`, `pipx`, `poetry`, `pip`,
   etc. Installing `uv` also ensures you get a compatible version of Python.
   See [uv’s docs](https://docs.astral.sh/uv/getting-started/installation/) for other
   installation methods and platforms.
   Usually you just want to run:
   ```shell
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install additional command-line tools:**

   In addition to Python, it’s highly recommended to install a few other dependencies to
   make more tools and commands work.
   For macOS, you can again use brew:

   ```shell
   brew update
   brew install libmagic ffmpeg ripgrep bat eza hexyl imagemagick zoxide
   ```

   For Ubuntu:

   ```shell
   sudo apt-get update
   sudo apt-get install -y libgl1 ffmpeg libmagic-dev imagemagick bat ripgrep hexyl

   # Or for additional command-line tools, pixi is better on Ubuntu:
   curl -fsSL https://pixi.sh/install.sh | sh
   . ~/.bashrc
   pixi global install ripgrep bat eza hexyl imagemagick zoxide
   ```

   For Windows or other platforms, see the uv instructions.

   Kash auto-detects and uses `ripgrep` (for search), `bat` (for prettier file display),
   `eza` (a much improved version of `ls`), `hexyl` (a much improved hex viewer),
   `imagemagick` (for image display in modern terminals), `libmagic` (for file type
   detection), `ffmpeg` (for audio and video conversions)

3. **Install kash or a kash kit:**

   For a more meaningful demo, use an enhanced version of kash that also has various
   media tools (like yt-dlp and Deepgram support):

   ```shell
   uv tool install kash-media --upgrade --python=3.13
   ```

   Other versions of Python should work but 3.13 is recommended.
   For a setup without the media tools, just install `kash-shell` instead.

4. **Set up API keys:**

   You will need API keys for all services you wish to use.
   Configuring OpenAI, Anthropic, Groq (for Llama 3), and Deepgram (if you wish to do
   transcriptions) are a good start.
   But kash supports dozens of models
   [via LiteLLM](https://docs.litellm.ai/docs/providers).

   You can set these up now, or after you run kash (below):

   ```shell
   # Set up API secrets:
   cp .env.template .env 
   # Now edit the .env file to add all desired API keys.
   # You can also put .env in ~/.env if you want it to be usable in any directory.
   ```

   These keys should go in the `.env` file in your current work directory or a parent or
   your home directory (recommended if you’ll be working in several directories, as with
   a typical shell).

5. **Run kash:**

   ```shell
   kash
   ```

   You should see a welcome message with all info about APIs and tools.

   Use the `self_check` command to confirm which tools and API keys are working.

   Use the `self_configure` command as a quick way to fill in additional values in your
   .env file and to set workspace parameters on what LLMs to use by default.

### Running Kash as an MCP Server

You can use kash from your MCP client (such as Anthropic Desktop or Cursor).

You do this by running the the `kash-mcp` binary to make kash actions available as MCP
tools.

For Claude Desktop, my config looks like this:

```json
{
  "mcpServers": {
    "kash": {
      "command": "/Users/levy/.local/bin/kash-mcp",
      "args": ["--proxy"]
    }
  }
}
```

If you add the `--proxy` arg, it will run an MCP stdio server but connect to the MCP SSE
server you are running in the kash shell, by default at `localhost:4440`.

Then if you run `start_mcp_server` from the shell, your client will connect to your
shell, and you can actually use any “published” kash action as an MCP tool.

Then you can for example ask your MCP client “can you transcribe this video?”
and give it a URL, and it will be able to call the `transcribe` action as a tool.

What is even better is that all the inputs and outputs are saved in the current kash
workspace, just as if you’d been running these commands yourself in the shell.
This way, you don’t lose context or any work, and can seamlessly switch between an MCP
client like Cursor, the shell, and any other tools to edit the inputs or outputs of
actions in your workspace directory.

### Running Kash From Source

See the `development.md` file in GitHub for building and using kash from source.
