from django.shortcuts import render

def dashboard(request):
    # Add any context you want to send to the template here
    return render(request, 'online_retail_template/dashboard.html')


def home(request):
    return render(request, 'online_retail_template/dashboard.html')

def orders(request):
    return render(request, 'online_retail_template/orders.html')

def inventory(request):
    return render(request, 'online_retail_template/inventory.html')

def procurement(request):
    return render(request, 'online_retail_template/procurement.html')

def crm(request):
    return render(request, 'online_retail_template/crm.html')

def settings_view(request):
    return render(request, 'online_retail_template/settings.html')

def help_view(request):
    return render(request, 'online_retail_template/help.html')

def search(request):
    return render(request, 'online_retail_template/search.html')

def profile(request):
    return render(request, 'online_retail_template/profile.html')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('online_retail_dash:home')