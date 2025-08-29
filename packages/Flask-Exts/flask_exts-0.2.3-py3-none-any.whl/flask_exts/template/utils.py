from wtforms import HiddenField
from wtforms.validators import DataRequired, InputRequired

def type_name(item):
    return type(item).__name__


def is_hidden_field(field):
    return isinstance(field, HiddenField)


def is_required_form_field(field):
    """
    Check if form field has `DataRequired`, `InputRequired`

    :param field:
        WTForms field to check
    """
    for validator in field.validators:
        if isinstance(validator, (DataRequired, InputRequired)):
            return True
    return False


def get_table_titles(data, primary_key, primary_key_title):
    """Detect and build the table titles tuple from ORM object, currently only support SQLAlchemy."""
    if not data:
        return []
    titles = []
    for k in data[0].__table__.columns.keys():
        if not k.startswith("_"):
            titles.append((k, k.replace("_", " ").title()))
    titles[0] = (primary_key, primary_key_title)
    return titles

