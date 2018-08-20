from collections import OrderedDict

from django_remote_forms import fields, logger, widgets
from django_remote_forms.utils import resolve_promise

class RemoteForm(object):
    def __init__(self, form, *args, **kwargs):
        self.form = form
        self._config = kwargs.pop('config', {})

        self.all_fields = set(self.form.fields.keys())

        self.excluded_fields = set(kwargs.pop('exclude', []))
        self.included_fields = set(kwargs.pop('include', []))
        self.readonly_fields = set(kwargs.pop('readonly', []))
        self.ordered_fields = kwargs.pop('ordering', [])

        self.fieldsets = []
        if(hasattr(self.form, 'Meta')):
            self.fieldsets = getattr(self.form.Meta, 'fieldsets', [])

        # Make sure all passed field lists are valid
        if self.excluded_fields and not (self.all_fields >= self.excluded_fields):
            logger.warning('Excluded fields %s are not present in form fields' % (self.excluded_fields - self.all_fields))
            self.excluded_fields = set()

        if self.included_fields and not (self.all_fields >= self.included_fields):
            logger.warning('Included fields %s are not present in form fields' % (self.included_fields - self.all_fields))
            self.included_fields = set()

        if self.readonly_fields and not (self.all_fields >= self.readonly_fields):
            logger.warning('Readonly fields %s are not present in form fields' % (self.readonly_fields - self.all_fields))
            self.readonly_fields = set()

        if self.ordered_fields and not (self.all_fields >= set(self.ordered_fields)):
            logger.warning('Readonly fields %s are not present in form fields' % (set(self.ordered_fields) - self.all_fields))
            self.ordered_fields = []

        if self.included_fields | self.excluded_fields:
            logger.warning('Included and excluded fields have following fields %s in common' % (set(self.ordered_fields) - self.all_fields))
            self.excluded_fields = set()
            self.included_fields = set()

        # Extend exclude list from include list
        self.excluded_fields |= (self.included_fields - self.all_fields)

        if not self.ordered_fields:
            try:
                self.ordered_fields = self.form.fields.keyOrder
            except AttributeError:
                self.ordered_fields = self.form.fields.keys()

        self.fields = []

        # Construct ordered field list considering exclusions
        for field_name in self.ordered_fields:
            if field_name in self.excluded_fields:
                continue

            self.fields.append(field_name)

    def as_dict(self):
        """
        Returns a form as a dictionary that looks like the following:

        form = {
            'non_field_errors': [],
            'label_suffix': ':',
            'is_bound': False,
            'prefix': 'text'.
            'fields': {
                'name': {
                    'type': 'type',
                    'errors': {},
                    'help_text': 'text',
                    'label': 'text',
                    'initial': 'data',
                    'max_length': 'number',
                    'min_length: 'number',
                    'required': False,
                    'bound_data': 'data'
                    'widget': {
                        'attr': 'value'
                    }
                }
            }
        }
        """
        form_dict = OrderedDict()
        form_dict['title'] = self.form.__class__.__name__
        form_dict['non_field_errors'] = self.form.non_field_errors()
        form_dict['label_suffix'] = self.form.label_suffix
        form_dict['is_bound'] = self.form.is_bound
        form_dict['prefix'] = self.form.prefix
        form_dict['fields'] = OrderedDict()
        form_dict['errors'] = self.form.errors
        fieldset_list = []
        for fieldset_name, fieldset_data in self.fieldsets:
            fieldset_data.update({
                'key': fieldset_name,
            })
            fieldset_list.append(fieldset_data)
        form_dict['fieldsets'] = fieldset_list

        initial_data = {}

        for bound_field in (x for x in self.form if x.name in self.fields):
            # Retrieve the initial data from the form itself if it exists so
            # that we properly handle which initial data should be returned in
            # the dictionary.

            # Please refer to the Django Form API documentation for details on
            # why this is necessary:
            # https://docs.djangoproject.com/en/dev/ref/forms/api/#dynamic-initial-values
            form_initial_field_data = self.form.initial.get(bound_field.name)

            # Instantiate the Remote Forms equivalent of the field if possible
            # in order to retrieve the field contents as a dictionary.
            # Use config to to check for any serializer overrides.
            field_class_name = bound_field.field.__class__.__name__
            if self._config.get('fields', {}).get(field_class_name):
                remote_field_class = self._config['fields'][field_class_name]
            else:
                remote_field_class = getattr(fields, 'Remote%s' % field_class_name)

            try:
                remote_field = remote_field_class(bound_field, form_initial_field_data)
            except Exception, e:
                logger.warning('Error serializing field %s: %s', remote_field_class, str(e))
                field_dict = {}
            else:
                field_dict = remote_field.as_dict()

            if bound_field.name in self.readonly_fields:
                field_dict['readonly'] = True

            form_dict['fields'][bound_field.name] = field_dict

            widget_class_name = bound_field.field.widget.__class__.__name__
            if self._config.get('widgets', {}).get(widget_class_name):
                remote_widget_class = self._config['widgets'][widget_class_name]
            else:
                remote_widget_class = getattr(widgets, 'Remote%s' % widget_class_name)

            try:
                remote_widget = remote_widget_class(remote_field.widget,
                        name=remote_field.name, required=remote_field.required)
            except Exception, e:
                logger.error('Error serializing %s: %s', remote_widget_class, str(e))
                widget_dict = {}
            else:
                widget_dict = remote_widget.as_dict()

            form_dict['fields'][bound_field.name]['widget'] = widget_dict

            # Load the initial data, which is a conglomerate of form initial and field initial
            if 'initial' not in form_dict['fields'][bound_field.name]:
                form_dict['fields'][bound_field.name]['initial'] = None

            initial_data[bound_field.name] = form_dict['fields'][bound_field.name]['initial']

        if self.form.data:
            form_dict['data'] = self.form.data
        else:
            form_dict['data'] = initial_data

        return resolve_promise(form_dict)
