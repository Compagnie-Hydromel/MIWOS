from MIWOS.libs.sql.association import BelongsTo
from MIWOS.model import Model


class Message(Model):
    _belongs_to = [BelongsTo("user")]
