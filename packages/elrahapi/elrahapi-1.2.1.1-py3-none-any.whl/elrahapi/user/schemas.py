from pydantic import BaseModel, Field,EmailStr,field_validator
from datetime import datetime

from elrahapi.authorization.user_role.meta_models import MetaUserRoleModel

from elrahapi.authorization.user_privilege.meta_models import MetaUserPrivilegeModel

class UserBaseModel(BaseModel):
    email: EmailStr = Field(example="user@example.com")
    username: str = Field(example="Harlequelrah")
    lastname: str = Field(example="SMITH")
    firstname: str = Field(example="jean-francois")


class UserCreateModel:
    password: str = Field(example="m*td*pa**e")



class UserPatchModel:
    email: EmailStr | None = Field(example="user@example.com",default=None)
    username: str | None = Field(example="Harlequelrah",default=None)
    lastname: str | None = Field(example="SMITH",default=None)
    firstname: str | None = Field(example="jean-francois",default=None)

class UserUpdateModel:
    pass

class UserReadModel:
    id: int
    is_active: bool
    attempt_login:int
    date_created: datetime
    date_updated: datetime



class UserFullReadModel(UserReadModel):
    user_roles:list["MetaUserRoleModel"] = []
    user_privileges: list["MetaUserPrivilegeModel"]=[]



class UserRequestModel(BaseModel):
    username: str | None = None
    email: str | None = None

    @property
    def sub(self):
        return self.username or self.email

    @field_validator('sub',check_fields=False)
    @classmethod
    def validate_sub(cls,value):
        if not value :
            raise ValueError("username or email must be provided")
        return value


class UserLoginRequestModel(UserRequestModel):
    password: str



class UserChangePasswordRequestModel(UserRequestModel):
    current_password: str
    new_password: str
