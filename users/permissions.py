from users.constants import GROUP_TYPE_ADMIN, GROUP_TYPE_HEAD_OF_DEPARTMENT


def get_actor_group_type(user):
    if not user or not user.is_authenticated:
        return None

    profile = getattr(user, "profile", None)
    if profile is None:
        return None

    return profile.group_type


def is_admin_user(user):
    return get_actor_group_type(user) == GROUP_TYPE_ADMIN


def is_head_of_department_user(user):
    return get_actor_group_type(user) == GROUP_TYPE_HEAD_OF_DEPARTMENT
