import hashlib
import json
from pydantic import BaseModel, model_validator
from pathlib import Path
import shutil

class Config(BaseModel):


    model_config = {
        "validate_assignment": True,
        "arbitrary_types_allowed": True
    }

    @classmethod
    @model_validator(mode="after")
    def strict_type_check(cls, values):
        def check_field(name, value_, expected_type_):

            if isinstance(expected_type_, type) and not isinstance(value_, expected_type_):
                raise TypeError(
                    f"Invalid value for '{name}': expected {expected_type_.__name__}, got {type(value_).__name__}"
                )

            # Nested BaseModel
            if isinstance(value_, BaseModel):
                for sub_name, sub_value in value_.model_dump().items():
                    sub_type = value_.model_fields[sub_name].annotation
                    check_field(f"{name}.{sub_name}", sub_value, sub_type)

        for field_name, value in values.__dict__.items():
            expected_type = cls.model_fields[field_name].annotation
            check_field(field_name, value, expected_type)

        return values

    def write_to_json_file(self, file_path: str) -> None:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.model_dump_json(indent=2))
            print(f"Successfully wrote config to {file_path}")
        except Exception as e:
            print("Error writing file:", e)

    @property
    def hash(self) -> str:
        data = self.model_dump()
        json_repr = json.dumps(data, sort_keys=True, default=str)
        data_bytes: bytes = json_repr.encode("utf-8")
        return hashlib.sha256(data_bytes).hexdigest()

    @staticmethod
    def copy_file(source: str, destination: str) -> None:
        """
        Copies a file from source to destination.

        Args:
            source (str): Path to the source file.
            destination (str): Path to the target location (can be a folder or a file).
        """
        try:
            src_path = Path(source)
            dest_path = Path(destination)

            if not src_path.exists():
                raise FileNotFoundError(f"Source file does not exist: {source}")

            # If destination is a directory, append the file name
            if dest_path.is_dir():
                dest_path = dest_path / src_path.name

            shutil.copy2(src_path, dest_path)  # preserves metadata (timestamps, etc.)
            print(f"Copied {src_path} to {dest_path}")

        except Exception as e:
            print(f"Error copying file: {e}")

