# -*- coding: utf-8 -*-
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from .forms import InviteForm, NewMessageForm
from .models import Message, UserProxyModel


class IndexView(ListView):
    template_name = 'chat/index.html'
    invite_form_class = InviteForm
    new_message_form_class = NewMessageForm
    model = Message

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.first_name:
            return HttpResponseRedirect(reverse_lazy('user-update'))
        return super(IndexView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if self.request.user.is_staff:
            context['invite_form'] = self.invite_form_class
        context['new_message_form'] = self.new_message_form_class
        return context

    def post(self, request, *args, **kwargs):
        form = None
        if request.user.is_staff and 'invite' in self.request.POST:
            form = self.invite_form_class(self.request.POST)
        elif 'send-message' in self.request.POST:
            form = self.new_message_form_class(self.request.POST)

        if form:
            if form.is_valid():
                new_user_password = UserProxyModel.objects.make_random_password()
                save_result = form.save(user=self.request.user, new_user_password=new_user_password)
                if isinstance(form, self.invite_form_class):
                    messages.add_message(request, messages.INFO, u'Приглашение успешно отправлено')
                    self.mail_invited_user(save_result, new_user_password=new_user_password)
                return HttpResponseRedirect(reverse_lazy('chat-index'))
            else:
                messages.add_message(request, messages.ERROR, form.errors)
        return self.get(request, *args, **kwargs)

    def mail_invited_user(self, new_user, new_user_password=None):
        subject = "Приглашение на участие в чате"
        to = [new_user.email]

        context = {
            'invited_user': new_user,
            'current_user': self.request.user,
            'invite_url': self.request.build_absolute_uri(reverse('chat-index')),
            'new_user_password': new_user_password
        }

        message = render_to_string('chat/email/invite.txt', context)
        EmailMessage(subject, message, to=to).send()


class UserUpdateView(UpdateView):
    model = UserProxyModel
    fields = 'first_name',
    success_url = reverse_lazy('chat-index')

    def get_object(self, *args, **kwargs):
        return self.request.user
