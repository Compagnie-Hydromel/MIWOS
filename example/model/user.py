from MIWOS.libs.sql.association import HasAndBelongsToMany, HasMany
from MIWOS.model import Model
import hashlib
import re


class User(Model):
    _has_many = [HasMany("messages")]
    _hidden_attributes = ["password"]
    _has_and_belongs_to_many = [HasAndBelongsToMany("channels")]
    _validators = {
        "username": lambda x: x is not None and len(x) > 0,
        "password": lambda x: x is not None and len(x) > 3,
        "email": lambda x: x is not None and re.match(r"[^@]+@[^@]+\.[^@]+", x),
    }

    def beforeSave(self):
        if self.isDirty("password"):
            self.password = hashlib.sha512(
                self.password.encode("utf-8")).hexdigest()

    def checkPassword(self, password):
        return self.password == hashlib.sha512(
            password.encode("utf-8")).hexdigest() or self.password == password
