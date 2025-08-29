"""Simple Regular Expressions Functions."""

import re

from loguru import logger

from lsre.utils import enforce_str_arg


@enforce_str_arg
def is_alphanumeric(text: str) -> bool:
    """Check if `text` is a alphanumeric string.

    Alphanumeric string has:

    - only letters (both uppercase and lowercase) and numbers.
    - Eg. `abc123`, `A1B2c3`

    Args:
        text (str): value to check

    Returns:
        bool: True if `text` is alphanumeric

    Raises:
        TypeError: If the `text` is not a string.

    Examples:
        >>> from lsre import is_alphanumeric
        >>> is_alphanumeric('abc123')
        True
        >>> is_alphanumeric('123@')
        False
    """
    logger.debug(f'Checking if {text} is alphanumeric')
    pattern = r'^[a-zA-Z0-9]+$'
    match = re.match(pattern=pattern, string=text)
    logger.debug(f'Match result: {match}')
    return match is not None


@enforce_str_arg
def is_email(text: str) -> bool:
    """Check if `text` is an email address.

    Email contains following parts:

    - **local-part**: the part before the @ symbol
        - 1-64 chars
        - letters, digits, `._%+-` allowed
        - must not start or end with a dot
        - no consecutive dots
    - **domain**: the part after the @ symbol
        - one or more labels separated by dots
        - each label 1-63 chars, letters/digits/hyphen
        - labels must not start or end with hyphen
    - **TLD**:
        - last label at least 2 chars
        - letters only
    - Final email is local-part@domain.tld
    - Eg. `user@example.com`, `user.name+tag@sub.domain.co`

    Args:
        text (str): value to check

    Returns:
        bool: True if `text` matches an email pattern

    Raises:
        TypeError: If the `text` is not a string.

    Examples:
        >>> from lsre import is_email
        >>> is_email('user@example.com')
        True
        >>> is_email('invalid-email')
        False

    Warning:
        - Overall length limits are not strictly enforced by regex here.
    """
    logger.debug(f'Checking if {text} is an email')
    pattern = (
        r'^(?!\.)(?!.*\.\.)[a-zA-Z0-9\._%\+-]{1,64}(?<!\.)'  # local-part
        r'@'  # @
        r'((?!(-|.*\-\.))[a-zA-Z0-9-]{1,63}\.)+'  # domain
        r'[a-zA-Z]{2,}$'  # TLD
    )
    match = re.match(pattern=pattern, string=text)
    logger.debug(f'Match result: {match}')
    return match is not None


@enforce_str_arg
def is_url(text: str) -> bool:
    """Check if `text` is a URL.

    URL contains following parts:

    - **scheme**: required, one of http, https, ftp (case-insensitive)
        followed by ://
    - **authority**: optional user:pass@
    - **host**: domain name (labels like domain.tld) or IPv4 address;
    - **port**: optional :<1-5 digits>
    - **path/query/fragment**: optional, may contain any non-space characters.
    - Eg. `https://example.com/path?query=1`, `ftp://ftp.example.org`

    Args:
        text (str): value to check

    Returns:
        bool: True if `text` matches a URL pattern

    Raises:
        TypeError: If the `text` is not a string.

    Examples:
        >>> from lsre import is_url
        >>> is_url('https://example.com')
        True
        >>> is_url('invalid-url')
        False

    Warning:
        - Overall length limits are not strictly enforced by regex here.
        - IDN/unicode domains are not considered here.
    """
    logger.debug(f'Checking if {text} is a url')
    pattern = (
        r'(http|https|ftp)://'  # scheme
        r'(\w+:\w+@)?[a-z0-9]+(\.[a-z0-9])*'  # authority and host
        r'(\:\d+)?(/\w+)?'  # port and path
    )
    match = re.match(pattern=pattern, string=text)
    logger.debug(f'Match result: {match}')
    return match is not None


@enforce_str_arg
def is_ipv4(text: str) -> bool:
    """Check if `text` is an IPv4 address.

    IPv4 address has:

    - four octets separated by dots
    - each octet is a decimal number 0-255 (no leading +); allow 0 and 255
    - Eg. `192.168.0.1`, `255.255.255.255`

    Args:
        text (str): value to check

    Returns:
        bool: True if `text` matches an IPv4 pattern

    Raises:
        TypeError: If the `text` is not a string.

    Examples:
        >>> from lsre import is_ipv4
        >>> is_ipv4('192.168.0.1')
        True
        >>> is_ipv4('invalid-ip')
        False

    Warning:
        - no leading zeros constraints (e.g. '01') are relaxed
    """
    logger.debug(f'Checking if {text} is an IPv4 address')
    pattern = (
        r'^([0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])\.'
        r'([0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])\.'
        r'([0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])\.'
        r'([0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])$'
    )
    match = re.match(pattern=pattern, string=text)
    logger.debug(f'Match result: {match}')
    return match is not None


@enforce_str_arg
def is_ipv6(text: str) -> bool:
    """Check if `text` is an IPv6 address.

    IPv6 address has:

    - colon-separated hex groups (1 to 8 groups)
    - each group 1-4 hex digits
    - hex digits are 0-9a-f (case-insensitive)
    - can be abbreviated with "::" to compress consecutive zero groups
    - Eg. `::1`, `2001:0db8:85a3:0000:0000:8a2e:0370:7334`

    Args:
        text (str): value to check

    Returns:
        bool: True if `text` matches an IPv6 pattern

    Raises:
        TypeError: If the `text` is not a string.

    Examples:
        >>> from lsre import is_ipv6
        >>> is_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:7334')
        True
        >>> is_ipv6('invalid-ipv6')
        False
    """
    logger.debug(f'Checking if {text} is an IPv6 address')
    pattern = (
        r'^('
        r'([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}|'
        r'([0-9A-Fa-f]{1,4}:){1,6}(:[0-9A-Fa-f]{1,4}){1}|'
        r'([0-9A-Fa-f]{1,4}:){1,5}(:[0-9A-Fa-f]{1,4}){1,2}|'
        r'([0-9A-Fa-f]{1,4}:){1,4}(:[0-9A-Fa-f]{1,4}){1,3}|'
        r'([0-9A-Fa-f]{1,4}:){1,3}(:[0-9A-Fa-f]{1,4}){1,4}|'
        r'([0-9A-Fa-f]{1,4}:){1,2}(:[0-9A-Fa-f]{1,4}){1,5}|'
        r'([0-9A-Fa-f]{1,4}:)(:[0-9A-Fa-f]{1,4}){1,6}|'
        r':((:[0-9A-Fa-f]{1,4}){1,7}|:)'
        r')$'
    )
    match = re.match(pattern=pattern, string=text)
    logger.debug(f'Match result: {match}')
    return match is not None


@enforce_str_arg
def is_phone_number(text: str) -> bool:
    """Check if `text` is a phone number.

    Phone number has:

    - optional leading + followed by 1-3 digit country code
    - allow separators: spaces, hyphens, dots
    - allow optional parentheses around area code
    - require total of 7-15 digits (counting only digits)
    - Eg. `+1-800-555-1212`, `8005551212`

    Args:
        text (str): value to check

    Returns:
        bool: True if `text` matches a phone number pattern

    Raises:
        TypeError: If the `text` is not a string.

    Examples:
        >>> from lsre import is_phone_number
        >>> is_phone_number('+1-800-555-1212')
        True
        >>> is_phone_number('invalid-phone')
        False

    Warning:
        - Doesn't check for separators consistency, only their presence
    """
    logger.debug(f'Checking if {text} is a phone number')
    pattern = r'^\+?(?=(?:.*\d){7,})(?!(?:.*\d){16,})[\d\-\(\)\s]+$'
    match = re.match(pattern=pattern, string=text)
    logger.debug(f'Match result: {match}')
    return match is not None


@enforce_str_arg
def is_credit_card(text: str) -> bool:
    """Check if `text` is a credit card number.

    Credit card number has:

    - 15 to 16 digits in total
    - allow groups separated by spaces
    - Eg. `4111 1111 1111 1111`, `4012888888881881`


    Args:
        text (str): value to check

    Returns:
        bool: True if `text` matches a credit card pattern

    Raises:
        TypeError: If the `text` is not a string.

    Examples:
        >>> from lsre import is_credit_card
        >>> is_credit_card('4111 1111 1111 1111')
        True
        >>> is_credit_card('invalid-credit-card')
        False

    Warning:
        - Doesn't support uncommon card numbers 13-14 or 17-19 digits
        - Luhn checksum is not validated
        - Hyphenated formats are not supported
    """
    logger.debug(f'Checking if {text} is a credit card')
    pattern = r'^(?=(?:.*\d){15,16}$)[0-9\s]+$'
    match = re.match(pattern=pattern, string=text)
    logger.debug(f'Match result: {match}')
    return match is not None


@enforce_str_arg
def is_iso_date(text: str) -> bool:
    """Check if `text` is an ISO date.

    ISO date is format is:

    - YYYY-MM-DD format
    - **Year**: 4 digits (e.g., 2025)
    - **Month**: 2 digits (01-12)
    - **Day**: 2 digits (01-31)
    - Eg. ``2025-08-22``, ``1999-12-31``

    Args:
        text (str): value to check

    Returns:
        bool: True if `text` matches an ISO date pattern

    Raises:
        TypeError: If the `text` is not a string.

    Examples:
        >>> from lsre import is_iso_date
        >>> is_iso_date('2025-08-22')
        True
        >>> is_iso_date('1999-13-01')
        False

    Warning:
        - This simple regex does not fully validate month/day combinations
        - It does not validate leap years
    """
    logger.debug(f'Checking if {text} is an ISO date')
    pattern = r'^\d{4}-(0[0-9]|1[1-2])-([0-2][0-9]|3[0-1])$'
    match = re.match(pattern=pattern, string=text)
    logger.debug(f'Match result: {match}')
    return match is not None


@enforce_str_arg
def is_time(text: str) -> bool:
    """Check if `text` is a time string.

    Time format is:

    - 24-hour clock
    - optional seconds
    - leading zeros are allowed
    - colon separated
    - Eg. `23:59`, `00:00:00`

    Args:
        text (str): value to check

    Returns:
        bool: True if `text` matches a time pattern

    Raises:
        TypeError: If the `text` is not a string.

    Examples:
        >>> from lsre import is_time
        >>> is_time('23:59')
        True
        >>> is_time('24:00')
        False
    """
    logger.debug(f'Checking if {text} is a time')

    pattern = r'^([0-1][0-9]|2[0-3]):([0-5][0-9])(\:[0-5][0-9])?$'
    match = re.match(pattern=pattern, string=text)
    logger.debug(f'Match result: {match}')
    return match is not None


@enforce_str_arg
def is_hex_color(text: str) -> bool:
    """Check if `text` is a hex color.

    Hex color is a:

    - 6-digit or 3-digit hexadecimal number
    - prefixed with a #
    - cases insensitive
    - Eg. #FFF, #123456

    Args:
        text (str): value to check

    Returns:
        bool: True if `text` matches a hex color pattern

    Raises:
        TypeError: If the `text` is not a string.

    Examples:
        >>> from lsre import is_hex_color
        >>> is_hex_color('#FFF')
        True
        >>> is_hex_color('invalid-hex')
        False
    """
    logger.debug(f'Checking if {text} is a hex color')
    pattern = r'^#([0-9a-f]{3}|[0-9a-f]{6})$'
    match = re.match(pattern=pattern, string=text, flags=re.IGNORECASE)
    logger.debug(f'Match result: {match}')
    return match is not None


@enforce_str_arg
def is_uuid(text: str) -> bool:
    """Check if `text` is a UUID.

    UUIDs are:

    - 8-4-4-4-12 hexadecimal digits
    - separated by hyphens
    - Eg. `123e4567-e89b-12d3-a456-426614174000`

    Args:
        text (str): value to check

    Returns:
        bool: True if `text` matches a UUID pattern

    Raises:
        TypeError: If the `text` is not a string.

    Examples:
        >>> from lsre import is_uuid
        >>> is_uuid('123e4567-e89b-12d3-a456-426614174000')
        True
        >>> is_uuid('invalid-uuid')
        False
    """
    logger.debug(f'Checking if {text} is a uuid')
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    match = re.match(pattern=pattern, string=text)
    logger.debug(f'Match result: {match}')
    return match is not None


@enforce_str_arg
def is_slug(text: str) -> bool:
    """Check if `text` is a URL slug.

    Slugs are:

    - lowercase letters and digits only
    - hyphens allowed as separators between words
    - cannot start or end with a hyphen
    - no consecutive hyphens

    Eg. `my-slug`, `another-slug-123`

    Args:
        text (str): value to check

    Returns:
        bool: True if `text` matches a slug pattern

    Raises:
        TypeError: If the `text` is not a string.

    Examples:
        >>> from lsre import is_slug
        >>> is_slug('my-slug')
        True
        >>> is_slug('invalid_slug')
        False
    """
    logger.debug(f'Checking if {text} is a slug')
    pattern = r'^[a-z0-9]+(\-[a-z0-9]+)*$'
    match = re.match(pattern=pattern, string=text)
    logger.debug(f'Match result: {match}')
    return match is not None


@enforce_str_arg
def is_strong_password(text: str) -> bool:
    """Check if text meets a strong password policy.

    A strong password has:

    - minimum length 8 characters
    - at least one lowercase letter, one uppercase letter, one digit,
      and one special character
    - Eg. `Aa1!aaaa`, `Str0ng#Pass`

    Args:
        text (str): value to check

    Returns:
        bool: True if `text` matches a strong password pattern

    Raises:
        TypeError: If the `text` is not a string.

    Examples:
        >>> from lsre import is_strong_password
        >>> is_strong_password('Aa1!aaaa')
        True
        >>> is_strong_password('invalid_password')
        False
    """
    logger.debug(f'Checking if {text} is a strong password')
    pattern = (
        r'^(?=(?:.*[a-z]))(?=(?:.*[A-Z]))(?=(?:.*[0-9]))(?=(?:.*[!@#$%&]))'
        r'.{8,}$'
    )
    match = re.match(pattern=pattern, string=text)
    logger.debug(f'Match result: {match}')
    return match is not None
