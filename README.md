# django-remote-forms

A package that allows you to serialize django forms, including fields and widgets into Python
dictionary for easy conversion into JSON and expose over API

Please go through my [djangocon US 2012 talk](http://www.slideshare.net/tarequeh/django-forms-in-a-web-api-world)
to understand the problem sphere, motivations, challenges and implementation of Remote Forms

## Sample Implementation

If you don't mind digging around a little bit to learn about different the components that might be
necessary for an implementation of django-remote-forms, check out
django Remote Admin [django-remote-admin](https://github.com/tarequeh/django-remote-admin)

## Usage

### Minimal Example

    from django_remote_forms.forms import RemoteForm

    form = LoginForm()
    remote_form = RemoteForm(form)
    remote_form_dict = remote_form.as_dict()

Upon converting the dictionary into JSON, it looks like this:

    {
        "is_bound": false,
        "non_field_errors": [],
        "errors": {},
        "title": "LoginForm",
        "fields": {
            "username": {
                "title": "CharField",
                "required": true,
                "label": "Username",
                "initial": null,
                "help_text": "This is your django username",
                "error_messages": {
                    "required": "This field is required.",
                    "invalid": "Enter a valid value."
                },
                "widget": {
                    "title": "TextInput",
                    "is_hidden": false,
                    "needs_multipart_form": false,
                    "is_localized": false,
                    "is_required": true,
                    "attrs": {
                        "maxlength": "30"
                    },
                    "input_type": "text"
                },
                "min_length": 6,
                "max_length": 30
            },
            "password": {
                "title": "CharField",
                "required": true,
                "label": "Password",
                "initial": null,
                "help_text": "",
                "error_messages": {
                    "required": "This field is required.",
                    "invalid": "Enter a valid value."
                },
                "widget": {
                    "title": "PasswordInput",
                    "is_hidden": false,
                    "needs_multipart_form": false,
                    "is_localized": false,
                    "is_required": true,
                    "attrs": {
                        "maxlength": "128"
                    },
                    "input_type": "password"
                },
                "min_length": 6,
                "max_length": 128
            }
        },
        "label_suffix": ":",
        "prefix": null,
        "csrfmiddlewaretoken": "2M3MDgfzBmkmBrJ9U0MuYUdy8vgeCCgw",
        "data": {
            "username": null,
            "password": null
        }
    }

### An API endpoint serving remote forms

    from django.core.serializers.json import simplejson as json, DjangoJSONEncoder
    from django.http import HttpResponse
    from django.middleware.csrf import CsrfViewMiddleware
    from django.views.decorators.csrf import csrf_exempt

    from django_remote_forms.forms import RemoteForm

    from my_awesome_project.forms import MyAwesomeForm


    @csrf_exempt
    def my_ajax_view(request):
        csrf_middleware = CsrfViewMiddleware()

        response_data = {}
        if request.method == 'GET':
            # Get form definition
            form = MyAwesomeForm()
        elif request.raw_post_data:
            request.POST = json.loads(request.raw_post_data)
            # Process request for CSRF
            csrf_middleware.process_view(request, None, None, None)
            form_data = request.POST.get('data', {})
            form = MyAwesomeForm(form_data)
            if form.is_valid():
                form.save()

        remote_form = RemoteForm(form)
        # Errors in response_data['non_field_errors'] and response_data['errors']
        response_data.update(remote_form.as_dict())

        response = HttpResponse(
            json.dumps(response_data, cls=DjangoJSONEncoder),
            mimetype="application/json"
        )

        # Process response for CSRF
        csrf_middleware.process_response(request, response)
        return response

### Custom fields and widget

    from django_remote_forms.forms import RemoteForm
    from django_remote_forms.widgets import RemoteTextInput

    form = LoginForm()
    remote_form_config = {
        'widgets': {
            'MyCustomWidget': RemoteTextInput,
        },
    }
    remote_form = RemoteForm(form, config=remote_form_config)
    remote_form_dict = remote_form.as_dict()
