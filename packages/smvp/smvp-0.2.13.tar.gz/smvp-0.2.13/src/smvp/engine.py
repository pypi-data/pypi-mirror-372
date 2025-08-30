import argparse
import re
from typing import List

from smvp.utilities import print_docstring
from smvp.utilities import task_runner
from smvp.version import get_version


def font_size(size: str) -> str:
    """Validate size inputs.

    Parameters
    ----------
    size : str
        User input for a font size option.

    Returns
    -------
    str
        The validated user input.

    Raises
    ------
    argparse.ArgumentTypeError
        If the input is not a valid integer (for example is a float).
    argparse.ArgumentTypeError
        If the input is not between 2 and 100.
    """
    for c in size:
        if not c.isdigit():
            msg = "Size must be a valid integer"
            raise argparse.ArgumentTypeError(msg)

    int_size = int(size)
    min_size = 2
    max_size = 100
    if int_size >= min_size and int_size <= max_size:
        return size
    else:
        msg = f"Font size must be between {min_size} and {max_size}"
        raise argparse.ArgumentTypeError(msg)


# ======================================================================


def font_family(font: str) -> str:
    """Validate font_family inputs.

    Parameters
    ----------
    font : str
        User input for a font family.

    Returns
    -------
    str
        The validated user input.

    Raises
    ------
    argparse.ArgumentTypeError
        If the the selected font family is not recognized.
    """
    valid_fonts = {
        "ANDALE MONO": "Andale Mono",
        "ARIAL": "Arial",
        "BRUSH SCRIPT MT": "Brush Script MT",
        "COMIC SANS MS": "Comic Sans MS",
        "COURIER NEW": "Courier New",
        "FANTASY": "fantasy",
        "GARAMOND": "Garamond",
        "GEORGIA": "Georgia",
        "HELVETICA": "Helvetica",
        "IMPACT": "Impact",
        "LUMINARI": "Luminari",
        "MONACO": "Monaco",
        "MONOSPACE": "monospace",
        "SANS-SERIF": "sans-serif",
        "SERIF": "serif",
        "TAHOMA": "Tahoma",
        "TIMES NEW ROMAN": "Times New Roman",
        "TREBUCHET MS": "Trebuchet MS",
        "VERDANA": "Verdana",
    }
    user_input = " ".join([word.upper() for word in font.split()])
    if user_input in valid_fonts:
        return valid_fonts[user_input]
    else:
        print()
        fonts = [f'"{token}"' for token in list(valid_fonts.values())]
        fonts.sort()
        msg = f"""
        The font you entered ({font}) is not valid. The default font is
        "Courier New". If you're changing the default font, please use
        one of the options below. Check the spelling to make sure it's
        correct.
        """
        print_docstring(msg=msg)
        print()
        chunk_size = 5
        start = 0
        end = 4
        chunks: List[str] = []
        for font in fonts:
            chunk = fonts[start:end]
            if start > len(fonts) or len(chunk) == 0:
                break
            if len(chunk) > 1:
                chunks.append(", ".join(fonts[start:end]))
            else:
                chunks.append(chunk[0])
            start = end
            end += chunk_size
        print(",\n".join(chunks))
        print()
        raise argparse.ArgumentTypeError("invalid font family")


# ======================================================================


def email_type(address: str) -> str:
    """Validate user input of email addresses.

    Parameters
    ----------
    address : str
        An email address.

    Returns
    -------
    str
        If the address is valid, it's returned.

    Raises
    ------
    argparse.ArgumentTypeError
        This is raised for an invalid email address.
    """
    S = r"[a-zA-Z"
    email = re.compile(rf"^{S}0-9._%+-]+@{S}0-9.-]+\.{S}]{{2,}}$")
    if not email.match(address):
        raise argparse.ArgumentTypeError(f"'{address}' is not a valid email address")
    return address


# ======================================================================


def process_args() -> None:
    msg = """
    Send Mail Via Python (smvp). This tool will send an email from the
    command line, with the body of the email taken from a specified
    file. For example, it's handy to use smvp to have automated Linux
    scripts (i.e. cron jobs) email you status updates and the contents
    of log files.
    """
    epi = f"Version: {get_version()}"
    parser = argparse.ArgumentParser(description=msg, epilog=epi)

    msg = """The email address of the recipient."""
    parser.add_argument("recipient", type=email_type, help=msg)

    msg = """
    The subject of the email. IMPORTANT: Make sure to enclose the entire
    subject in double quotes for proper processing on the command line.
    """
    parser.add_argument("subject", type=str, help=msg)

    msg = """
    The file containing the text which will make up the body of the
    email message. The input file can be a text file with ANSI color
    codes, HTML, or plain text. The resulting email will be sent as a
    multi-part MIME message that renders properly in both plain text and
    HTML.
    """
    parser.add_argument("file", type=argparse.FileType("r"), help=msg)

    msg = """
    Enter the desired font family (enclosed in quotes). Values here are
    not case sensitive. See the README.md file for available options.
    Default = \"Courier New\".
    """
    parser.add_argument(
        "-f", "--font_family", type=font_family, default="Courier New", help=msg
    )

    msg = """
    Enter the desired font pixel size as an integer. Valid sizes are
    between 2 and 100. Default = 12.
    """
    parser.add_argument("-s", "--font_size", type=font_size, default=12, help=msg)

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"smvp {get_version()}",
    )

    args = parser.parse_args()
    task_runner(args=args)
    return
