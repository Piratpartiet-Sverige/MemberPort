import os
import importlib.util


def get_available_plugins():
    rootdir = './app/plugins'
    plugins = []

    for subdir, dirs, files in os.walk(rootdir):
        if subdir == "./app/plugins" or subdir.count('/') > 3:
            continue
        for file in files:
            if file == "plugin.py":
                plugin_name = os.path.basename(os.path.normpath(subdir))
                plugins.append((os.path.join(subdir, file), plugin_name))

    return plugins

def load_plugins(plugins_paths):
    plugins = []

    for plugin_path, plugin_name in plugins_paths:
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin)
        plugins.append(plugin)

    return plugins
