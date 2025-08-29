from discord import Message, PartialMessage
from typing import Union
from re import search

def utils_get_message(ctx: Message, message: Union[int, str]) -> PartialMessage:
    """
    Returns the message object of the specified message ID or link.
    Message is only available in the same server as the command and in the same channel.
    If the message is a link, it must be in the format: https://discord.com/channels/{guild_id}/{channel_id}/{message_id}
    """

    if isinstance(message, int):
        return ctx.channel.get_partial_message(message)

    elif isinstance(message, str):
        match = search(r'https://discord\.com/channels/(\d+)/(\d+)/(\d+)', message)
        if not match:
            raise Exception("Invalid message link format. Use a valid Discord message link.")
        guild_id = int(match.group(1))
        channel_id = int(match.group(2))
        message_id = int(match.group(3))

        if guild_id != ctx.guild.id:
            raise Exception("The message must be from the same server as the command !")

        return ctx.guild.get_channel(channel_id).get_partial_message(message_id)

    raise Exception(f"Message must be an integer or a string, not {type(message)} !")
