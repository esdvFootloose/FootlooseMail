from django.forms.widgets import PasswordInput, Select, TextInput, CheckboxInput, FileInput, DateTimeInput, TimeInput, DateInput

class MetroTextInput(TextInput):
    input_type = 'text'
    template_name = 'widgets/text.html'

class MetroPasswordInput(PasswordInput):
    input_type = 'password'
    template_name = 'widgets/password.html'


class MetroEmailInput(MetroTextInput):
    input_type = 'email'


class MetroNumberInput(MetroTextInput):
    input_type = 'number'


class MetroMultiTextInput(TextInput):
    input_type = 'text'
    template_name = 'widgets/multitext.html'

class MetroSelect(Select):
    input_type = 'select'
    template_name = 'widgets/select.html'
    option_template_name = 'widgets/select_option.html'


class MetroSelectMultiple(Select):
    input_type = 'select'
    allow_multiple_selected = True
    template_name = 'widgets/select.html'
    option_template_name = 'widgets/select_option.html'


class MetroCheckBox(CheckboxInput):
    input_type = 'checkbox'
    template_name = 'widgets/checkbox.html'

class MetroFileInput(FileInput):
    input_type = 'file'
    needs_multipart_form = True
    template_name = 'widgets/file.html'
