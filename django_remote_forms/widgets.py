import datetime

from django.forms.widgets import Widget, Input
from django.utils.dates import MONTHS
from django.utils.datastructures import SortedDict

class RemoteWidget(object):
    def __init__(self, widget, name=None):
        self.widget = widget
        self.name = name or self.widget.__class__.__name__

    def as_dict(self):
        widget_dict = SortedDict()
        widget_dict['title'] = self.name
        widget_dict['is_hidden'] = self.widget.is_hidden
        widget_dict['needs_multipart_form'] = self.widget.needs_multipart_form
        widget_dict['is_localized'] = self.widget.is_localized
        widget_dict['is_required'] = self.widget.is_required
        widget_dict['attrs'] = self.widget.build_attrs()

        return widget_dict
    
class RemoteInput(RemoteWidget):
    def as_dict(self):
        widget_dict = super(RemoteInput, self).as_dict()
        widget_dict['input_type'] = self.widget.input_type
        return widget_dict

class RemoteTextInput(RemoteInput):
    def as_dict(self):
        return super(RemoteTextInput, self).as_dict()

class RemotePasswordInput(RemoteInput):
    def as_dict(self):
        return super(RemotePasswordInput, self).as_dict()

class RemoteHiddenInput(RemoteInput):
    def as_dict(self):
        return super(RemoteHiddenInput, self).as_dict()

class RemoteMultipleHiddenInput(RemoteHiddenInput):
    def as_dict(self):
        widget_dict = super(RemoteMultipleHiddenInput, self).as_dict()
        widget_dict['choices'] = self.choices
        return widget_dict

class RemoteFileInput(RemoteInput):
    def as_dict(self):
        return super(RemoteFileInput, self).as_dict()

class RemoteClearableFileInput(RemoteFileInput):
    def as_dict(self):
        widget_dict = super(RemoteClearableFileInput, self).as_dict()
        widget_dict['initial_text'] = self.initial_text
        widget_dict['input_text'] = self.input_text
        widget_dict['clear_checkbox_label'] = self.clear_checkbox_label
        return widget_dict

class RemoteTextarea(RemoteInput):
    def as_dict(self):
        widget_dict = super(RemoteTextarea, self).as_dict()
        widget_dict['input_type'] = 'textarea'
        return widget_dict

class RemoteTimeInput(RemoteWidget):
    def as_dict(self):
        widget_dict = super(RemoteTimeInput, self).as_dict()

        widget_dict['format'] = self.widget.format
        widget_dict['manual_format'] = self.widget.manual_format
        widget_dict['date'] = self.widget.manual_format
        widget_dict['input_type'] = 'time'
        return widget_dict

class RemoteDateInput(RemoteWidget):
    def as_dict(self):
        widget_dict = super(RemoteDateInput, self).as_dict()

        widget_dict['input_type'] = 'date'

        years = self.widget.years
        if not callable(self.widget.years):
            years = lambda: self.widget.years

        current_year = datetime.datetime.now().year
        widget_dict['choices'] = [{
            'title': 'day',
            'data': [{'key': x, 'value': x} for x in range(1, 32)]
        }, {
            'title': 'month',
            'data': [{'key': x, 'value': y} for (x, y) in MONTHS.items()]
        }, {
            'title': 'year',
            'data': [{'key': x, 'value': x} for x in years()]
        }]
        return widget_dict


class RemoteDateTimeInput(RemoteWidget):
    def as_dict(self):
        widget_dict = super(RemoteDateTimeInput, self).as_dict()

        widget_dict['input_type'] = 'datetime'
        return widget_dict

class RemoteCheckboxInput(RemoteWidget):
    def as_dict(self):
        widget_dict = super(RemoteCheckboxInput, self).as_dict()

        # If check test is None then the input should accept null values
        check_test = None
        if self.check_test is not None:
            check_test = True

        widget_dict['check_test'] = check_test
        widget_dict['input_type'] = 'checkbox'
        return widget_dict

class RemoteSelect(RemoteWidget):
    def as_dict(self):
        widget_dict = super(RemoteSelect, self).as_dict()
        widget_dict['input_type'] = 'select'

        widget_dict['choices'] = []
        for key, value in self.widget.choices:
            widget_dict['choices'].append({
                'value': key,
                'display': value
            })

        return widget_dict

class RemoteNullBooleanSelect(RemoteSelect):
    def as_dict(self):
        return super(RemoteNullBooleanSelect, self).as_dict()

class RemoteSelectMultiple(RemoteSelect):
    def as_dict(self):
        widget_dict = super(RemoteSelectMultiple, self).as_dict()

        widget_dict['input_type'] = 'selectmultiple'
        widget_dict['size'] = len(widget_dict['choices'])
        return widget_dict

class RemoteRadioInput(RemoteWidget):
    def as_dict(self):
        widget_dict = SortedDict()
        widget_dict['title'] = self.__class__.__name__
        widget_dict['name'] = self.name
        widget_dict['value'] = self.value
        widget_dict['attrs'] = self.attrs
        widget_dict['choice_value'] = self.choice_value
        widget_dict['choice_label'] = self.choice_label
        widget_dict['index'] = self.index
        widget_dict['input_type'] = 'radio'
        return widget_dict

class RemoteRadioFieldRenderer(RemoteWidget):
    def as_dict(self):
        widget_dict = SortedDict()
        widget_dict['title'] = self.__class__.__name__
        widget_dict['name'] = self.name
        widget_dict['value'] = self.value
        widget_dict['attrs'] = self.attrs
        widget_dict['choices'] = self.choices
        widget_dict['input_type'] = 'radio'
        return widget_dict

class RemoteRadioSelect(RemoteSelect):
    def as_dict(self):
        widget_dict = super(RemoteRadioSelect, self).as_dict()

        widget_dict['choices'] = []
        for key, value in self.choices:
            widget_dict['choices'].append({
                'name': self.field_name or '',
                'value': key,
                'display': value
            })

        widget_dict['input_type'] = 'radio'
        return widget_dict

class RemoteCheckboxSelectMultiple(RemoteSelectMultiple):
    def as_dict(self):
        return super(RemoteCheckboxSelectMultiple, self).as_dict()

class RemoteMultiWidget(RemoteWidget):
    def as_dict(self):
        widget_dict = super(RemoteMultiWidget, self).as_dict()

        widget_list = []
        for widget in self.widgets:
            # Fetch remote widget and convert to dict
            widget_list.append()

        widget_dict['widgets'] = widget_list
        return widget_dict

class RemoteSplitDateTimeWidget(RemoteMultiWidget):
    def as_dict(self):
        widget_dict = super(RemoteSplitDateTimeWidget, self).as_dict()

        widget_dict['date_format'] = self.date_format
        widget_dict['time_format'] = self.time_format

        return widget_dict

class RemoteSplitHiddenDateTimeWidget(RemoteSplitDateTimeWidget):
    def as_dict(self):
        return super(RemoteSplitHiddenDateTimeWidget, self).as_dict()
