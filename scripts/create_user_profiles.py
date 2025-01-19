import os
import django

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos.settings')
django.setup()

from django.contrib.auth.models import User
from posApp.models import UserProfile  # Ajustez si votre modèle est dans un autre module

def create_profiles_based_on_is_superuser():
    users_without_profile = User.objects.filter(profile__isnull=True)

    for user in users_without_profile:
        if user.is_superuser == 1:
            user_type = 'admin'
        elif user.is_superuser == 2:  # Si 2 est une valeur personnalisée
            user_type = 'binome'
        else:
            user_type = 'employe'

        UserProfile.objects.create(user=user, user_type=user_type)
        print(f"Profil créé pour {user.username} avec type {user_type}")

    print(f"{users_without_profile.count()} profils créés.")

if __name__ == "__main__":
    create_profiles_based_on_is_superuser()
