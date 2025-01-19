from posApp.models import UserProfile

def user_profile(request):
    if request.user.is_authenticated:
        try:
            return {'profile': UserProfile.objects.get(user=request.user)}
        except UserProfile.DoesNotExist:
            return {'profile': None}
    return {}
