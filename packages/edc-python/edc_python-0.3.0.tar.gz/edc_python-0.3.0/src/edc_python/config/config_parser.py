import dataclasses
import sys
import os
from pathlib import Path
from typing import List, Type, TypeVar, get_origin, get_args, get_type_hints
from configargparse import get_arg_parser, YAMLConfigFileParser, _parsers
# from functools import lru_cache

T = TypeVar("T")

def parse_config(config_file_path: Path, config_class: Type[T]) -> T:
    """
    Reads defaults from dataclass, overwrites them with values from:
      - YAML config file
      - CLI-flags (--fieldname)
    :return: An instance of config_class
    """
    # Create parser for YAML-config files
    parser = get_arg_parser(_get_app_name(), default_config_files=[config_file_path], config_file_parser_class=YAMLConfigFileParser)
    # parser = configargparse.ArgParser(default_config_files=[config_file_path])
    # parser.add('-c', '--config', is_config_file=True, help="The connectors config file.")

    type_hints = get_type_hints(config_class, include_extras=False)

    # Automatically register all dataclass-fields
    for fld in dataclasses.fields(config_class):
        name = fld.name
        tp = type_hints.get(name, fld.type)
        default = fld.default if fld.default is not dataclasses.MISSING else None

        # if typ == List[str]:
        #     parser.add(f'--{name}', type=str, nargs='*', default=default)
        # else:
        #     parser.add(f'--{name}', type=typ, default=default)


        arg_name = f"--{name}"
        kwargs = {"default": default, "help": f"{name} (default: {default})"}

        # List-type
        if get_origin(tp) is list:
            inner_type = get_args(tp)[0]
            kwargs.update({"nargs": "*", "type": inner_type})

        # Boolean flags
        elif tp is bool:
            if default is True:
                parser.add_argument(f"--no-{name}", dest=name, action="store_false")
                continue
            else:
                kwargs["action"] = "store_true"

        # Other types (int, float, str, ...)
        else:
            kwargs["type"] = tp

        parser.add_argument(arg_name, **kwargs)

    # Parse - CLI-flags before YAML-values
    args = parser.parse_args()

    # Convert to Dict and inject into dataclass
    args_dict = vars(args)
    return config_class(**args_dict)

# @lru_cache(maxsize=1)
def _get_app_name() -> str:
    """
    The name of the app == The file name without extension of the main executing script.
    :return: The name of the app.
    """
    main_module = sys.modules['__main__']
    module_or_dir_path = getattr(main_module, '__file__', os.getcwd())
    module_or_dir_name = os.path.basename(module_or_dir_path)
    module_or_dir_extensionless, _ = os.path.splitext(module_or_dir_name)
    if module_or_dir_extensionless in _parsers:
        module_or_dir_extensionless = f'{module_or_dir_extensionless}_{len(_parsers)}' # make sure to get a unique parser name
    return module_or_dir_extensionless

# def init_config_with_file_and_classes(config_file_name, *config_class: Type[SupportsAddArgs],
#                                         additional_parser_func: Callable[[ArgumentParser], None] = None) -> Namespace:
#     """
#     Initializes the configuration/arguments system by parsing one config file and mapping it to several config classes.
#     :return: An configargparse namespace (anonymous object) with the config values (as members).
#     Use unpacking to map it to objects as you like.
#     """

#     logging.info(f'Reading config file {config_file_name}...')
#     add_funcs = list([config.add_args for config in config_class])
#     if additional_parser_func:
#         add_funcs.append(additional_parser_func)
#     args = init_config_with_file(config_file_name, *add_funcs)
#     #print(config_file_name)
#     # logging.info(f'Config file args: {args}')

#     configs : List[Union[SupportsAddArgs, Namespace]] 
#     configs = list([from_dict(data_class=config_class, data=args.__dict__) for config_class in config_class])
#     configs.append(args)
#     return tuple(configs)


# db_config, ssh_config, _ = config_parser.init_config_with_file_and_classes('confluence.config.secrets.yaml', DbConfig, SshConfig)