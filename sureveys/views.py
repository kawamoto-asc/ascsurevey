from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# トップ画面
@login_required
def top(request):
    return render(request, "sureveys/top.html")