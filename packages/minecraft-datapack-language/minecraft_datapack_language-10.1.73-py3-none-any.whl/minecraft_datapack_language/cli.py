
import argparse, os, sys, json, traceback, re, zipfile, shutil, glob
from typing import Dict, Any, List
from .pack import Pack, Function
from .utils import ensure_dir
from .mdl_parser_js import parse_mdl_js
from .expression_processor import expression_processor, ProcessedExpression
from .linter import lint_mcfunction_file, lint_mcfunction_directory, format_lint_report
from . import __version__

def _slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r'[^a-z0-9._-]+', '-', s)
    return s or "pack"

def _zip_dir(src_dir: str, zip_path: str):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(src_dir):
            for f in files:
                abs_path = os.path.join(root, f)
                rel = os.path.relpath(abs_path, src_dir)
                zf.write(abs_path, rel)

def _gather_mdl_files(path: str):
    """Gather MDL files from a path. Supports:
    - Directory: recursively finds all .mdl files
    - Single file: returns just that file
    - Space-separated file list: returns all specified files
    """
    # Check if it's a space-separated list of files
    if ' ' in path and not os.path.exists(path):
        files = path.split()
        # Validate each file exists
        for f in files:
            if not os.path.isfile(f):
                raise SystemExit(f"File not found: {f}")
        return files
    
    if os.path.isdir(path):
        files = [p for p in glob.glob(os.path.join(path, "**", "*.mdl"), recursive=True)]
        # Sort files, but prioritize files with pack declarations
        def sort_key(f):
            # Check if file has a pack declaration
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    content = file.read()
                    has_pack = any(line.strip().startswith("pack ") for line in content.splitlines())
                    # Files with pack declarations come first (lower sort key)
                    return (0 if has_pack else 1, f)
            except:
                # If we can't read the file, treat it as a regular file
                return (1, f)
        
        return sorted(files, key=sort_key)
    elif os.path.isfile(path):
        return [path]
    else:
        raise SystemExit(f"Path not found: {path}")

def _parse_many(files, default_pack_format: int, verbose: bool = False):
    root_pack = None
    if verbose:
        print(f"Processing {len(files)} MDL file(s)...")
    
    for i, fp in enumerate(files, 1):
        if verbose:
            print(f"  [{i}/{len(files)}] {fp}")
        with open(fp, "r", encoding="utf-8") as f:
            src = f.read()
        
        # Check if this file has a pack declaration
        has_pack_declaration = any(line.strip().startswith("pack ") for line in src.splitlines())
        
        if has_pack_declaration and root_pack is not None:
            raise RuntimeError(f"{fp}: duplicate pack declaration (only the first file should have a pack declaration)")
        
        try:
            # Parse with JavaScript-style parser
            ast = parse_mdl_js(src)
            
            # Convert AST to Pack object
            p = _ast_to_pack(ast, default_pack_format)
        except Exception as e:
            # Bubble up with filename context
            raise RuntimeError(f"{fp}: {e}")
        
        if root_pack is None:
            root_pack = p
            if verbose:
                print(f"    Using pack: {p.name} (format: {p.pack_format})")
        else:
            # Ensure consistent pack_format; prefer explicit default
            if p.pack_format != root_pack.pack_format and default_pack_format is not None:
                p.pack_format = default_pack_format
            if verbose:
                print(f"    Merging into: {root_pack.name}")
            root_pack.merge(p)
    
    if root_pack is None:
        raise SystemExit("No .mdl files found")
    
    if verbose:
        print(f"Successfully merged {len(files)} file(s) into datapack: {root_pack.name}")
    return root_pack

def cmd_new(args):
    # Create a sample project
    root = os.path.abspath(args.path)
    
    # Check if the path already exists
    if os.path.exists(root):
        print(f"ERROR: Path {root} already exists")
        return 1
    
    # Create the directory
    ensure_dir(root)
    
    # Use the path name for the pack name and namespace, not the --name argument
    pack_name = os.path.basename(args.path)
    
    # Create the pack declaration separately to avoid f-string issues with array literals
    pack_declaration = 'pack "{}" description "Example datapack" pack_format {} min_format [{}, 0] max_format [{}, 1] min_engine_version "1.21.4";'.format(pack_name, args.pack_format, args.pack_format, args.pack_format)
    
    sample = f"""// {pack_name}.mdl - Advanced example showcasing ALL MDL features
{pack_declaration}
namespace "{pack_name}";

// Global state variables
var num global_counter = 0;
var str global_message = "System Ready";
var list global_numbers = [1, 2, 3, 4, 5];
var list global_strings = ["apple", "banana", "cherry"];

function "inner" {{
    tellraw @s {{"text":"[{pack_name}:inner] This is the inner function"}};
    tellraw @a {{"text":"Running inner","color":"yellow"}};
}}

function "hello" {{
    tellraw @s {{"text":"[{pack_name}:hello] Outer says hi"}};
    function {pack_name}:inner;
    tellraw @a {{"text":"Back in hello","color":"aqua"}};
}}

// Advanced variable operations with all data types
function "variable_demo" {{
    var num local_counter = 10;
    var str player_name = "Steve";
    var list local_items = ["sword", "shield", "potion"];
    
    // Number operations
    local_counter = local_counter + 5;
    global_counter = global_counter + 1;
    
    // String operations
    player_name = "Alex";
    global_message = "Updated: " + player_name;
    var str full_name = player_name + " Minecraft";
    
    // List operations
    local_items.append("bow");
    local_items.insert(1, "armor");
    var num first_item = local_items[0];
    var num item_count = local_items.length;
    
    // Complex calculations
    var num result = (local_counter * 2) + global_counter;
    var num modulo_result = result % 7;
    
    // String concatenation with variables
    var str status = player_name + " has " + item_count + " items";
    
    tellraw @s {{"text":"Variable demo complete"}};
    tellraw @s [{{"text":"Result: "}},{{"score":{{"name":"@s","objective":"result"}}}}];
    tellraw @s [{{"text":"Modulo: "}},{{"score":{{"name":"@s","objective":"modulo_result"}}}}];
    tellraw @s [{{"text":"Status: "}},{{"nbt":"status","storage":"{args.name}:variables"}}];
}}

// Advanced conditional logic with dynamic variables
function "conditional_demo" {{
    var num player_level = 15;
    var str player_class = "warrior";
    var num experience = 75;
    var num min_level = 10;
    var num max_level = 20;
    var num required_exp = 50;
    
    // Use simple variable names - system will automatically convert to matches syntax
    if "player_level matches min_level.." {{
        if "player_class matches 'warrior'" {{
            if "experience matches required_exp.." {{
                tellraw @s {{"text":"Advanced warrior detected!"}};
                effect give @s minecraft:strength 10 2;
                effect give @s minecraft:glowing 10 0;
            }} else {{
                tellraw @s {{"text":"Novice warrior"}};
                effect give @s minecraft:haste 10 0;
            }}
        }} else if "player_class matches 'mage'" {{
            tellraw @s {{"text":"Advanced mage detected!"}};
            effect give @s minecraft:night_vision 10 0;
            effect give @s minecraft:levitation 5 0;
        }} else {{
            tellraw @s {{"text":"Unknown advanced class"}};
            effect give @s minecraft:glowing 10 0;
        }}
    }} else if "player_level matches ..max_level" {{
        tellraw @s {{"text":"Player level within range"}};
        effect give @s minecraft:speed 10 0;
    }} else {{
        tellraw @s {{"text":"Beginner player"}};
        effect give @s minecraft:jump_boost 10 0;
    }}
}}

// Advanced weapon effects with list operations
function "weapon_effects" {{
    var list weapons = ["diamond_sword", "golden_sword", "bow"];
    var num weapon_index = 0;
    
    if "entity @s[type=minecraft:player,nbt={{SelectedItem:{{id:'minecraft:diamond_sword'}}}}]" {{
        weapon_index = 0;
        tellraw @s {{"text":"Diamond sword detected!"}};
        effect give @s minecraft:strength 10 1;
        effect give @s minecraft:glowing 10 0;
    }} else if "entity @s[type=minecraft:player,nbt={{SelectedItem:{{id:'minecraft:golden_sword'}}}}]" {{
        weapon_index = 1;
        tellraw @s {{"text":"Golden sword detected!"}};
        effect give @s minecraft:speed 10 1;
        effect give @s minecraft:night_vision 10 0;
    }} else if "entity @s[type=minecraft:player,nbt={{SelectedItem:{{id:'minecraft:bow'}}}}]" {{
        weapon_index = 2;
        tellraw @s {{"text":"Bow detected!"}};
        effect give @s minecraft:jump_boost 10 1;
    }} else if "entity @s[type=minecraft:player]" {{
        tellraw @s {{"text":"Player without special weapon"}};
        effect give @s minecraft:haste 5 0;
    }} else {{
        tellraw @s {{"text":"No player found"}};
    }}
    
    // Use list to get weapon name with dynamic variable
    if "weapon_index matches ..weapons_length" {{
        var str current_weapon = weapons[weapon_index];
        tellraw @s [{{"text":"Using weapon: "}},{{"nbt":"current_weapon","storage":"{pack_name}:variables"}}];
    }}
}}

// Advanced loop patterns with break and continue
function "loop_demo" {{
    var num outer_count = 0;
    var num inner_count = 0;
    var num total_iterations = 0;
    
    // Nested loops with matches syntax
    var num max_outer = 2;
    var num max_inner = 1;
    while "outer_count matches ..max_outer" {{
        inner_count = 0;
        
        while "inner_count matches ..max_inner" {{
            total_iterations = total_iterations + 1;
            
            // Complex calculation within loop
            var num calculation = (outer_count * 10) + inner_count;
            var num modulo_result = calculation % 5;
            
            if "score @s modulo_result matches 0" {{
                tellraw @s [{{"text":"Perfect calculation: "}},{{"score":{{"name":"@s","objective":"calculation"}}}}];
            }} else {{
                tellraw @s [{{"text":"Calculation: "}},{{"score":{{"name":"@s","objective":"calculation"}}}},{{"text":" (mod 5 = "}},{{"score":{{"name":"@s","objective":"modulo_result"}}}},{{"text":")"}}];
            }}
            
            inner_count = inner_count + 1;
        }}
        
        outer_count = outer_count + 1;
    }}
    
    // Loop with break and continue using matches syntax
    var num break_counter = 0;
    var num continue_counter = 0;
    var num break_sum = 0;
    var num continue_sum = 0;
    var num max_break = 9;
    var num max_continue = 9;
    var num break_threshold = 7;
    
    while "break_counter matches ..max_break" {{
        break_counter = break_counter + 1;
        
        if "break_counter matches break_threshold" {{
            break;
        }}
        
        break_sum = break_sum + break_counter;
    }}
    
    while "continue_counter matches ..max_continue" {{
        continue_counter = continue_counter + 1;
        
        if continue_counter % 2 == 0 {{
            continue;
        }}
        
        continue_sum = continue_sum + continue_counter;
    }}
    
    tellraw @s {{"text":"Loop demo complete"}};
    tellraw @s [{{"text":"Total iterations: "}},{{"score":{{"name":"@s","objective":"total_iterations"}}}}];
    tellraw @s [{{"text":"Break sum: "}},{{"score":{{"name":"@s","objective":"break_sum"}}}}];
    tellraw @s [{{"text":"Continue sum: "}},{{"score":{{"name":"@s","objective":"continue_sum"}}}}];
}}

// Mathematical algorithms with dynamic variables
function "calculate_fibonacci" {{
    var num n = 10;
    var num a = 0;
    var num b = 1;
    var num i = 2;
    var num temp = 0;
    
    // Use dynamic variable in while loop condition
    while "i matches ..n" {{
        temp = a + b;
        a = b;
        b = temp;
        i = i + 1;
    }}
    
    tellraw @s [{{"text":"Fibonacci result: "}},{{"score":{{"name":"@s","objective":"b"}}}}];
    tellraw @s [{{"text":"Fibonacci("}},{{"score":{{"name":"@s","objective":"n"}}}},{{"text":") = "}},{{"score":{{"name":"@s","objective":"b"}}}}];
}}

// Data processing with lists and dynamic variables
function "process_data" {{
    var list scores = [85, 92, 78, 96, 88];
    var list names = ["Alice", "Bob", "Charlie", "Diana", "Eve"];
    var num total_score = 0;
    var num highest_score = 0;
    var str best_player = "";
    
    // Calculate total and find highest
    var num i = 0;
    // Use dynamic variable for list length
    while "i matches ..scores_length" {{
        var num current_score = scores[i];
        var str current_name = names[i];
        
        total_score = total_score + current_score;
        
        if "score @s current_score matches @s highest_score.." {{
            highest_score = current_score;
            best_player = current_name;
        }}
        i = i + 1;
    }}
    
    var num average_score = total_score / scores.length;
    
    tellraw @s {{"text":"Data processing complete"}};
    tellraw @s [{{"text":"Total score: "}},{{"score":{{"name":"@s","objective":"total_score"}}}}];
    tellraw @s [{{"text":"Average score: "}},{{"score":{{"name":"@s","objective":"average_score"}}}}];
    tellraw @s [{{"text":"Best player: "}},{{"nbt":"best_player","storage":"{args.name}:variables"}},{{"text":" ("}},{{"score":{{"name":"@s","objective":"highest_score"}}}},{{"text":")"}}];
}}

// Error handling and edge cases with dynamic variables
function "error_handling" {{
    // Test division by zero handling
    var num dividend = 10;
    var num divisor = 0;
    var num result = 0;
    var num zero_threshold = 0;
    
    if "divisor matches zero_threshold" {{
        result = 0;
        tellraw @s {{"text":"Division by zero prevented"}};
    }} else {{
        result = dividend / divisor;
    }}
    
    // Test list bounds checking with dynamic variables
    var list test_list = [1, 2, 3];
    var num safe_index = 1;
    var num unsafe_index = 10;
    var num safe_value = 0;
    var num unsafe_value = 0;
    
    if "safe_index matches ..test_list_length" {{
        safe_value = test_list[safe_index];
    }}
    
    if "score @s unsafe_index matches ..@{{test_list_length}}" {{
        unsafe_value = test_list[unsafe_index];
    }} else {{
        unsafe_value = -1;
        tellraw @s {{"text":"List bounds check passed"}};
    }}
    
    tellraw @s {{"text":"Error handling complete"}};
    tellraw @s [{{"text":"Safe value: "}},{{"score":{{"name":"@s","objective":"safe_value"}}}}];
    tellraw @s [{{"text":"Unsafe value: "}},{{"score":{{"name":"@s","objective":"unsafe_value"}}}}];
}}

// Dynamic variable usage in matches syntax
function "dynamic_matches_demo" {{
    // Set up some variables
    var num min_level = 5;
    var num max_level = 15;
    var num player_level = 10;
    var num required_gold = 100;
    var num player_gold = 75;
    
    // Use variables dynamically in matches syntax
    if "player_level matches min_level.." {{
        if "player_level matches ..max_level" {{
            tellraw @s {{"text":"Player level is within acceptable range"}};
            
            // Check if player has enough gold using variable
            if "player_gold matches required_gold.." {{
                tellraw @s {{"text":"Player has enough gold for upgrade"}};
            }} else {{
                tellraw @s {{"text":"Player needs more gold"}};
                var num gold_needed = required_gold - player_gold;
                tellraw @s [{{"text":"Gold needed: "}},{{"score":{{"name":"@s","objective":"gold_needed"}}}}];
            }}
        }} else {{
            tellraw @s {{"text":"Player level too high"}};
        }}
    }} else {{
        tellraw @s {{"text":"Player level too low"}};
    }}
}}

// Hook the functions into load and tick
on_load "{pack_name}:hello";
on_tick "{pack_name}:hello";
on_tick "{pack_name}:variable_demo";
on_tick "{pack_name}:conditional_demo";
on_tick "{pack_name}:weapon_effects";
on_tick "{pack_name}:loop_demo";
on_tick "{pack_name}:calculate_fibonacci";
on_tick "{pack_name}:process_data";
on_tick "{pack_name}:error_handling";
on_tick "{pack_name}:dynamic_matches_demo";

// Second namespace with cross-namespace calls
namespace "util";

function "helper" {{
    tellraw @s {{"text":"[util:helper] Helping out..."}};
}}

function "boss" {{
    tellraw @s {{"text":"[util:boss] Calling {pack_name} functions"}};
    function {pack_name}:hello;
    function {pack_name}:variable_demo;
    function {pack_name}:loop_demo;
    function util:helper;

// Run boss every tick
on_tick "util:boss";

// Function tag examples
tag function minecraft:load {{
    add {pack_name}:hello;
}}

tag function minecraft:tick {{
    add {pack_name}:hello;
    add {pack_name}:variable_demo;
    add {pack_name}:conditional_demo;
    add {pack_name}:weapon_effects;
    add {pack_name}:loop_demo;
    add {pack_name}:calculate_fibonacci;
    add {pack_name}:process_data;
    add {pack_name}:error_handling;
    add util:boss;

// Data tag examples across registries
tag item {pack_name}:swords {{
    add minecraft:diamond_sword;
    add minecraft:netherite_sword;
    add minecraft:golden_sword;
}}

tag block {pack_name}:glassy {{
    add minecraft:glass;
    add minecraft:tinted_glass;
    add minecraft:white_stained_glass;
}}

// Garbage collection
function "cleanup" {{
    function {pack_name}:garbage_collect;
    tellraw @s {{"text":"Cleanup complete"}};
}}

on_tick "{pack_name}:cleanup";
"""
    # Create the main MDL file with a better name
    mdl_filename = f"{args.name.lower().replace(' ', '_')}.mdl"
    with open(os.path.join(root, mdl_filename), "w", encoding="utf-8") as f:
        f.write(sample.strip() + os.linesep)
    
    # Create a README file
    readme_content = f"""# {args.name}

This is a sample MDL (Minecraft Datapack Language) project.

## Usage

1. Build the datapack:
   ```bash
   mdl build --mdl {mdl_filename} -o dist
   ```

2. Copy the generated `dist` folder to your Minecraft world's `datapacks` directory.

3. Enable the datapack in-game with `/reload` and `/datapack enable`.

## Features

This sample demonstrates:
- Variable declarations and assignments
- List operations
- Control flow (if/else, while, for loops)
- Function calls
- String concatenation
- Arithmetic operations
- And more!

## Files

- `{mdl_filename}` - Main MDL source file
- `dist/` - Generated datapack (after building)
"""
    
    with open(os.path.join(root, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"Created sample project at {root}")
    print(f"Main file: {mdl_filename}")
    print(f"Build with: mdl build --mdl {mdl_filename} -o dist")
def _ast_to_pack(ast: Dict[str, Any], default_pack_format: int) -> Pack:
    """Convert JavaScript-style AST to Pack object."""
    # Extract pack information
    pack_info = ast.get('pack')
    if pack_info:
        pack_name = pack_info.name
        pack_format = pack_info.pack_format
        description = pack_info.description
        min_format = pack_info.min_format.values if pack_info.min_format else None
        max_format = pack_info.max_format.values if pack_info.max_format else None
        min_engine_version = pack_info.min_engine_version
    else:
        pack_name = "Generated Pack"
        pack_format = default_pack_format
        description = ""
        min_format = None
        max_format = None
        min_engine_version = None
    
    # Create pack with all metadata
    pack = Pack(
        name=pack_name,
        description=description,
        pack_format=pack_format,
        min_format=min_format,
        max_format=max_format,
        min_engine_version=min_engine_version
    )
    
    # Add garbage collection function
    gc_namespace = pack.namespace("mdl")
    gc_function = gc_namespace.functions.setdefault("garbage_collect", Function("garbage_collect", []))
    gc_function.commands.extend([
        "# Garbage collection for MDL variables",
        "# Clear temporary storage",
        "data remove storage mdl:temp element",
        "data remove storage mdl:temp index",
        "data remove storage mdl:temp last_index",
        "# Reset scoreboard objectives (optional - uncomment if needed)",
        "# scoreboard objectives remove temp dummy",
        "# scoreboard objectives remove temp2 dummy"
    ])
    
    # Process functions by their namespace
    current_namespace = 'minecraft'  # Default namespace
    
    # First, get the current namespace from namespace declarations
    namespaces = ast.get('namespaces', [])
    if namespaces:
        current_namespace = namespaces[-1].name  # Use the last declared namespace
    
    for func in ast.get('functions', []):
        if hasattr(func, 'name'):
            func_name = func.name
            # Use the current namespace (or function-specific namespace if it has one)
            namespace_name = getattr(func, 'namespace', current_namespace)
            ns = pack.namespace(namespace_name)
            
            # Convert function body to commands
            commands = _ast_to_commands(func.body, namespace_name, pack)
            print(f"DEBUG: Generated {len(commands)} commands for {namespace_name}:{func_name}: {commands}")
            if commands:
                # Create function directly without going through old processing pipeline
                fn = ns.functions.setdefault(func_name, Function(func_name, []))
                fn.commands.extend(commands)
                print(f"DEBUG: Function {namespace_name}:{func_name} now has {len(fn.commands)} commands: {fn.commands}")
    
    # Process hooks (on_load, on_tick)
    for hook in ast.get('hooks', []):
        if hook.hook_type == 'load':
            pack.on_load(hook.function_name)
        elif hook.hook_type == 'tick':
            pack.on_tick(hook.function_name)
    
    # Process tags
    for tag in ast.get('tags', []):
        pack.tag(tag.tag_type, tag.name, tag.values)
    
    return pack

def _convert_condition_to_minecraft_syntax(condition: str) -> str:
    """Convert regular comparison operators to Minecraft matches syntax and handle dynamic variable references."""
    processed_condition = condition
    
    # Handle dynamic variable references using @{variable_name} syntax
    # This converts @{var_name} to @s var_name for scoreboard references
    import re
    pattern = r'@\{([^}]+)\}'
    def replace_var_ref(match):
        var_name = match.group(1)
        return f"@s {var_name}"
    
    processed_condition = re.sub(pattern, replace_var_ref, processed_condition)
    
    # Convert comparison operators to matches syntax
    if ">=" in condition:
        # score @s var >= 10 -> score @s var matches 10..
        parts = condition.split(">=")
        if len(parts) == 2:
            left = parts[0].strip()
            right = parts[1].strip()
            processed_condition = f"{left} matches {right}.."
    elif "<=" in condition:
        # score @s var <= 10 -> score @s var matches ..10
        parts = condition.split("<=")
        if len(parts) == 2:
            left = parts[0].strip()
            right = parts[1].strip()
            processed_condition = f"{left} matches ..{right}"
    elif ">" in condition:
        # score @s var > 10 -> score @s var matches 11..
        parts = condition.split(">")
        if len(parts) == 2:
            left = parts[0].strip()
            right = parts[1].strip()
            try:
                num = int(right)
                processed_condition = f"{left} matches {num + 1}.."
            except ValueError:
                # If not a number, keep original
                processed_condition = condition
    elif "<" in condition:
        # score @s var < 10 -> score @s var matches ..9
        parts = condition.split("<")
        if len(parts) == 2:
            left = parts[0].strip()
            right = parts[1].strip()
            try:
                num = int(right)
                processed_condition = f"{left} matches ..{num - 1}"
            except ValueError:
                # If not a number, keep original
                processed_condition = condition
    
    # Convert string quotes for NBT data
    if "data storage" in processed_condition and "'" in processed_condition:
        processed_condition = processed_condition.replace("'", '"')
    
    return processed_condition

def _add_final_command(commands: List[str], final_command: str, execute_prefix: str = ""):
    """Helper function to add final command, splitting on newlines if needed"""
    if '\n' in final_command:
        # Split the command and add each part separately with execute prefix
        parts = final_command.split('\n')
        for part in parts:
            if part.strip():  # Skip empty lines
                if execute_prefix and not part.startswith('#'):
                    commands.append(f"{execute_prefix} {part}")
                else:
                    commands.append(part)
    else:
        if execute_prefix and not final_command.startswith('#'):
            commands.append(f"{execute_prefix} {final_command}")
        else:
            commands.append(final_command)



def _ast_to_commands(body: List[Any], current_namespace: str = "test", current_pack: Any = None, execute_prefix: str = "") -> List[str]:
    """Convert AST function body to list of valid Minecraft commands."""
    print(f"DEBUG: _ast_to_commands called with {len(body)} nodes")
    commands = []
    
    # Performance optimization: Pre-allocate common variables
    temp_var_counter = 0
    
    for i, node in enumerate(body):
        print(f"DEBUG: Processing node {i}: {type(node).__name__}")
        if hasattr(node, '__class__'):
            class_name = node.__class__.__name__
            print(f"DEBUG: Node class: {class_name}")
            
            try:
                if class_name == 'Command':
                    # Remove semicolon from command and clean up
                    command = node.command.rstrip(';').strip()
                    
                    # Skip comments - they should not be converted to execute commands
                    if command.startswith('#'):
                        commands.append(command)
                        continue
                    
                    # Fix tellraw commands with string concatenation
                    if command.startswith('tellraw') and '{"text":"' in command and '+' in command:
                        # Convert string concatenation to proper JSON format
                        # Example: tellraw @s {"text":"Fibonacci(" + n + ") = " + b}
                        # Should become: tellraw @s [{"text":"Fibonacci("},{"score":{"name":"@s","objective":"n"}},{"text":") = "},{"score":{"name":"@s","objective":"b"}}]
                        
                        # Extract the JSON part
                        json_start = command.find('{"text":"')
                        if json_start != -1:
                            json_part = command[json_start:]
                            
                            # Simple fix for common patterns
                            if '+ n +' in json_part:
                                json_part = json_part.replace('+ n +', '","score":{"name":"@s","objective":"n"},"text":"')
                            if '+ b}' in json_part:
                                json_part = json_part.replace('+ b}', '","score":{"name":"@s","objective":"b"}}')
                            if '+ total_score}' in json_part:
                                json_part = json_part.replace('+ total_score}', '","score":{"name":"@s","objective":"total_score"}}')
                            if '+ average_score}' in json_part:
                                json_part = json_part.replace('+ average_score}', '","score":{"name":"@s","objective":"average_score"}}')
                            if '+ highest_score}' in json_part:
                                json_part = json_part.replace('+ highest_score}', '","score":{"name":"@s","objective":"highest_score"}}')
                            if '+ safe_value}' in json_part:
                                json_part = json_part.replace('+ safe_value}', '","score":{"name":"@s","objective":"safe_value"}}')
                            if '+ unsafe_value}' in json_part:
                                json_part = json_part.replace('+ unsafe_value}', '","score":{"name":"@s","objective":"unsafe_value"}}')
                            
                            # Convert to array format
                            if json_part.startswith('{"text":"'):
                                json_part = '[' + json_part.replace('{"text":"', '{"text":"').replace('"}', '"}') + ']'
                            
                            command = command[:json_start] + json_part
                    
                    # Fix say commands with variables
                    if command.startswith('say ') and ':' in command:
                        # Convert say commands with variables to tellraw
                        # Example: say Fibonacci result: b
                        # Should become: tellraw @s [{"text":"Fibonacci result: "},{"score":{"name":"@s","objective":"b"}}]
                        parts = command.split(':')
                        if len(parts) == 2:
                            prefix = parts[0].replace('say ', '').strip()
                            var_name = parts[1].strip()
                            command = f'tellraw @s [{{"text":"{prefix}: "}},{{"score":{{"name":"@s","objective":"{var_name}"}}}}]'
                    
                    if execute_prefix:
                        commands.append(f"{execute_prefix} {command}")
                    else:
                        commands.append(command)
                
                elif class_name == 'FunctionCall':
                    # Convert function call to Minecraft function command
                    function_name = node.function_name
                    commands.append(f"function {function_name}")
                
                elif class_name == 'VariableDeclaration':
                    # Convert variable declarations to scoreboard commands
                    var_type = node.data_type
                    var_name = node.name
                    
                    # Initialize the variable based on type
                    if var_type == 'num':
                        commands.append(f"scoreboard objectives add {var_name} dummy")
                    elif var_type == 'str' and not node.value:
                        # Only initialize empty string if no value is provided
                        # Don't initialize empty strings - they'll be set when needed
                        pass
                    elif var_type == 'list' and not node.value:
                        # Only initialize empty list if no value is provided
                        commands.append(f"data modify storage mdl:variables {var_name} set value []")
                    
                    # Handle the value using expression processor
                    if node.value:
                        processed = expression_processor.process_expression(node.value, var_name)
                        
                        # Apply execute prefix to temp assignments
                        for temp_cmd in processed.temp_assignments:
                            if execute_prefix and not temp_cmd.startswith('#'):
                                commands.append(f"{execute_prefix} {temp_cmd}")
                            else:
                                commands.append(temp_cmd)
                        
                        # If there's a final command, add it with execute prefix
                        if processed.final_command:
                            _add_final_command(commands, processed.final_command, execute_prefix)
                            
                elif class_name == 'VariableAssignment':
                    # Convert variable assignments to appropriate Minecraft commands
                    var_name = node.name
                    
                    # Handle the value using expression processor
                    if node.value:
                        processed = expression_processor.process_expression(node.value, var_name)
                        
                        # Apply execute prefix to temp assignments
                        for temp_cmd in processed.temp_assignments:
                            if execute_prefix and not temp_cmd.startswith('#'):
                                commands.append(f"{execute_prefix} {temp_cmd}")
                            else:
                                commands.append(temp_cmd)
                        
                        # If there's a final command, add it with execute prefix
                        if processed.final_command:
                            _add_final_command(commands, processed.final_command, execute_prefix)
                        
                elif class_name == 'IfStatement':
                    # Convert if statements to Minecraft conditional commands
                    condition = node.condition.strip('"')
                    
                    # Convert condition to proper Minecraft syntax
                    condition = _convert_condition_to_minecraft_syntax(condition)
                    
                    # Convert if body to commands
                    if_commands = _ast_to_commands(node.body, current_namespace, current_pack)
                    
                    # Convert else body to commands (if it exists)
                    else_commands = []
                    if node.else_body:
                        else_commands = _ast_to_commands(node.else_body, current_namespace, current_pack)
                    
                    # Handle different types of conditions
                    if "[" in condition and "==" in condition:
                        # List access comparison - convert to data command
                        # Example: "score @s completed_quests[completed_index] == current_quest" -> "data storage mdl:variables completed_quests[score @s completed_index] matches current_quest"
                        parts = condition.split("==")
                        if len(parts) == 2:
                            left_part = parts[0].strip()
                            right_part = parts[1].strip()
                            
                            if "score @s" in left_part and "[" in left_part:
                                # Extract list name and index
                                list_part = left_part.replace("score @s", "").strip()
                                if "[" in list_part and "]" in list_part:
                                    list_name = list_part.split("[")[0].strip()
                                    index_var = list_part.split("[")[1].split("]")[0].strip()
                                    
                                    # Create data condition for list access
                                    data_condition = f"data storage mdl:variables {list_name}[score @s {index_var}] matches {right_part}"
                                    
                                    # Generate conditional execution
                                    if if_commands:
                                        for cmd in if_commands:
                                            commands.append(f"execute if {data_condition} run {cmd}")
                                    
                                    if else_commands:
                                        for cmd in else_commands:
                                            commands.append(f"execute unless {data_condition} run {cmd}")
                                else:
                                    # Fallback to original condition
                                    if if_commands:
                                        commands.extend(if_commands)
                                    
                                    if else_commands:
                                        commands.extend(else_commands)
                            else:
                                # Fallback to original condition
                                if if_commands:
                                    
                                    for cmd in if_commands:
                                        commands.append(f"execute if {condition} run {cmd}")
                                
                                if else_commands:
                                    
                                    for cmd in else_commands:
                                        commands.append(f"execute unless {condition} run {cmd}")
                        else:
                            # Fallback to original condition
                            if if_commands:
                                
                                for cmd in if_commands:
                                    commands.append(f"execute if {condition} run {cmd}")
                            
                            if else_commands:
                                
                                for cmd in else_commands:
                                    commands.append(f"execute unless {condition} run {cmd}")
                    elif "==" in condition and "'" in condition:
                        # String comparison - convert to data command
                        # Example: "score @s current_quest == 'kill_zombies'" -> "data storage mdl:variables current_quest matches 'kill_zombies'"
                        parts = condition.split("==")
                        if len(parts) == 2:
                            left_part = parts[0].strip()
                            right_part = parts[1].strip().strip("'")
                            
                            if "score @s" in left_part:
                                var_name = left_part.replace("score @s", "").strip()
                                data_condition = f"data storage mdl:variables {var_name} matches \"{right_part}\""
                                
                                # Generate conditional execution
                                if if_commands:
                                    
                                    for cmd in if_commands:
                                        commands.append(f"execute if {data_condition} run {cmd}")
                                
                                if else_commands:
                                    
                                    for cmd in else_commands:
                                        commands.append(f"execute unless {data_condition} run {cmd}")
                            else:
                                # Fallback to original condition
                                if if_commands:
                                    
                                    for cmd in if_commands:
                                        commands.append(f"execute if {condition} run {cmd}")
                                
                                if else_commands:
                                    
                                    for cmd in else_commands:
                                        commands.append(f"execute unless {condition} run {cmd}")
                        else:
                            # Fallback to original condition
                            if if_commands:
                                
                                for cmd in if_commands:
                                    commands.append(f"execute if {condition} run {cmd}")
                            
                            if else_commands:
                                
                                for cmd in else_commands:
                                    commands.append(f"execute unless {condition} run {cmd}")
                    else:
                        # Regular scoreboard condition - use the already converted condition
                        if if_commands:
                            for cmd in if_commands:
                                commands.append(f"execute if {condition} run {cmd}")
                        
                        if else_commands:
                            for cmd in else_commands:
                                commands.append(f"execute unless {condition} run {cmd}")
                        
                elif class_name == 'ForLoop':
                    # Convert for loops to Minecraft iteration commands
                    variable = node.variable
                    selector = node.selector.strip('"')
                    loop_body = _ast_to_commands(node.body, current_namespace, current_pack)
                
                    # Generate loop commands
                    
                    for cmd in loop_body:
                        commands.append(f"execute as {selector} run {cmd}")
                        
                elif class_name == 'ForInLoop':
                    # Convert for-in loops to Minecraft list iteration commands
                    variable = node.variable
                    list_name = node.list_name
                    loop_body = _ast_to_commands(node.body, current_namespace, current_pack)

                    
                    commands.append(f"execute store result storage mdl:temp list_length int 1 run data get storage mdl:variables {list_name}")
                    commands.append(f"execute if data storage mdl:variables {list_name} run function {current_namespace}:for_in_{variable}_{list_name}")

                    # Generate the loop body function
                    loop_func_name = f"for_in_{variable}_{list_name}"
                    loop_func_commands = []

                    # Add loop initialization
                    loop_func_commands.append(f"# Initialize loop index")
                    loop_func_commands.append(f"scoreboard players set @s loop_index 0")

                    # Add loop condition and body
                    loop_func_commands.append(f"# Loop condition")
                    loop_func_commands.append(f"execute if score @s loop_index matches ..@{list_name}_length run function {current_namespace}:for_in_body_{variable}_{list_name}")

                    # Generate the loop body function
                    body_func_name = f"for_in_body_{variable}_{list_name}"
                    body_commands = []

                    # Get current element and store it in a variable
                    body_commands.append(f"# Get current element")
                    body_commands.append(f"data modify storage mdl:temp current_element set from storage mdl:variables {list_name}[score @s loop_index]")

                    # Replace variable references in loop body
                    for cmd in loop_body:
                        modified_cmd = cmd.replace(f"@{variable}", "storage mdl:temp current_element")
                        body_commands.append(modified_cmd)

                    # Increment loop index and continue
                    body_commands.append(f"# Increment index and continue")
                    body_commands.append(f"scoreboard players add @s loop_index 1")
                    body_commands.append(f"execute if score @s loop_index matches ..@{list_name}_length run function {current_namespace}:for_in_body_{variable}_{list_name}")

                    # Store the functions for later generation
                    if not hasattr(current_pack, 'loop_functions'):
                        current_pack.loop_functions = {}
                    current_pack.loop_functions[loop_func_name] = loop_func_commands
                    current_pack.loop_functions[body_func_name] = body_commands
                    
                elif class_name == 'WhileLoop':
                    # Convert while loops to Minecraft conditional commands
                    loop_body = _ast_to_commands(node.body, current_namespace, current_pack)
                    
                    # Handle condition expression
                    if hasattr(node.condition, 'condition_string'):
                        # ConditionExpression - parse the condition string to handle length() functions
                        condition_string = node.condition.condition_string
                        
                        # Check if the condition contains length() function calls
                        if 'length(' in condition_string:
                            # Parse the condition to extract list names and build proper condition
                            # Example: "score @s index < length(items)" -> "score @s index < @s items_length"
                            
                            # Find all length() function calls in the condition
                            import re
                            length_pattern = r'length\(([^)]+)\)'
                            matches = re.findall(length_pattern, condition_string)
                            
                            # Replace each length() call with the corresponding score
                            modified_condition = condition_string
                            for list_name in matches:
                                # Add length calculation before the loop
                                commands.append(f"# Calculate length of {list_name}")
                                commands.append(f"execute store result score @s {list_name}_length run data get storage mdl:variables {list_name}")
                                
                                # Replace length(list_name) with @s list_name_length
                                modified_condition = modified_condition.replace(f'length({list_name})', f'@s {list_name}_length')
                            
                            condition_str = modified_condition
                        else:
                            # No length() functions, use condition as-is
                            condition_str = condition_string
                    else:
                        # Fallback for other expression types
                        condition_str = str(node.condition)
                    
                    # Generate loop commands
                    for cmd in loop_body:
                        commands.append(f"execute if {condition_str} run {cmd}")
                    
                elif class_name == 'BreakStatement':
                    # Handle break statements in loops
                    commands.append(f"# Break statement - exit current loop")
                    commands.append(f"execute unless score @s break_flag matches 1.. run scoreboard players set @s break_flag 1")
                
                elif class_name == 'ContinueStatement':
                    # Handle continue statements in loops
                    commands.append(f"# Continue statement - skip to next iteration")
                    commands.append(f"execute unless score @s continue_flag matches 1.. run scoreboard players set @s continue_flag 1")
                
                elif class_name == 'ReturnStatement':
                    # Convert return statements to Minecraft commands
                    if hasattr(node, 'value') and node.value:
                        if hasattr(node.value, 'value'):
                            return_value = node.value.value
                            commands.append(f"# Return value: {return_value}")
                        else:
                            commands.append(f"# Return statement")
                    else:
                        commands.append(f"# Return (no value)")
                    
                elif class_name == 'ListAccessExpression':
                    # Convert list access to Minecraft NBT commands
                    list_name = node.list_name
                    if hasattr(node.index, 'value'):
                        index = node.index.value
                        # Comment removed to avoid Command node generation
                        commands.append(f"execute store result storage mdl:temp index int 1 run scoreboard players get @s {index}")
                        commands.append(f"data modify storage mdl:temp element set from storage mdl:variables {list_name}[storage mdl:temp index]")
                    elif hasattr(node.index, 'name'):
                        # Variable index
                        index_var = node.index.name
                        # Comment removed to avoid Command node generation
                        commands.append(f"execute store result storage mdl:temp index int 1 run scoreboard players get @s {index_var}")
                        commands.append(f"data modify storage mdl:temp element set from storage mdl:variables {list_name}[storage mdl:temp index]")
                    else:
                        # Comment removed to avoid Command node generation
                        commands.append(f"data modify storage mdl:temp element set from storage mdl:variables {list_name}[0]")
                        
                elif class_name == 'BuiltInFunctionCall':
                    # Handle built-in function calls like length(list_name)
                    if node.function_name == 'length' and len(node.arguments) == 1:
                        # Handle length(list_name) function call
                        list_name = node.arguments[0].name if hasattr(node.arguments[0], 'name') else str(node.arguments[0])
                        # Comment removed to avoid Command node generation
                        commands.append(f"execute store result score @s {list_name}_length run data get storage mdl:variables {list_name}")
                        # Comment removed to avoid Command node generation
                        commands.append(f"scoreboard players operation @s list_length = @s {list_name}_length")
                    else:
                        # Unknown built-in function - skip
                        continue
                
                elif class_name == 'ListAppendOperation':
                    # Convert list append operations to Minecraft NBT commands
                    list_name = node.list_name
                    if hasattr(node.value, 'value'):
                        # Handle string literals
                        if hasattr(node.value, 'type') and node.value.type == 'string':
                            value = node.value.value.strip('"')
                            commands.append(f"data modify storage mdl:variables {list_name} append value \"{value}\"")
                        elif hasattr(node.value, 'type') and node.value.type == 'number':
                            value = node.value.value
                            commands.append(f"data modify storage mdl:variables {list_name} append value {value}")
                        else:
                            # Try to determine type from value
                            try:
                                value = int(node.value.value)
                                commands.append(f"data modify storage mdl:variables {list_name} append value {value}")
                            except (ValueError, TypeError):
                                # Assume string
                                value = node.value.value.strip('"')
                                commands.append(f"data modify storage mdl:variables {list_name} append value \"{value}\"")
                    else:
                        # Unknown value type - skip
                        continue
                        
                elif class_name == 'ListRemoveOperation':
                    # Convert list remove operations to Minecraft NBT commands
                    list_name = node.list_name
                    if hasattr(node.value, 'value'):
                        # Handle string literals
                        if hasattr(node.value, 'type') and node.value.type == 'string':
                            value = node.value.value.strip('"')
                            # Use a temporary storage to find and remove the item
                            commands.append(f"# Remove '{value}' from {list_name}")
                            commands.append(f"execute store result storage mdl:temp index int 1 run data get storage mdl:variables {list_name}")
                            commands.append(f"execute if data storage mdl:variables {list_name}[{{value:\"{value}\"}}] run data remove storage mdl:variables {list_name}[{{value:\"{value}\"}}]")
                        elif hasattr(node.value, 'type') and node.value.type == 'number':
                            value = node.value.value
                            commands.append(f"# Remove {value} from {list_name}")
                            commands.append(f"execute if data storage mdl:variables {list_name}[{{value:{value}}}] run data remove storage mdl:variables {list_name}[{{value:{value}}}]")
                        else:
                            # Try to determine type from value
                            try:
                                value = int(node.value.value)
                                commands.append(f"# Remove {value} from {list_name}")
                                commands.append(f"execute if data storage mdl:variables {list_name}[{{value:{value}}}] run data remove storage mdl:variables {list_name}[{{value:{value}}}]")
                            except (ValueError, TypeError):
                                # Assume string
                                value = node.value.value.strip('"')
                                commands.append(f"# Remove '{value}' from {list_name}")
                                commands.append(f"execute if data storage mdl:variables {list_name}[{{value:\"{value}\"}}] run data remove storage mdl:variables {list_name}[{{value:\"{value}\"}}]")
                    else:
                        # Unknown value type - skip
                        continue
                        
                elif class_name == 'ListInsertOperation':
                    # Convert list insert operations to Minecraft NBT commands
                    list_name = node.list_name
                    if hasattr(node.index, 'value') and hasattr(node.value, 'value'):
                        index = node.index.value
                        if hasattr(node.value, 'type') and node.value.type == 'string':
                            value = node.value.value.strip('"')
                            # Comment removed to avoid Command node generation
                            commands.append(f"data modify storage mdl:variables {list_name} insert {index} value \"{value}\"")
                        elif hasattr(node.value, 'type') and node.value.type == 'number':
                            value = node.value.value
                            # Comment removed to avoid Command node generation
                            commands.append(f"data modify storage mdl:variables {list_name} insert {index} value {value}")
                        else:
                            # Try to determine type from value
                            try:
                                value = int(node.value.value)
                                # Comment removed to avoid Command node generation
                                commands.append(f"data modify storage mdl:variables {list_name} insert {index} value {value}")
                            except (ValueError, TypeError):
                                # Assume string
                                value = node.value.value.strip('"')
                                # Comment removed to avoid Command node generation
                                commands.append(f"data modify storage mdl:variables {list_name} insert {index} value \"{value}\"")
                    else:
                        # Unknown value type - skip
                        continue
                        
                elif class_name == 'ListPopOperation':
                    # Convert list pop operations to Minecraft NBT commands
                    list_name = node.list_name
                    # Comment removed to avoid Command node generation
                    # Use a simpler approach: just remove the last element without specifying index
                    commands.append(f"execute if data storage mdl:variables {list_name} run data remove storage mdl:variables {list_name}[-1]")
                    
                elif class_name == 'ListClearOperation':
                    # Convert list clear operations to Minecraft NBT commands
                    list_name = node.list_name
                    # Comment removed to avoid Command node generation
                    commands.append(f"data modify storage mdl:variables {list_name} set value []")
                
                else:
                    # Unknown node type - skip for now
                    continue
                    
            except Exception as e:
                print(f"ERROR: Failed to process node {i} of type {class_name}: {str(e)}")
                # Error comment removed to avoid Command node generation
                continue
                
    return commands

def _convert_arithmetic_expression(var_name: str, expr: Any) -> List[str]:
    """Convert arithmetic expressions to Minecraft scoreboard commands."""
    commands = []
    
    if hasattr(expr, 'operator'):
        op = expr.operator
        left = expr.left
        right = expr.right
        
        # Handle simple cases first
        if op == '+':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                result = left + right
                commands.append(f"scoreboard players set @s {var_name} {result}")
            elif isinstance(left, (int, float)):
                commands.append(f"scoreboard players set @s {var_name} {left}")
                if isinstance(right, (int, float)):
                    commands.append(f"scoreboard players add @s {var_name} {right}")
            elif isinstance(right, (int, float)):
                commands.append(f"scoreboard players set @s {var_name} {right}")
                if isinstance(left, (int, float)):
                    commands.append(f"scoreboard players add @s {var_name} {left}")
            else:
                # Both are variables - use operation
                commands.append(f"scoreboard players operation @s {var_name} = @s {left}")
                commands.append(f"scoreboard players add @s {var_name} {right}")
        elif op == '-':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                result = left - right
                commands.append(f"scoreboard players set @s {var_name} {result}")
            elif isinstance(left, (int, float)):
                commands.append(f"scoreboard players set @s {var_name} {left}")
                if isinstance(right, (int, float)):
                    commands.append(f"scoreboard players remove @s {var_name} {right}")
            elif isinstance(right, (int, float)):
                commands.append(f"scoreboard players set @s {var_name} {left}")
                commands.append(f"scoreboard players remove @s {var_name} {right}")
            else:
                commands.append(f"scoreboard players operation @s {var_name} = @s {left}")
                commands.append(f"scoreboard players remove @s {var_name} {right}")
        elif op == '*':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                result = left * right
                commands.append(f"scoreboard players set @s {var_name} {result}")
            else:
                # For complex multiplication, set to 0 for now
                commands.append(f"scoreboard players set @s {var_name} 0")
        elif op == '/':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)) and right != 0:
                result = left // right  # Integer division
                commands.append(f"scoreboard players set @s {var_name} {result}")
            else:
                commands.append(f"scoreboard players set @s {var_name} 0")
        elif op == '%':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)) and right != 0:
                result = left % right  # Modulo
                commands.append(f"scoreboard players set @s {var_name} {result}")
            elif isinstance(left, (int, float)) and hasattr(right, 'name'):
                # Constant % variable
                commands.append(f"scoreboard players set @s {var_name} {left}")
                commands.append(f"execute store result storage mdl:temp remainder int 1 run scoreboard players get @s {right.name}")
                commands.append(f"execute if score @s {right.name} matches 0.. run scoreboard players set @s {var_name} 0")
                commands.append(f"execute unless score @s {right.name} matches 0.. run scoreboard players operation @s {var_name} %= @s {right.name}")
            elif hasattr(left, 'name') and isinstance(right, (int, float)):
                # Variable % constant
                if right != 0:
                    commands.append(f"scoreboard players operation @s {var_name} = @s {left.name}")
                    commands.append(f"scoreboard players set @s temp_mod {right}")
                    commands.append(f"scoreboard players operation @s {var_name} %= @s temp_mod")
                else:
                    commands.append(f"scoreboard players set @s {var_name} 0")
            elif hasattr(left, 'name') and hasattr(right, 'name'):
                # Variable % variable
                commands.append(f"scoreboard players operation @s {var_name} = @s {left.name}")
                commands.append(f"scoreboard players operation @s {var_name} %= @s {right.name}")
            else:
                commands.append(f"scoreboard players set @s {var_name} 0")
        else:
            # Unknown operator, set to 0
            commands.append(f"scoreboard players set @s {var_name} 0")
    else:
        # Simple value assignment
        if isinstance(expr, (int, float)):
            commands.append(f"scoreboard players set @s {var_name} {expr}")
        else:
            commands.append(f"scoreboard players set @s {var_name} 0")
    
    return commands

def _convert_string_expression(var_name: str, expr: Any) -> List[str]:
    """Convert string expressions to Minecraft NBT commands."""
    commands = []
    
    if hasattr(expr, 'operator') and expr.operator == '+':
        # String concatenation
        left = expr.left
        right = expr.right
        
        if isinstance(left, str) and isinstance(right, str):
            result = left.strip('"') + right.strip('"')
            commands.append(f"data modify storage mdl:variables {var_name} set value \"{result}\"")
        elif isinstance(left, str):
            left_val = left.strip('"')
            commands.append(f"data modify storage mdl:variables {var_name} set value \"{left_val}\"")
        elif isinstance(right, str):
            right_val = right.strip('"')
            commands.append(f"data modify storage mdl:variables {var_name} set value \"{right_val}\"")
        else:
            commands.append(f"data modify storage mdl:variables {var_name} set value \"\"")
    else:
        # Simple string assignment
        if isinstance(expr, str):
            value = expr.strip('"')
            commands.append(f"data modify storage mdl:variables {var_name} set value \"{value}\"")
        else:
            commands.append(f"data modify storage mdl:variables {var_name} set value \"\"")
    
    return commands

def _determine_wrapper(pack: Pack, override: str | None):
    if override:
        return override
    if pack.namespaces:
        return next(iter(pack.namespaces.keys()))
    return _slug(pack.name)

def cmd_build(args):
    out_root = os.path.abspath(args.out)
    ensure_dir(out_root)

    # Resolve pack: from --mdl/--src or --py-module
    pack = None
    if args.mdl or args.src:
        path = args.mdl or args.src
        files = _gather_mdl_files(path)
        pack = _parse_many(files, default_pack_format=args.pack_format, verbose=args.verbose)
    else:
        # from python module path containing a function create_pack()
        sys.path.insert(0, os.path.abspath("."))
        mod = __import__(args.py_module)
        if not hasattr(mod, "create_pack"):
            raise SystemExit("Python module must expose create_pack() -> Pack")
        pack = mod.create_pack()

    wrapper = _determine_wrapper(pack, args.wrapper)
    wrapped_dir = os.path.join(out_root, wrapper)
    if os.path.exists(wrapped_dir):
        shutil.rmtree(wrapped_dir)
    os.makedirs(wrapped_dir, exist_ok=True)

    pack.build(wrapped_dir)

    zip_path = f"{wrapped_dir}.zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)
    _zip_dir(wrapped_dir, zip_path)

    print(f"Built datapack at {wrapped_dir}")
    print(f"Zipped datapack at {zip_path}")

def cmd_check(args):
    errors = []
    try:
        path = args.path
        if os.path.isdir(path):
            # Use the same multi-file logic as build command
            files = _gather_mdl_files(path)
            try:
                _parse_many(files, default_pack_format=args.pack_format, verbose=args.verbose)
            except Exception as e:
                # Try to extract filename and line info from the error
                error_str = str(e)
                if ":" in error_str:
                    # Format: "filename: error message" or "filename: Line N: error message"
                    parts = error_str.split(":", 2)
                    if len(parts) >= 2:
                        file_path = parts[0]
                        if len(parts) >= 3 and "Line" in parts[1]:
                            # "Line N: error message" format
                            line_match = re.search(r'Line (\d+):\s*(.*)', parts[1] + ":" + parts[2])
                            if line_match:
                                errors.append({"file": file_path, "line": int(line_match.group(1)), "message": line_match.group(2)})
                            else:
                                errors.append({"file": file_path, "line": None, "message": parts[2]})
                        else:
                            # "error message" format
                            errors.append({"file": file_path, "line": None, "message": parts[1]})
                    else:
                        errors.append({"file": path, "line": None, "message": error_str})
                else:
                    errors.append({"file": path, "line": None, "message": error_str})
        else:
            # Single file - parse individually
            with open(path, "r", encoding="utf-8") as f:
                src = f.read()
            ast = parse_mdl_js(src)
            # Convert AST to Pack for validation
            _ast_to_pack(ast, args.pack_format)
    except Exception as e:
        # For top-level failures
        m = re.search(r'Line (\d+):\s*(.*)', str(e))
        if m:
            errors.append({"file": path, "line": int(m.group(1)), "message": m.group(2)})
        else:
            errors.append({"file": path, "line": None, "message": str(e)})

    if args.json:
        print(json.dumps({"ok": len(errors) == 0, "errors": errors}, indent=2))
        return 0 if not errors else 1

    if errors:
        for err in errors:
            loc = f"{err['file']}"
            if err["line"]:
                loc += f":{err['line']}"
            print(f"ERROR {loc} -> {err['message']}")
        return 1
    else:
        print("OK")
        return 0

def cmd_check_advanced(args):
    """Advanced linting that builds the project and analyzes generated mcfunction files"""
    import tempfile
    import shutil
    
    # Create temporary output directory if not specified
    output_dir = args.output_dir
    temp_dir = None
    if not output_dir:
        temp_dir = tempfile.mkdtemp(prefix="mdl_lint_")
        output_dir = temp_dir
    
    try:
        # First, build the project to generate mcfunction files
        if args.verbose:
            print(f"🔨 Building project to generate mcfunction files...")
        
        # Create a temporary build command
        build_args = argparse.Namespace()
        build_args.mdl = args.path
        build_args.src = None
        build_args.py_module = None
        build_args.out = output_dir
        build_args.pack_format = args.pack_format
        build_args.wrapper = None
        build_args.verbose = args.verbose
        
        # Build the project
        cmd_build(build_args)
        
        if args.verbose:
            print(f"✅ Build completed. Analyzing generated files...")
        
        # Find the generated datapack directory
        datapack_dir = None
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "pack.mcmeta")):
                datapack_dir = item_path
                break
        
        if not datapack_dir:
            print("❌ No datapack directory found in output")
            return 1
        
        # Run Mecha validation on all mcfunction files
        mecha_results = {}
        mecha_errors = 0
        
        if args.verbose:
            print(f"🔍 Running Mecha validation...")
        
        # Find all mcfunction files
        mcfunction_files = []
        for root, dirs, files in os.walk(datapack_dir):
            for file in files:
                if file.endswith('.mcfunction'):
                    mcfunction_files.append(os.path.join(root, file))
        
        for mcfunction_file in mcfunction_files:
            try:
                # Run Mecha on the file
                import subprocess
                result = subprocess.run(
                    ['mecha', mcfunction_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    # Check if this is a false positive from Mecha being overly strict
                    output = result.stdout + result.stderr
                    
                    # Ignore Mecha errors about nested execute commands (these are valid Minecraft syntax)
                    if "Expected eof, literal 'align', literal 'anchored', literal 'as', literal 'at', literal 'facing' or 10 other tokens but got literal 'execute'" in output:
                        # This is a false positive - nested execute commands are valid Minecraft syntax
                        mecha_results[mcfunction_file] = "IGNORED: Mecha false positive - nested execute commands are valid Minecraft syntax"
                    elif "Expected eof, literal 'align', literal 'anchored', literal 'as', literal 'at', literal 'facing' or 10 other tokens but got literal 'scoreboard'" in output:
                        # This is also a false positive - execute if score ... run scoreboard ... is valid syntax
                        mecha_results[mcfunction_file] = "IGNORED: Mecha false positive - execute if score ... run scoreboard ... is valid Minecraft syntax"
                    elif "Expected eof, literal 'align', literal 'anchored', literal 'as', literal 'at', literal 'facing' or 10 other tokens but got literal 'tellraw'" in output:
                        # This is also a false positive - execute if score ... run tellraw ... is valid syntax
                        mecha_results[mcfunction_file] = "IGNORED: Mecha false positive - execute if score ... run tellraw ... is valid Minecraft syntax"
                    else:
                        # This is a real error
                        mecha_errors += 1
                        mecha_results[mcfunction_file] = output
                    
            except subprocess.TimeoutExpired:
                mecha_results[mcfunction_file] = "Mecha validation timed out"
                mecha_errors += 1
            except FileNotFoundError:
                mecha_results[mcfunction_file] = "Mecha not found - please ensure mecha is installed"
                mecha_errors += 1
            except Exception as e:
                mecha_results[mcfunction_file] = f"Mecha validation error: {str(e)}"
                mecha_errors += 1
        
        # Also run our custom linter for additional checks
        lint_results = lint_mcfunction_directory(datapack_dir)
        
        # Process results
        all_issues = []
        total_files = len(mcfunction_files)
        files_with_issues = 0
        
        for file_path, issues in lint_results.items():
            if issues:
                files_with_issues += 1
                all_issues.extend(issues)
        
        # Generate report
        if args.json:
            # JSON output
            report = {
                "summary": {
                    "total_files": total_files,
                    "files_with_issues": files_with_issues,
                    "total_issues": len(all_issues),
                    "errors": len([i for i in all_issues if i.severity == 'error']),
                    "warnings": len([i for i in all_issues if i.severity == 'warning']),
                    "info": len([i for i in all_issues if i.severity == 'info'])
                },
                "mecha_validation": {
                    "files_with_errors": mecha_errors,
                    "errors": {os.path.relpath(k, output_dir): v for k, v in mecha_results.items()}
                },
                "files": {}
            }
            
            for file_path, issues in lint_results.items():
                rel_path = os.path.relpath(file_path, output_dir)
                report["files"][rel_path] = [
                    {
                        "line": issue.line_number,
                        "severity": issue.severity,
                        "category": issue.category,
                        "message": issue.message,
                        "suggestion": issue.suggestion,
                        "command": issue.command
                    }
                    for issue in issues
                ]
            
            print(json.dumps(report, indent=2))
        else:
            # Human-readable output
            print(f"📊 Advanced Linting Report")
            print(f"=" * 50)
            print(f"📁 Files analyzed: {total_files}")
            print(f"⚠️  Files with custom linter issues: {files_with_issues}")
            print(f"📝 Total custom linter issues: {len(all_issues)}")
            print(f"🔍 Files with Mecha validation errors: {mecha_errors}")
            
            # Show Mecha validation results
            if mecha_results:
                print(f"\n❌ Mecha Validation Errors:")
                for file_path, error_output in mecha_results.items():
                    rel_path = os.path.relpath(file_path, output_dir)
                    print(f"\n📄 {rel_path}")
                    print("-" * 40)
                    print(error_output)
            else:
                print(f"\n✅ All files passed Mecha validation!")
            
            if all_issues:
                error_count = len([i for i in all_issues if i.severity == 'error'])
                warning_count = len([i for i in all_issues if i.severity == 'warning'])
                info_count = len([i for i in all_issues if i.severity == 'info'])
                
                print(f"❌ Errors: {error_count}")
                print(f"⚠️  Warnings: {warning_count}")
                print(f"ℹ️  Info: {info_count}")
                print()
                
                # Show issues by file
                for file_path, issues in lint_results.items():
                    if issues:
                        rel_path = os.path.relpath(file_path, output_dir)
                        print(f"📄 {rel_path}")
                        print("-" * 40)
                        
                        for issue in issues:
                            severity_icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[issue.severity]
                            print(f"{severity_icon} Line {issue.line_number}: {issue.message}")
                            if issue.suggestion:
                                print(f"   💡 {issue.suggestion}")
                            if issue.command:
                                cmd_preview = issue.command[:60] + "..." if len(issue.command) > 60 else issue.command
                                print(f"   📝 {cmd_preview}")
                            print()
            else:
                print("✅ No linting issues found!")
        
        # Return appropriate exit code
        has_custom_errors = any(issue.severity == 'error' for issues in lint_results.values() for issue in issues)
        has_mecha_errors = mecha_errors > 0
        return 1 if (has_custom_errors or has_mecha_errors) else 0
        
    except Exception as e:
        print(f"❌ Error during advanced linting: {e}")
        if args.verbose:
            traceback.print_exc()
        return 1
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def main(argv=None):
    p = argparse.ArgumentParser(prog="mdl", description="Minecraft Datapack Language (compiler)")
    
    # Add version argument
    p.add_argument("--version", action="version", version="%(prog)s " + __version__)
    
    sub = p.add_subparsers(dest="cmd", required=True)

    p_new = sub.add_parser("new", help="Create a sample .mdl project")
    p_new.add_argument("path")
    p_new.add_argument("--name", default="Minecraft Datapack Language")
    p_new.add_argument("--pack-format", type=int, default=82, help="Pack format (default: 82 for modern)")
    p_new.set_defaults(func=cmd_new)

    p_build = sub.add_parser("build", help="Build a datapack")
    g = p_build.add_mutually_exclusive_group(required=True)
    g.add_argument("--mdl", help="Path to .mdl source (file or directory)")
    g.add_argument("--src", help="Path to .mdl source (file or directory)")
    g.add_argument("--py-module", help="Python module path exposing create_pack() -> Pack")
    p_build.add_argument("-o", "--out", required=True, help="Output folder (MDL creates <out>/<wrapper>/ and <out>/<wrapper>.zip)")
    p_build.add_argument("--pack-format", type=int, default=82, help="Pack format (default: 82 for modern)")
    p_build.add_argument("--wrapper", help="Wrapper folder/zip name (default: first namespace or slug of pack name)")
    p_build.add_argument("-v", "--verbose", action="store_true", help="Show detailed processing information")
    p_build.set_defaults(func=cmd_build)

    p_check = sub.add_parser("check", help="Validate .mdl (file or directory)")
    p_check.add_argument("path", help="Path to .mdl file or directory")
    p_check.add_argument("--pack-format", type=int, default=82, help="Pack format (default: 82 for modern)")
    p_check.add_argument("--json", action="store_true", help="Emit JSON diagnostics")
    p_check.add_argument("-v", "--verbose", action="store_true")
    p_check.set_defaults(func=cmd_check)

    p_check_advanced = sub.add_parser("check-advanced", help="Advanced linting of generated mcfunction files")
    p_check_advanced.add_argument("path", help="Path to .mdl file or directory")
    p_check_advanced.add_argument("--pack-format", type=int, default=82, help="Pack format (default: 82 for modern)")
    p_check_advanced.add_argument("--output-dir", help="Output directory for generated files (default: temp)")
    p_check_advanced.add_argument("--json", action="store_true", help="Emit JSON diagnostics")
    p_check_advanced.add_argument("-v", "--verbose", action="store_true")
    p_check_advanced.set_defaults(func=cmd_check_advanced)

    args = p.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
