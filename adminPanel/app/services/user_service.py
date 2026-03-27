from app.models.user import User
from app.core.security import hash_password


class UserService:
    def __init__(self, db_session):
        self.db = db_session

    def register(self, username: str, password: str) -> User:
        existing = self.db.query(User).filter(User.username == username).first()
        if existing:
            return None

        user = User(
            username=username,
            password_hash=hash_password(password)
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, username: str, password: str):
        user = self.db.query(User).filter(User.username == username).first()
        if not user or user.password_hash != hash_password(password):
            return None
        return user