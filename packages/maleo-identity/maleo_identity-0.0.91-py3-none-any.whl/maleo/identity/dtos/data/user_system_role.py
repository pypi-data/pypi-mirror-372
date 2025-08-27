from maleo.soma.mixins.general import UserId
from maleo.metadata.schemas.data.system_role import SimpleSystemRoleMixin


class UserSystemRoleDTO(
    SimpleSystemRoleMixin,
    UserId,
):
    pass
