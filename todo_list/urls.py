from django.urls import path
from django.views.generic import RedirectView
from .import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='home', permanent=False)),
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('add/', views.add_task, name='add_task'),
    path('task/delete/<int:task_id>', views.delete_task, name='delete_task'),
    path('task/toggle-complete/<int:task_id>', views.toggle_complete, name='toggle_complete'),
    path('task/toggle-important/<int:task_id>', views.toggle_important, name='toggle_important'),
    path('task/edit/<int:task_id>', views.edit_task, name='edit_task'),

]