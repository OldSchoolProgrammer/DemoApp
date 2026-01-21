from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib import messages


class RegisterView(CreateView):
    """User registration view."""
    template_name = 'accounts/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('inventory:dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Welcome, {user.username}! Your account has been created.')
        return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('inventory:dashboard')
        return super().get(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view."""
    template_name = 'accounts/profile.html'
