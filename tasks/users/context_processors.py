from .models import Profile


def user_roles(request):
    ctx = {'user_profile': None, 'is_company_admin': False}
    if request.user.is_authenticated:
        try:
            prof = request.user.profile
            ctx['user_profile'] = prof
            ctx['is_company_admin'] = prof.role == Profile.Role.ADMIN
        except Profile.DoesNotExist:
            pass
    return ctx
