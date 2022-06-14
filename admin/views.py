from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from starlette import status
from fastapi import Request
from auth import schemas as auth_schema
from auth import services as auth_services
from admin import dependencies as admin_dependencies
from fastapi_pagination import paginate
from admin import services as admin_services


async def users(
    request: Request,
    admin_user: auth_schema.UserSchema = Depends(admin_dependencies.get_super_user),
):
    """
        returns all the users from the database in paginated form
        only superusers/admins are allowed to access this route
    {
      "items": [
        {
          "id": int,
          "username": "string",
          "is_admin": bool
        }
      ],
      "total": 0,
      "page": 1,
      "size": 1
    }
    """
    if admin_user:
        return paginate(await admin_services.get_users())
    else:
        raise HTTPException(
            detail="you are not authorized to access this resource",
            status_code=status.HTTP_403_FORBIDDEN,
        )


async def create_user(
    user: auth_schema.UserSchema,
    request: Request,
    request_user: auth_schema.UserSchema = Depends(admin_dependencies.get_super_user),
):
    """
        admin specific route pass the following to the body
        returns user in json form in the username passed doesn't exist
    {
      "id": int,
      "username": "string",
      "password": "string",
      "is_admin": bool
    }

    """
    if not request_user:
        raise HTTPException(
            detail="you are not allowed to view this resource",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user = await admin_services.add_user(user)
    if not user[0]:
        raise HTTPException(
            detail=user[1],
            status_code=status.HTTP_409_CONFLICT,
        )
    else:
        return user[1]


async def delete_user(
    username: str,
    request_user: auth_schema.UserSchema = Depends(
        admin_dependencies.get_super_user,
    ),
):
    """
    admin specific route username -> username (parameter) of the user
    deletes the user from the database
    """
    if not request_user:
        raise HTTPException(
            detail="you are not allowed to view this resource",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    if user := await auth_services.get_user_by_username(username=username):
        await admin_services.remove_user(user=user)
        return {"message": "user deleted"}
    raise HTTPException(
        detail="user not found",
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def patch_user(
    username: str,
    user: auth_schema.UserUpdateSchema,
    request_user: auth_schema.UserSchema = Depends(
        admin_dependencies.get_super_user,
    ),
):
    """
        admin specific route username -> username (parameter) of the user
    {
      "username": "string",
      "is_admin": bool
    }
    """
    if not request_user:
        raise HTTPException(
            detail="you are not allowed to view this resource",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    if user_from_db := await auth_services.get_user_by_username(username=username):
        result = await admin_services.update_user(user=user_from_db, request_data=user)
        if not result[0]:
            raise HTTPException(
                detail=result[1],
                status_code=status.HTTP_409_CONFLICT,
            )
        return result[1]
    raise HTTPException(
        detail="user not found",
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def get_all_code(
    user: auth_schema.UserSchema = Depends(admin_dependencies.get_super_user),
):
    if not user:
        raise HTTPException(
            detail="you are not allowed to update this code",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return paginate(await admin_services.get_all_from_db())
