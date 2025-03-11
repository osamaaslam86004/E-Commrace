from django.shortcuts import render


def maintenance(request):
    return render(request, "503.html", context=None, status=503)


def page_not_found(request, exception):
    return render(request, "404.html", context=None, status=404)


def server_error(request):
    return render(request, "500.html", context=None, status=500)


def bad_request(request, exception):
    return render(request, "400.html", context=None, status=400)


def permission_denied(request, exception):
    return render(request, "403.html", context=None, status=403)


def page_not_allowed(request, exception):
    return render(request, "405.html", context=None, status=405)
