from traceback import print_tb
from aiohttp import request
from django.shortcuts import render
from django.http import Http404
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, FormView
from .owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView, GroupOwnerDeleteView
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import  render, redirect
from .forms import NewUserForm
from django.contrib.auth import login
from django.contrib import messages

from .models import Note, Group, Done
from .forms import NoteCreateForm, GroupCreateForm


class ListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = "list.html"
    
    def get(self, request):
        group_list = Group.objects.filter(group_owner=self.request.user)
        note_list = Note.objects.filter(owner=self.request.user)
        done_list = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.done_things.values('id')
        
            # favorites = [2, 4, ...] using list comprehension
            done_list = [ row['id'] for row in rows ]
        #print(done_list)
        ctx = {
            'done_list' : done_list,
            'group_list' : group_list,
            'note_list' : note_list
        }
        return render(request, self.template_name, ctx)
    
    def get_queryset(self):
        print('update get_queryset called')
        qs = super(ListView, self).get_queryset()
        return qs.filter(group_owner=self.request.user)
    
    
def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("todo:all")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="register.html", context={"register_form":form})
    

class NoteCreateView(OwnerCreateView):
    template_name = 'form.html'
    success_url = reverse_lazy('todo:all')

    def get(self, request, pk):
        gr = get_object_or_404(Group, id=pk)
        print(gr.group_owner)
        if gr.group_owner != request.user:
            raise Http404("Page does not exist")
        else:
            form = NoteCreateForm()
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

    def post(self, request, pk):
        form = NoteCreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        note = form.save(commit=False)
        note.owner = self.request.user
        note.group_id_id = pk
        note.save()
        return redirect(self.success_url)
    
    
class UpdateView(LoginRequiredMixin, View):
    template_name = 'form.html'
    success_url = reverse_lazy('todo:all')

    def get(self, request, pk):
        note = get_object_or_404(Note, id=pk, owner=self.request.user)
        form = NoteCreateForm(instance=note)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        note = get_object_or_404(Note, id=pk, owner=self.request.user)
        form = NoteCreateForm(request.POST, request.FILES or None, instance=note)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        note = form.save(commit=False)
        note.save()

        return redirect(self.success_url)
    
    
class DeleteView(OwnerDeleteView):
    model = Note
    template_name = "delete.html"
    

class GroupCreateView(LoginRequiredMixin, View):
    template_name = 'form.html'
    success_url = reverse_lazy('todo:all')

    def get(self, request, pk=None):
        form = GroupCreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = GroupCreateForm(request.POST)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        group = form.save(commit=False)
        group.group_owner = self.request.user
        group.save()
        return redirect(self.success_url)
    
    
class GroupUpdateView(LoginRequiredMixin, View):
    template_name = 'form.html'
    success_url = reverse_lazy('todo:all')

    def get(self, request, pk):
        group = get_object_or_404(Group, id=pk, group_owner=self.request.user)
        form = GroupCreateForm(instance=group)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        group = get_object_or_404(Group, id=pk, group_owner=self.request.user)
        form = GroupCreateForm(request.POST, request.FILES or None, instance=group)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        group = form.save(commit=False)
        group.save()

        return redirect(self.success_url)


class GroupDeleteView(GroupOwnerDeleteView):
    model = Group
    template_name = "group_delete.html"
    
    
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError


@method_decorator(csrf_exempt, name='dispatch')
class AddDoneView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        n = get_object_or_404(Note, id=pk)
        done = Done(user=request.user, thing=n)
        try:
            done.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteDoneView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        n = get_object_or_404(Note, id=pk)
        try:
            done = Done.objects.get(user=request.user, thing=n).delete()
        except Done.DoesNotExist as e:
            pass

        return HttpResponse()