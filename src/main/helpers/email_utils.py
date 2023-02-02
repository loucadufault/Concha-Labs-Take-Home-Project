import re


def normalize_email(email):
    """Normalize the email address by lowercasing the domain part of it.
    Mimics Django's approach, @see https://github.com/django/django/blob/stable/4.2.x/django/contrib/auth/base_user.py#L22-L33
    """
    email = email or ""
    try:
        email_name, domain_part = email.strip().rsplit("@", 1)
    except ValueError:
        pass
    else:
        email = email_name + "@" + domain_part.lower()
    return email

def is_valid_email(email):
    """Basic email validation, mainly to ensure it can be normalized."""
    return re.match(r".+@.+", email) is not None
