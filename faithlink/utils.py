# student_profile/utils.py

from accounts.models import CustomUser

def get_parishionerSignup(user):
    # Get users who are not parishioners, not staff, and not superusers
    non_parishioners = CustomUser.objects.filter(
        is_parishioner=False,
        is_staff=False,
        is_superuser=False
    )

    # Count of such users
    non_parishioner_count = non_parishioners.count()

    return {
        'user': user,
        'count': non_parishioner_count,
        'non_parishioners': non_parishioners,
    }
