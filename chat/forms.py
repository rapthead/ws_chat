# -*- coding: utf-8 -*-
from django.db.models import Q
from django.forms import ModelForm, ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from crispy_forms.bootstrap import StrictButton
from django_select2.forms import Select2MultipleWidget

from .models import Message, UserProxyModel


class InviteForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)
        helper = FormHelper()
        helper.form_method = 'post'
        helper.form_class = 'navbar-form navbar-right'
        helper.field_template = 'bootstrap3/layout/inline_field.html'
        helper.form_show_labels = False

        helper.layout = Layout(
            Field('email', placeholder='email', required='required'),
            StrictButton(u'Пригласить', css_class='btn-default', type='submit', name='invite')
        )
        self.helper = helper

    def clean_email(self):
        data = self.cleaned_data['email']
        if UserProxyModel.objects.filter(Q(email=data) | Q(username=data)).exists():
            raise ValidationError(u"Пользователь с таким email уже существует")
        return data

    def save(self, user=None, new_user_password=None, *args, **kwargs):
        self.instance.username = self.instance.email
        self.instance.set_password(new_user_password)
        return super(InviteForm, self).save(*args, **kwargs)

    class Meta:
        model = UserProxyModel
        fields = ('email',)


# class UserUpdateForm(ModelForm):
#     class Meta:
#         model = User
#         fields = ('name',)


class NewMessageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewMessageForm, self).__init__(*args, **kwargs)
        helper = FormHelper()
        helper.form_method = 'post'
        helper.add_input(Submit('send-message', u'Отправить сообщение', css_class="pull-right"))

        self.helper = helper

    def save(self, user=None, *args, **kwargs):
        self.instance.user = user
        super(NewMessageForm, self).save(*args, **kwargs)

    class Meta:
        model = Message
        fields = ('message', 'tags')
        widgets = {
            'tags': Select2MultipleWidget
        }
