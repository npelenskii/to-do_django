from django.urls import path, reverse_lazy
from . import views
from django.views.generic import TemplateView


app_name = 'todo'

urlpatterns = [
    path('', views.ListView.as_view(), name='all'),
    path("register", views.register_request, name="register"),
    path('<int:pk>/create', 
         views.NoteCreateView.as_view(success_url=reverse_lazy('todo:all')), name='create'),
    path('<int:pk>/update', 
         views.UpdateView.as_view(success_url=reverse_lazy('todo:all')), name='update'),
    path('<int:pk>/delete', 
         views.DeleteView.as_view(success_url=reverse_lazy('todo:all')), name='delete'),
    path('group_create', views.GroupCreateView.as_view(), name='group_create'),
    path('<int:pk>/group_update', 
         views.GroupUpdateView.as_view(success_url=reverse_lazy('todo:all')), name='group_update'),
    path('<int:pk>/group_delete', 
         views.GroupDeleteView.as_view(success_url=reverse_lazy('todo:all')), name='group_delete'),
    path('<int:pk>/done', 
        views.AddDoneView.as_view(), name='thing_done'),
    path('<int:pk>/undone', 
        views.DeleteDoneView.as_view(), name='thing_undone'),
]