import argparse
import os
import re
import smtplib
import ssl
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ansi2html import Ansi2HTMLConverter
from bs4 import BeautifulSoup
from bs4.element import Tag

STYLE = "font-family: FF !important; font-size: FSpx !important;"


def print_docstring(msg: str) -> None:
    """Print a formatted docstring.

    This function assumes the docstring is in a very specific format:

    >>> msg = \"\"\"
    >>> First line (non-blank)
    >>>
    >>> Subsequent lines
    >>> Subsequent lines
    >>> Subsequent lines
    >>> ...
    >>> Can include empty lines after the first.
    >>> \"\"\"

    Parameters
    ----------
    msg : str
        The docstring to be printed.
    """
    # Delete the first line ('\n' by itself), then strip any trailing
    # spaces. Remove leading padding, then print.
    clean = msg[1:].rstrip()
    lines = clean.split("\n")
    spaces = 0
    for c in lines[0]:
        if c.isspace():
            spaces += 1
        else:
            break
    formatted_docstring = "\n".join([line[spaces:] for line in lines])
    print(formatted_docstring)
    return


# ======================================================================


def file_is_html(file_to_test: str) -> bool:
    """Determine if a file is HTML

    Parameters
    ----------
    file_to_test : str
        The text of a file to test.

    Returns
    -------
    bool
        True if the file is HTML; else False
    """
    if re.search(
        r"<!DOCTYPE\s+html>|<(html|head|body|title|div|p|span)",
        file_to_test,
        re.IGNORECASE,
    ):
        return True
    return False


# ======================================================================


def validate_environment() -> bool:
    """Ensure the correct environment variables are in place.

    Returns
    -------
    bool
        True if the correct variables are set; else False.
    """
    try:
        os.environ["SMVP_USER"]
        os.environ["SMVP_TOKEN"]
        os.environ["SMVP_SERVER"]

    except KeyError:
        msg = """
        One or more credentials for sending email are missing from your
        environment. Make sure the following environment variables are
        set and exported in your current shell:
        
        export SMVP_USER="<your email>"    # e.g. "myemail@gmail.com"
        export SMVP_TOKEN="<your token>"   # e.g. "<gmail app password>"
        export SMVP_SERVER="<smtp server>" # e.g. "smtp.gmail.com"

        It's recommended that you put the lines above in your "rc" file
        (.bashrc, .zshrc, etc.) for use across multiple shell sessions
        and processes. To confirm you have the environment variables
        correctly set (with the correct spellings), run this in a
        terminal:

        set | grep ^SMVP_

        Note: If you make changes to your "rc" file, make sure to
        "source" it before running smvp again. Also, the SMVP_SERVER you
        select must support secure TLS connections on port 587.
        """
        print()
        print_docstring(msg=msg)
        return False

    return True


# ======================================================================


def task_runner(args: argparse.Namespace) -> None:
    """Package email contents and send message

    Parameters
    ----------
    args : argparse.Namespace
        The collection of command line arguments.
    """
    if not validate_environment():
        sys.exit(1)

    # Initialize
    sender_email = os.environ["SMVP_USER"]
    email_server = os.environ["SMVP_SERVER"]
    email_token = os.environ["SMVP_TOKEN"]
    receiver_email = args.recipient
    email_subject = args.subject
    email_port = 587

    try:
        with args.file as f:
            text_in = f.read()
    except UnicodeDecodeError:
        msg = f"""
        Unable to process: {args.file.name}
        smvp can only process textfiles (including those with ANSI
        escape sequences) or html files. No email sent.
        """
        print_docstring(msg=msg)
        sys.exit(1)

    # Craft an HTML version compatible with Gmail. If it's not HTML,
    # then filter it through ansi2html to scan for ANSI codes and turn
    # that into HTML. Plaintext will process fine. The text replacement
    # below is to ditch the dull-grey default in ansi2html.
    if not file_is_html(text_in):
        converter = Ansi2HTMLConverter(dark_bg=False)
        html_text = converter.convert(text_in, full=True)
        html_text = html_text.replace("color: #AAAAAA", "color: #FFFFFF")
    else:
        html_text = text_in

    # Set font family and size
    new_style = STYLE.replace("FF", args.font_family)
    new_style = new_style.replace("FS", str(args.font_size))

    soup = BeautifulSoup(html_text, "lxml")
    plain_text = soup.get_text().strip()

    # Gmail strips custom css, so we need to apply inline styles with
    # (!important) to the body tag.
    body_tag = soup.find("body")
    if isinstance(body_tag, Tag):
        body_tag["style"] = new_style

    # Also apply inline styles with (!important) to .ansi2html-content
    # tags
    ansi_content_tags = soup.find_all(class_="ansi2html-content")
    for tag in ansi_content_tags:
        if isinstance(tag, Tag):
            tag["style"] = new_style

    # ! Debug code goes here when testing.

    # Package both parts into a MIME multipart message.
    message = MIMEMultipart("alternative")
    message["Subject"] = email_subject
    message["From"] = sender_email
    message["To"] = receiver_email
    message.attach(MIMEText(plain_text, "plain"))
    message.attach(MIMEText(str(soup), "html"))

    # Create a secure context for the TLS connection
    context = ssl.create_default_context()

    # Send the email
    try:
        server = smtplib.SMTP(email_server, email_port)
        server.starttls(context=context)
        server.login(sender_email, email_token)
        server.sendmail(
            from_addr=sender_email,
            to_addrs=receiver_email,
            msg=message.as_string(),
        )
        print("Message successfully sent.")
    except Exception as e:
        print(e)
    finally:
        server.quit()
    return


# ======================================================================
