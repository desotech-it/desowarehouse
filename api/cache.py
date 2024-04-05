import redis
from datetime import datetime
from typing import Optional

from user import User, user_repository

DATE_FMT = '%Y-%m-%d'

# TODO: add error handling
r = redis.Redis(host='redis', decode_responses=True, protocol=3)

def get_user(username: str) -> Optional[User]:
    user = r.hgetall('user:session:' + username)
    if len(user) == 0:
        user = user_repository.get_by_mail(username)
        mapping = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'mail': user.mail,
            'birthdate': user.birthdate.strftime(DATE_FMT),
            'role': user.role,
        }
        r.hset('user:session:' + username, mapping=mapping)
    else:
        user = User(
            id=user['id'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            mail=user['mail'],
            birthdate=datetime.strptime(user['birthdate'], DATE_FMT).date(),
            role=user['role'],
        )

    return user
