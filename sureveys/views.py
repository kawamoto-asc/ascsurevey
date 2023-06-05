from django.shortcuts import render

# トップ画面
def top(request):
    return render(request, "sureveys/top.html")