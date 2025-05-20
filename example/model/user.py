from MIWOS.libs.sql.association import HasMany
from MIWOS.model import Model
import hashlib


class User(Model):
    _has_many = [HasMany("messages")]
    _hidden_attributes = ["password"]

    def beforeSave(self):
        if self.isDirty("password"):
            self.password = hashlib.sha512(
                self.password.encode("utf-8")).hexdigest()

    def checkPassword(self, password):
        return self.password == hashlib.sha512(
            password.encode("utf-8")).hexdigest() or self.password == password
