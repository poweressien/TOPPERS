from django.shortcuts import render

def home(request):        return render(request, 'home.html')
def login_page(request):  return render(request, 'auth/login.html')
def register_page(request): return render(request, 'auth/register.html')
def dashboard(request):   return render(request, 'game/dashboard.html')
def play(request):        return render(request, 'game/play.html')
def leaderboard(request): return render(request, 'leaderboard.html')
def profile(request):     return render(request, 'profile.html')
def about(request):       return render(request, 'about.html')
def contact(request):     return render(request, 'contact.html')
def terms(request):       return render(request, 'terms.html')
def privacy(request):     return render(request, 'privacy.html')
