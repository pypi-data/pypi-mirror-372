---
layout: page
title: Getting Started
permalink: /docs/getting-started/
---

# Getting Started

This guide will help you install Minecraft Datapack Language (MDL) and create your first datapack.

## Installation

### Option A: Using pipx (Recommended)

pipx installs Python applications in isolated environments, which is perfect for command-line tools like MDL.

```bash
# Install pipx if you don't have it
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install MDL
pipx install minecraft-datapack-language

# Verify installation
mdl --help
```

**Note**: After installing pipx, you may need to restart your terminal or run `source ~/.bashrc` (Linux/macOS) or restart your PowerShell session (Windows).

### Option B: Using pip in a Virtual Environment

If you prefer using pip directly:

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate it (Linux/macOS)
source .venv/bin/activate

# Activate it (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install MDL
pip install minecraft-datapack-language

# Verify installation
mdl --help
```

### Option C: From Source (for Contributors)

```bash
# Clone the repository
git clone https://github.com/aaron777collins/MinecraftDatapackLanguage.git
cd MinecraftDatapackLanguage

# Install in development mode
python -m pip install -e .
```

## Updating MDL

- **pipx**: `pipx upgrade minecraft-datapack-language`
- **pip**: `pip install -U minecraft-datapack-language`
- **Pin a version**: `pipx install "minecraft-datapack-language==1.1.0"`

## Your First Datapack

Let's create a simple datapack that displays a welcome message when the world loads.

### 1. Create the MDL File

Create a file called `hello.mdl` with the following content:

```mdl
# hello.mdl - My first datapack
pack "My First Pack" description "A simple example datapack" pack_format 48

namespace "example"

function "hello":
    say Hello, Minecraft!
    tellraw @a {"text":"Welcome to my datapack!","color":"green"}

# Hook the function to run when the world loads
on_load "example:hello"
```

### 2. Build the Datapack

```bash
mdl build --mdl hello.mdl -o dist
```

This will create a `dist/` folder containing your compiled datapack.

### 3. Install in Minecraft

1. Open your Minecraft world
2. Navigate to the world's `datapacks` folder:
   - **Singleplayer**: `.minecraft/saves/[WorldName]/datapacks/`
   - **Multiplayer**: Copy to the server's `world/datapacks/` folder
3. Copy the folder from `dist/` to the datapacks folder
4. In-game, run `/reload` to load the datapack
5. You should see the welcome message!

## Understanding the Code

Let's break down what we just created:

- **`pack "My First Pack"`**: Declares the datapack name and metadata
- **`pack_format 48`**: Specifies compatibility with Minecraft 1.21+
- **`namespace "example"`**: Creates a namespace for organizing functions
- **`function "hello":`**: Defines a function that contains Minecraft commands
- **`on_load "example:hello"`**: Automatically runs the function when the world loads

## Adding Conditional Logic

> **Enhanced Logic**: The conditional system ensures proper if/else if/else logic where each condition is only checked if all previous conditions were false.

Now let's create a more advanced example that uses conditional blocks to detect different types of entities:

```mdl
# conditional.mdl - Conditional logic example
pack "Conditional Demo" description "Shows if/else if/else functionality" pack_format 48

namespace "demo"

function "detect_entity":
    if "entity @s[type=minecraft:player]":
        say Player detected!
        effect give @s minecraft:glowing 5 1
        tellraw @a {"text":"A player is nearby!","color":"green"}
    else if "entity @s[type=minecraft:zombie]":
        say Zombie detected!
        effect give @s minecraft:poison 5 1
        tellraw @a {"text":"A zombie is nearby!","color":"red"}
    else if "entity @s[type=minecraft:creeper]":
        say Creeper detected!
        effect give @s minecraft:slowness 5 1
        tellraw @a {"text":"A creeper is nearby!","color":"dark_red"}
    else:
        say Unknown entity detected
        tellraw @a {"text":"Something unknown is nearby...","color":"gray"}

# Run the detection every tick
on_tick "demo:detect_entity"
```

This example demonstrates:
- **`if "condition":`** - Checks if the condition is true
- **`else if "condition":`** - Checks another condition if the first was false
- **`else:`** - Runs if none of the above conditions were true
- **Indentation** - Commands inside conditional blocks must be indented with 4 spaces

The conditional blocks are compiled into separate functions and called using Minecraft's `execute` command for efficient execution.

## Next Steps

Now that you have the basics, explore:

- **[Language Reference]({{ site.baseurl }}/docs/language-reference/)** - Learn the complete MDL syntax
- **[Examples]({{ site.baseurl }}/docs/examples/)** - See more complex examples (all tested and verified!)
- **[CLI Reference]({{ site.baseurl }}/docs/cli-reference/)** - Master the command-line tools
- **[VS Code Extension]({{ site.baseurl }}/docs/vscode-extension/)** - Get syntax highlighting and linting

### Want to See Working Examples?

All examples in the documentation are thoroughly tested and available for download. Check out the **[Tested Examples]({{ site.baseurl }}/docs/examples/#tested-examples)** section for direct links to working MDL and Python API files.

## Troubleshooting

### "mdl command not found"

If you get a "command not found" error after installation:

1. **pipx users**: Make sure you ran `python3 -m pipx ensurepath` and restarted your terminal
2. **pip users**: Make sure your virtual environment is activated
3. **Windows users**: Try using `python -m minecraft_datapack_language.cli` instead of `mdl`

### Build Errors

If you get build errors:

1. Check that your MDL syntax is correct (see [Language Reference]({{ site.baseurl }}/docs/language-reference/))
2. Make sure you have a `pack` declaration at the top of your file
3. Verify that function names are unique within each namespace
4. Use `mdl check hello.mdl` to validate your file before building

### Datapack Not Working

If your datapack doesn't work in Minecraft:

1. Make sure you copied the entire folder from `dist/` to the datapacks directory
2. Run `/reload` in-game to reload datapacks
3. Check the game logs for error messages
4. Verify that your pack_format is compatible with your Minecraft version
