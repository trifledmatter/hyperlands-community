import importlib.util
import glob

async def load_commands(load_extension, commands_directory, commands_loaded):
    commands = glob.glob(f"{commands_directory}/**/*.py", recursive=True)

    for command in commands:
        module_name = command \
            .replace('/', '.') \
            .replace('\\', '.') \
            .removesuffix('.py')
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, command)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            # Check if the module has a 'setup' function
            if hasattr(mod, 'setup'):
                print(f"Found setup in {module_name}")
                await mod.setup(load_extension)  # Load the command using its setup function

                commands_loaded.append({
                    "name": module_name,
                    "loaded": True
                })
            else:
                commands_loaded.append({
                    "name": module_name,
                    "loaded": False
                })
        except Exception as e:
            print(f"Error loading command {module_name}: {e}")
            commands_loaded.append({
                "name": module_name,
                "loaded": False
            })
            continue
