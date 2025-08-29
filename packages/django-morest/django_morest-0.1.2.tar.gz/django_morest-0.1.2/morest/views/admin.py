from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib import admin
from django.forms import Form

from rest_framework.views import APIView
from rest_framework.parsers import FormParser
from rest_framework import permissions



class AdminFormView(APIView):
    parser_classes = (FormParser,)
    action_name = "Action Name"
    template = "admin_form.html"
    breadcrumbs: tuple[tuple[str, str]] = None
    permission_classes = (permissions.IsAdminUser,)
    form = None
    
    def handle(self, request: HttpRequest, form: Form, **kwargs) -> HttpResponse:
        raise NotImplementedError

    def get_template(self, request: HttpRequest, **kwargs):
        return self.template
    
    def get_action_name(self, request: HttpRequest, form: Form, **kwargs):
        return self.action_name
    
    def get_breadcrumbs(self, request: HttpRequest, form: Form, **kwargs):
        if self.breadcrumbs is None:
            return tuple()
        return self.breadcrumbs
    
    def get_context(self, request: HttpRequest, form: Form = None, **kwargs):
        if form is None:
            form = self.form()

        return {
            "action_name": self.get_action_name(request=request, form=form, **kwargs),
            "breadcrumbs": self.get_breadcrumbs(request=request, form=form, **kwargs),
            "form": form,
            **admin.site.each_context(request),
        }
    
    def get(self, request: HttpRequest, **kwargs):
        return render(
            request, 
            self.get_template(request=request, **kwargs), 
            self.get_context(request=request, **kwargs)
        )

    def post(self, request: HttpRequest, **kwargs):
        form = self.form(request.POST)
        if not form.is_valid():
            return render(
                request, 
                self.get_template(request=request, **kwargs),
                self.get_context(request=request, form=form, **kwargs)
            )
        
        return self.handle(request=request, form=form, **kwargs)