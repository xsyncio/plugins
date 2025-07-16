import re
import typing
import unicodedata
import urllib.parse

T = typing.TypeVar("T")
EMAIL_REGEX: typing.Pattern[str] = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
MAP_KEY: str = "___obmap___"


def chunks(lst: typing.List[T], n: int) -> typing.Iterator[typing.List[T]]:
    """
    Yield successive n-sized chunks from a list.

    Parameters
    ----------
    lst : List[T]
        The list to divide into chunks.
    n : int
        The size of each chunk.

    Returns
    -------
    Iterator[List[T]]
        An iterator over sub-lists of length `n` (the last chunk may be shorter).

    Raises
    ------
    ValueError
        If `n` is not a positive integer.

    Examples
    --------
    >>> list(chunks([1, 2, 3, 4, 5], 2))
    [[1, 2], [3, 4], [5]]
    """
    if n <= 0:
        raise ValueError("Chunk size 'n' must be a positive integer.")
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def find_emails(value: str) -> typing.List[str]:
    """
    Extract unique email-like substrings from a string.

    Parameters
    ----------
    value : str
        The input string to search for email patterns.

    Returns
    -------
    List[str]
        A list of unique email-like strings (no external validation).

    Notes
    -----
    - Uses a basic regex; may not cover all valid email cases.
    - Strips trailing dots if present.

    Examples
    --------
    >>> find_emails("Reach me at user@example.com.")
    ['user@example.com']
    """
    raw_matches: typing.List[str] = EMAIL_REGEX.findall(value)
    cleaned: typing.Set[str] = set()
    for email in raw_matches:
        if email.endswith("."):
            email = email[:-1]
        cleaned.add(email)
    return list(cleaned)


def to_clean_domain(value: str) -> str:
    """
    Normalize a URL or domain string and extract its base domain.

    Parameters
    ----------
    value : str
        A URL or domain (with or without scheme).

    Returns
    -------
    str
        The cleaned base domain (e.g., "example.com" from "https://sub.example.com/path").

    Examples
    --------
    >>> to_clean_domain("example.com/path")
    'example.com'
    >>> to_clean_domain("https://sub.domain.co.uk")
    'domain.co.uk'
    """
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    parsed: urllib.parse.ParseResult = urllib.parse.urlparse(value)
    parts: typing.List[str] = parsed.netloc.split(".")
    if len(parts) > 2:
        parts = parts[-2:]
    return ".".join(parts)


def slugify(value: typing.Any, allow_unicode: bool = False) -> str:
    """
    Convert a string to a URL-friendly slug.

    Parameters
    ----------
    value : Any
        The input value to slugify (will be cast to str).
    allow_unicode : bool, optional
        Whether to allow unicode characters (default is False).

    Returns
    -------
    str
        The slugified string.

    Notes
    -----
    - Collapses whitespace and hyphens.
    - Removes non-word characters.
    - Converts to lowercase.

    Examples
    --------
    >>> slugify("Hello, World!")
    'hello-world'
    >>> slugify("Café Münch", allow_unicode=True)
    'Café-Münch'
    """
    text: str = str(value)
    if allow_unicode:
        text = unicodedata.normalize("NFKC", text)
    else:
        text = (
            unicodedata.normalize("NFKD", text)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-_")


def to_camel_case(value: str) -> str:
    """
    Convert a snake_case or space-separated string to camelCase.

    Parameters
    ----------
    value : str
        The input string (e.g., "my_function_name" or "My Function Name").

    Returns
    -------
    str
        The camelCase version of the string.

    Examples
    --------
    >>> to_camel_case("hello_world")
    'helloWorld'
    """
    parts: typing.List[str] = value.replace(" ", "_").lower().split("_")
    return parts[0] + "".join(word.title() for word in parts[1:])


def to_snake_case(name: str) -> str:
    """
    Convert camelCase or kebab-case string to snake_case.

    Parameters
    ----------
    name : str
        The input string (e.g., "myFunctionName" or "my-function-name").

    Returns
    -------
    str
        The snake_case version of the string.

    Examples
    --------
    >>> to_snake_case("myFunctionName")
    'my_function_name'
    >>> to_snake_case("my-function-name")
    'my_function_name'
    """
    camel: str = to_camel_case(name.replace("-", "_"))
    step1: str = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", camel)
    step2: str = re.sub(r"__+", "_", step1)
    return step2.lower()


@typing.overload
def dkeys_to_snake_case(
    data: typing.Dict[str, typing.Any],
) -> typing.Dict[str, typing.Any]: ...


@typing.overload
def dkeys_to_snake_case(
    data: typing.List[typing.Any],
) -> typing.List[typing.Any]: ...


def dkeys_to_snake_case(
    data: typing.Union[typing.Dict[str, typing.Any], typing.List[typing.Any]],
) -> typing.Union[typing.Dict[str, typing.Any], typing.List[typing.Any]]:
    """
    Recursively convert all dictionary keys to snake_case.

    Parameters
    ----------
    data : Union[Dict[str, Any], List[Any]]
        The input dict or list.

    Returns
    -------
    Union[Dict[str, Any], List[Any]]
        The data structure with all keys converted to snake_case.

    Examples
    --------
    >>> dkeys_to_snake_case(
    ...     {"FirstName": "Alice", "Details": {"PhoneNumber": "123"}}
    ... )
    {'first_name': 'Alice', 'details': {'phone_number': '123'}}
    """
    # If it's a list, recurse per item
    if isinstance(data, list):
        lst: typing.List[typing.Any] = data
        return [
            dkeys_to_snake_case(
                typing.cast(
                    "typing.Union[typing.Dict[str, typing.Any], typing.List[typing.Any]]",
                    item,
                )
            )
            if isinstance(item, (dict, list))
            else item
            for item in lst
        ]

    # Now data is treated as Dict[str, Any]
    mapping: typing.Dict[str, typing.Any] = data
    result: typing.Dict[str, typing.Any] = {}
    for key, value in mapping.items():
        new_key: str = to_snake_case(key)
        if isinstance(value, (dict, list)):
            result[new_key] = dkeys_to_snake_case(
                typing.cast(
                    "typing.Union[typing.Dict[str, typing.Any], typing.List[typing.Any]]",
                    value,
                )
            )
        else:
            result[new_key] = value

    return result
