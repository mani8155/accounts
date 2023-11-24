from .forms import RegisterForm, LoginForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


def user_register(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # print(form.cleaned_data)

            user_name = form.cleaned_data['username']
            mobile_no = form.cleaned_data['mobile_no']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            if password == confirm_password:
                # print("password correct")

                if User.objects.filter(username=user_name).exists():
                    messages.info(request, "already user exists ")
                    return redirect('user-register')

                else:
                    # print("user create")
                    user = User.objects.create_user(username=user_name, first_name=mobile_no, password=confirm_password)
                    return redirect('user-login')

            else:
                messages.info(request, "password not matching")
                return redirect('user-register')

    context = {"form": form}
    return render(request, 'register.html', context)


def user_login(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # print(form.cleaned_data)
            user_name = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(username=user_name, password=password, user=request.user)

            if user is not None:
                auth.login(request, user)
                return redirect('accounts')

            else:
                messages.info(request, 'invalid user name or password')
                return redirect('user-login')

    context = {"form": form}
    return render(request, 'login.html', context)


@login_required(login_url='login/')
def logout_view(request):
    logout(request)
    return redirect('user-login')





