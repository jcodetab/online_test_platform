from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required




def home(request):
    return render(request, 'registration/home.html') 


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)  
        if form.is_valid():
            user = form.save()  
            login(request, user)  
            return redirect('home')  
    else:
        form = UserCreationForm()  

    return render(request, 'registration/register.html', {'form': form})
 

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('personal_cabinet')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, "registration/profile.html")











 



























