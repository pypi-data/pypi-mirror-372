import re
from typing import Callable, Generator

from faker import Faker


class Generators:
    """A registry of callable generators that produce synthetic data using Faker or custom generator.

    This class wraps a Faker instance and provides a dictionary-like interface
    to access predefined or custom data generators by name. It supports default
    Faker methods (like 'name', 'email') and allows future extension with custom generators.

    Attributes:
        fake_gen (Faker): The underlying Faker instance used to generate data.
        __generators (dict[str, Callable[..., str]]): A private mapping of generator names to callables.
    """

    def __init__(self, fake_gen: Faker) -> None:
        self.fake_gen: Faker = fake_gen
        self.__generators: dict[str, Callable[..., str]] = {}
        self._register_default_generators()

    def _register_default_generators(self) -> None:
        """Registers default Faker-based generators for common data fields.

        The following Faker methods are registered if available:
        'name', 'first_name', 'last_name', 'email', 'phone', 'city',
        'company', 'job', 'date', 'address'.

        Each method is wrapped in a lambda to ensure correct binding.
        """

        default_faker_methods = [
            "name",
            "first_name",
            "last_name",
            "email",
            "phone",
            "city",
            "company",
            "job",
            "date",
            "address",
        ]
        for method_name in default_faker_methods:
            if hasattr(self.fake_gen, method_name):
                def make_gen(method: str) -> Callable[..., str]:
                    return lambda: getattr(self.fake_gen, method)()

                self.__generators[method_name] = make_gen(method_name)

    def get_generator(self, name: str) -> Callable[..., str]:
        """Returns a callable generator by its name.

        Args:
            name (str): The name of the generator (e.g., 'email', 'city').

        Returns:
            Callable[..., str]: A function that returns a generated string.

        Raises:
            ValueError: If no generator exists with the given name.
        """
        if name not in self.__generators:
            raise ValueError("Invalid generator name")
        return self.__generators.get(name)  # type: ignore

    def has_generator(self, name: str) -> bool:
        """Checks whether a generator with the given name exists.

        Args:
            name (str): The name of the generator to check.

        Returns:
            bool: True if the generator exists, False otherwise.
        """
        return name in self.__generators

    # TODO: template method
    def get_all_generators(self) -> dict[str, Callable[..., str]]:
        return self.__generators

    # TODO: add custom generator option


class LinesGenerator:
    """Generates formatted text lines using a template and fake data.

    This class takes a template string with placeholders (e.g., {name}, {city}),
    replaces them with synthetic data from a Generators instance, and produces one or more lines.

    Attributes:
        line_template (str): The template string with placeholders.
        data_generator (Generators): Instance providing fake data generators.
        line_count (int): Number of lines to generate.
        _template_fields_list (list[str]): List of field names extracted from the template.
    """

    def __init__(self, line_template: str, data_generator: Generators, line_count: int = 1) -> None:
        self.line_template: str = line_template
        self.data_generator: Generators = data_generator
        self.line_count: int = line_count
        self._template_fields_list: list = self._extract_fields(self.line_template)

    def _extract_fields(self, template: str) -> list[str]:
        """Extracts placeholder field names from a template string.

        Supports placeholders in the format {field}, { field }, or {field }.

        Args:
            template (str): The template string containing placeholders.

        Returns:
            list[str]: A list of field names extracted from the template.

        Example:
            >>> self._extract_fields("Hello {name}! You live in { city }?")
            ['name', 'city']
        """
        return re.findall(r"\{\s*([^}]+?)\s*}", template)

    def one_line_generator(self) -> str:
        """Generates a single formatted line by replacing placeholders with fake data.

        For each field in the template:
        - If a generator exists, uses generated data.
        - Otherwise, replaces with 'UNKNOWN_field_[field_name]'.

        Returns:
            str: A fully formatted string with fake or placeholder data.
        """
        generated_data = {}
        for field in self._template_fields_list:
            if self.data_generator.has_generator(field):
                # TODO: add exception
                fake_data = self.data_generator.get_generator(field)()
                generated_data[field] = fake_data
            else:
                generated_data[field] = f"UNKNOWN_field_[{field}]"

        return self.line_template.format(**generated_data)

    def lines_generator(self) -> Generator[str, None, None]:
        """Generates multiple formatted lines lazily (one at a time).

        Yields:
            str: A generated line with fake data, one per iteration.

        Note:
            This is a generator function. Use in a loop or convert to list if needed.
        """
        for _ in range(self.line_count):
            yield self.one_line_generator()

# TODO: add export to file option

