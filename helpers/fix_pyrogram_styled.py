import pyrogram_styled.types.messages_and_media.rich_block as rb
from pyrogram_styled import types


old_parse = rb.types.Location._parse


def fixed_parse(client, geo_point):
    return old_parse(client, geo_point)


rb.types.Location._parse = fixed_parse