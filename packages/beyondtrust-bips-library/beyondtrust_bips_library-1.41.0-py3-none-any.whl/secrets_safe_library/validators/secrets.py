from secrets_safe_library.constants.versions import Version
from secrets_safe_library.validators.base import BaseValidator


class _SecretSchemaValidator:
    def __init__(self):
        self.common_schema = {
            "Title": {
                "type": "string",
                "maxlength": 256,
                "minlength": 1,
                "required": True,
            },
            "Description": {"type": "string", "maxlength": 256, "nullable": True},
            "Notes": {"type": "string", "maxlength": 4000, "nullable": True},
            "Urls": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "Id": {"type": "string"},
                        "CredentialId": {"type": "string"},
                        "Url": {"type": "string"},
                    },
                },
                "nullable": True,
            },
        }

        self.owners_v30 = {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "OwnerId": {"type": "integer", "required": True},
                    "Owner": {"type": "string", "required": False, "nullable": True},
                    "Email": {"type": "string", "required": False, "nullable": True},
                },
            },
            "required": True,
        }

        self.owners_v31 = {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "GroupId": {"type": "integer"},
                    "UserId": {"type": "integer", "required": True},
                    "Name": {"type": "string", "required": False, "nullable": True},
                    "Email": {"type": "string", "required": False, "nullable": True},
                },
            },
            "required": True,
        }

    def get_create_secret_schema(self, version: str, operation: str) -> dict:
        """
        Retrieve the schema for the specified operation and version.

        Args:
            operation (str): The operation type (e.g., 'create_credential_secret',
                'create_text_secret', 'create_file_secret').
            version (str): The version (e.g., '3.0', '3.1', '3.2', '3.3', 'DEFAULT')

        Returns:
            dict: The schema for the specified operation and version.
        """

        if operation == "create_credential_secret":
            self.common_schema.update(
                {
                    "Username": {
                        "type": "string",
                        "maxlength": 1000,
                        "minlength": 1,
                        "required": True,
                    },
                    "Password": {
                        "type": "string",
                        "maxlength": 256,
                        "minlength": 1,
                        "required": True,
                    },
                    "PasswordRuleID": {"type": "integer"},
                }
            )

            if version == Version.V3_0.value:
                return {
                    **self.common_schema,
                    "OwnerId": {"type": "integer"},
                    "OwnerType": {"type": "string", "allowed": ["User", "Group"]},
                    "Owners": self.owners_v30,
                }

            elif version == Version.V3_1.value:
                return {**self.common_schema, "Owners": self.owners_v31}

        elif operation == "create_text_secret":
            self.common_schema.update(
                {
                    "Text": {
                        "type": "string",
                        "maxlength": 4096,
                        "minlength": 1,
                        "required": True,
                    },
                }
            )

            if version == Version.V3_0.value:
                return {
                    **self.common_schema,
                    "OwnerId": {"type": "integer"},
                    "OwnerType": {"type": "string", "allowed": ["User", "Group"]},
                    "Owners": self.owners_v30,
                }

            elif version == Version.V3_1.value:
                return {**self.common_schema, "Owners": self.owners_v31}

        elif operation == "create_file_secret":
            self.common_schema.update(
                {
                    "FilePath": {
                        "type": "string",
                        "maxlength": 256,
                        "minlength": 1,
                        "required": True,
                    }
                }
            )

            if version == Version.V3_0.value:
                return {
                    **self.common_schema,
                    "OwnerId": {"type": "integer"},
                    "OwnerType": {"type": "string", "allowed": ["User", "Group"]},
                    "Owners": self.owners_v30,
                }

            elif version == Version.V3_1.value:
                return {**self.common_schema, "Owners": self.owners_v31}

        else:
            raise ValueError(f"Unsupported operation: {operation}")


class SecretsValidator(BaseValidator):
    """Validator for secrets operations."""

    def __init__(self):
        self.schema_validator = _SecretSchemaValidator()

    def get_schema(self, operation: str, version: str = Version.DEFAULT.value) -> dict:
        """
        Retrieve the schema for the specified operation and version.

        Args:
            operation (str): The operation type (e.g., 'create_by_asset',
                'create_by_database', 'create_by_workgroup').
            version (str): The version (e.g., '3.0', '3.1', '3.2', '3.3', 'DEFAULT')

        Returns:
            dict: The schema for the specified operation and version.
        """

        return self.schema_validator.get_create_secret_schema(version, operation)

    def validate(
        self,
        data: dict,
        operation: str,
        version: str = Version.DEFAULT.value,
        allow_unknown: bool = True,
        update: bool = False,
    ) -> dict:
        schema = self.get_schema(operation, version)
        data = super().validate(data, schema, allow_unknown, update)
        return data
