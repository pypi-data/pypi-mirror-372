import contextlib
import importlib.util
import os
import pathlib
from typing import Iterator, Type, TypeVar

from truss_train import definitions
from truss.base.truss_spec import TrussSpec

T = TypeVar("T")


@contextlib.contextmanager
def import_training_project(
    module_path: pathlib.Path,
) -> Iterator[definitions.TrainingProject]:
    with import_target(module_path, definitions.TrainingProject) as project:
        yield project


@contextlib.contextmanager
def import_deploy_checkpoints_config(
    module_path: pathlib.Path,
) -> Iterator[definitions.DeployCheckpointsConfig]:
    with import_target(module_path, definitions.DeployCheckpointsConfig) as config:
        yield config


@contextlib.contextmanager
def import_target(module_path: pathlib.Path, target_type: Type[T]) -> Iterator[T]:
    module_name = module_path.stem
    if not os.path.isfile(module_path):
        raise ImportError(
            f"`{module_path}` is not a file. You must point to a python file where "
            f"the training configuration is defined."
        )

    if module_path.suffix == ".yaml":
        import yaml
        with open(module_path, 'r') as f:
            yaml_content = yaml.safe_load(f)
        try:
            parsed_object = target_type(**yaml_content)
            target = [parsed_object]
        except Exception as e:
            raise ValueError(f"Failed to parse YAML file {module_path} as {target_type.__name__}: {e}")
            
    elif module_path.suffix == ".py":
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if not spec or not spec.loader:
            raise ImportError(f"Could not import `{module_path}`. Check path.")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        module_vars = (getattr(module, name) for name in dir(module))
        target = [sym for sym in module_vars if isinstance(sym, target_type)]

    print(f"Target: {target}")
    if len(target) == 0:
        raise ValueError(f"No `{target_type}` was found.")
    elif len(target) > 1:
        raise ValueError(f"Multiple `{target_type}`s were found.")

    yield target[0]
