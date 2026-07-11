from django.shortcuts import render, redirect
from .forms import RegisterForm, TaskForm
from .models import Task
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Case, When, Value
from django.utils import timezone

# Create your views here.

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'authentication/register.html',{'form':form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'authentication/login.html')


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('login')
    else: 
        return redirect('home')

def _home_context(request, task_form=None):
    tasks = Task.objects.filter(user=request.user)

    active_tasks = tasks.filter(completed=False, important=False).order_by(
        Case(When(due_date__isnull=True, then=Value(1)), default=Value(0)),
        "due_date",
    )
    important_tasks = tasks.filter(completed=False, important=True)
    completed_tasks = tasks.filter(completed=True)

    return {
        "active_tasks": active_tasks,
        "important_tasks": important_tasks,
        "completed_tasks": completed_tasks,
        "form": task_form or TaskForm(),
        "today": timezone.localdate(),
    }

@login_required
def home(request):
    return render(request, "view_display/home.html", _home_context(request))

@login_required
def add_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('home')

        context = _home_context(request, task_form=form)
        context["show_add_modal"] = True
        return render(request, "view_display/home.html", context)

    return redirect('home')


@login_required
def toggle_complete(request, task_id):

    task = get_object_or_404(
        Task,
        id=task_id,
        user=request.user
    )

    task.completed = not task.completed
    task.save()

    return redirect("home")

@login_required
def toggle_important(request, task_id):

    task = get_object_or_404(
        Task,
        id=task_id,
        user=request.user
    )

    task.important = not task.important
    task.save()

    return redirect("home")

@login_required
def delete_task(request, task_id):

    task = get_object_or_404(
        Task,
        id=task_id,
        user=request.user
    )

    task.delete()

    return redirect("home")

@login_required
def edit_task(request, task_id):

    task = get_object_or_404(
        Task,
        id=task_id,
        user=request.user
    )

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            form.save()
            return redirect("home")

    return redirect("home")