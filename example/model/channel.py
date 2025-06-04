from MIWOS.model import Model
from MIWOS.libs.sql.association import HasAndBelongsToMany


class Channel(Model):
    _has_and_belongs_to_many = [HasAndBelongsToMany("users")]
