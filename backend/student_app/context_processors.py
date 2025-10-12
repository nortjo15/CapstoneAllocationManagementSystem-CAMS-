from admin_app.models import Round

def active_rounds(request):
    return {
        'active_rounds': Round.objects.filter(is_active=True)
    }