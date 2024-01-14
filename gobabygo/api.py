from typing import List
from ninja import NinjaAPI, Schema, ModelSchema, Field

from gobabygo.models import User

api = NinjaAPI()


class UserEchoSchema(ModelSchema):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


@api.get("/whoami", response=UserEchoSchema)
def whoami(request):
    return request.user
