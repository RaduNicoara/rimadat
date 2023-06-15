from django.http import HttpResponse


def view_test(request):
    return HttpResponse("<h1>Yay</h1>")
