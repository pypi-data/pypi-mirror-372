import json
from collections.abc import Callable
from datetime import UTC, datetime
from inspect import ismethod
from typing import Any

from dateutil.parser import ParserError, parse
from discord import Colour, Embed

from ...exceptions import BadColourArgument, EmbedParseError
from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import split_at_substring_zero_depth


def _add_field(embed: Embed, _: str, value: str | None) -> None:
    if value is None:
        return
    if len(embed.fields) == 25:
        raise EmbedParseError("Maximum number of embed fields exceeded (25).")
    data = split_at_substring_zero_depth(value, "|", max_split=2)
    if len(data) == 1:
        raise EmbedParseError("`add_field` payload was not split by |.")
    elif len(data) == 2:
        name = data[0]
        value = data[1]
        inline = False
    elif len(data) == 3:
        name = data[0]
        value = data[1]
        inline = (
            True
            if data[2].lower() == "true"
            else False if data[2].lower() == "false" else None
        )
    else:  # pragma: no cover
        # impossible due to max split of 2 meaning: 1 <= len(data) <= 3
        # but better to have this than to want for it
        raise EmbedParseError("`add_field` payload invalid.")
    if inline is None:
        raise EmbedParseError(
            f"`inline` argument for `add_field` is not a boolean value "
            f"(was `{data[2]}`).",
        )
    embed.add_field(name=name, value=value, inline=inline)


def _set_author(embed: Embed, _: str, payload: str | None) -> None:
    if payload is None:
        return
    data = split_at_substring_zero_depth(payload, "|", max_split=2)
    if len(data) == 1:
        embed.set_author(name=payload)
    elif len(data) == 2:
        if data[0] == "":
            return
        embed.set_author(
            name=data[0],
            url=data[1] if data[1] != "" else None,
        )
    elif len(data) == 3:
        if data[0] == "":
            return
        embed.set_author(
            name=data[0],
            url=data[1] if data[1] != "" else None,
            icon_url=data[2] if data[2] != "" else None,
        )
    else:  # pragma: no cover
        # impossible due to max split of 2 meaning: 1 <= len(data) <= 3
        raise EmbedParseError("`author` payload invalid.")


def _set_colour(embed: Embed, attribute: str, value: str | None) -> None:
    if value is None:
        return
    colour = _string_to_colour(value)
    setattr(embed, attribute, colour)


def _set_image_url(embed: Embed, attribute: str, value: str | None) -> None:
    if value is None:
        return
    method = getattr(embed, f"set_{attribute}")
    method(url=value)


def _set_footer(embed: Embed, _: str, value: str | None) -> None:
    if value is None:
        return
    data = split_at_substring_zero_depth(value, "|", max_split=1)
    if len(data) == 1:
        embed.set_footer(text=value if value != "" else None)
    elif len(data) == 2:
        embed.set_footer(
            text=data[0] if data[0] != "" else None,
            icon_url=data[1] if data[1] != "" else None,
        )
    else:  # pragma: no cover
        # impossible due to max split of 1 meaning: 1 <= len(data) <= 2
        raise EmbedParseError("`footer` payload invalid.")


def _set_timestamp(embed: Embed, _: str, value: str | None) -> None:
    if value is None:
        return
    if value.isdigit():
        ts = datetime.fromtimestamp(int(value), tz=UTC)
    else:
        try:
            ts = parse(value)
        except (ParserError, OverflowError):
            return
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    embed.timestamp = ts


def _string_to_colour(arg: str) -> Colour:
    arg = arg.replace("0x", "").lower()

    if arg[0] == "#":
        arg = arg.removeprefix("#")
    try:
        value = int(arg, base=16)
        if not (0 <= value <= 0xFFFFFF):
            raise BadColourArgument(arg)
        return Colour(value)
    except ValueError:
        arg = arg.replace(" ", "_")
        method = getattr(Colour, arg, None)
        if arg.startswith("from_") or method is None or not ismethod(method):
            raise BadColourArgument(arg)
        return method()


def _value_to_colour(value: Any) -> Colour | None:
    if value is None or isinstance(value, Colour):
        return value
    elif isinstance(value, int):
        return Colour(value)
    elif isinstance(value, str):
        return _string_to_colour(value)
    else:
        raise EmbedParseError(
            f"Received invalid type for colour key (expected Colour | str | int"
            f" | None, got {type(value).__qualname__}).",
        )


def _return_embed(ctx: Context, embed: Embed) -> str:
    try:
        size = len(embed)
    except KeyError as e:
        return str(e)
    if size > 6000:
        return f"`MAX EMBED LENGTH REACHED ({size}/6000)`"
    ctx.response.actions["embed"] = embed
    return ""


def _json_to_embed(text: str) -> Embed:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise EmbedParseError(e) from e

    if data.get("embed"):
        data = data["embed"]
    if data.get("timestamp"):
        data["timestamp"] = data["timestamp"].removesuffix("Z")

    colour = data.pop("colour", data.pop("color", None))

    embed = Embed.from_dict(data)

    if (colour := _value_to_colour(colour)) is not None:
        embed.colour = colour
    return embed


class EmbedBlock(BlockABC):
    """
    This block includes an embed in the tag response.

    There are two ways to use the embed block: manually inputting the accepted embed
    attributes or using properly formatted embed JSON from an embed generator.

    The JSON method allows complete embed customization (including setting attributes
    not supported by the manual method here), while the manual method provides
    control over individual attributes without requiring the entire block to be
    defined at once.

    **Manual**:

    The following embed attributes can be set manually:

    - ``author`` (see notes below)
    - ``title``
    - ``description``
    - ``color``
    - ``url``
    - ``thumbnail``
    - ``image``
    - ``footer`` (see notes below)
    - ``field`` (see notes below)
    - ``timestamp``

    Note:
        Some attributes expect a specially formed payload, these are explained below:

        - ``author``: The payload must be 1, 2, or 3 parts in size, with parts split by
          ``|``. The name is required, the other attributes are optional. If a name and
          an icon should be used *without* providing a website URL, leave the website
          URL empty but keep the ``|`` on either side.

          Valid ``author`` formats::

            {embed(author):name}
            {embed(author):name|website url}
            {embed(author):name|website url|icon url}
            # Note how the website url is left empty but the | are kept on either side
            {embed(author):name||icon url}

        - ``footer``: The payload must be 1 or 2 parts in size, with parts split by
          ``|``. The text is required, the icon URL is optional.

          Valid ``footer`` formats::

            {embed(footer):text}
            {embed(footer):text|icon URL}

        - ``field``: The payload must be 2 or 3 parts in size, with parts split by
          ``|``. The name and value are required, the inline status is optional. If
          inline is not set explicitly, it defaults to :data:`False`.

          Valid ``field`` formats::

            {embed(field):name|value}
            {embed(field):name|value|true}
            {embed(field):name|value|false}

    **Usage**: ``{embed(<attribute>):<value>}``

    **Aliases**: ``embed``

    **Parameter**: ``attribute`` (required)

    **Payload**: ``value`` (required)

    **Examples**::

        {embed(color):#37b2cb}
        {embed(title):Rules}
        {embed(description):Follow these rules to ensure a good experience in our server!}
        {embed(field):Rule 1|Respect everyone you speak to.|false}
        {embed(footer):Thanks for reading!|{guild(icon)}}
        {embed(timestamp):1681234567}

    ----

    **JSON**:

    **Usage**: ``{embed(<json>)}``

    **Aliases**: ``embed``

    **Parameter**: ``json`` (required)

    **Payload**: ``None`` (ignored if JSON is used)

    **Examples**::

        # Note how the JSON sits entirely within the block's parameter section, even
        # when split across several lines.
        {embed({"title":"Hello!", "description":"This is a test embed."})}
        {embed({
            "title":"Here's a random duck!",
            "image":{"url":"https://random-d.uk/api/randomimg"},
            "color":15194415
        })}

    Both methods can be combined to create an embed in a tag. For example, JSON
    can be used to create an embed with fields, and the embed title can be set
    later.

    **Examples**::

        {embed({"fields":[{"name":"Field 1","value":"field description","inline":false}]})}
        {embed(title):my embed title}

    **Response Attribute**:

    This block sets the following attribute on the
    :class:`~ya_tagscript.interpreter.Response` object:

    - :attr:`~ya_tagscript.interpreter.Response.actions`
        - ``actions["embed"]``: :class:`discord.Embed` — The constructed
          :class:`discord.Embed`

    Note:
        This block only sets the ``embed`` actions key as shown above. It is *up to the
        client* to actually send the :class:`discord.Embed` object being constructed.
    """

    ATTRIBUTE_HANDLERS: dict[str, Callable[[Embed, str, str | None], None]] = {
        "author": _set_author,
        "description": setattr,
        "title": setattr,
        "color": _set_colour,
        "colour": _set_colour,
        "url": setattr,
        "thumbnail": _set_image_url,
        "image": _set_image_url,
        "field": _add_field,
        "footer": _set_footer,
        "timestamp": _set_timestamp,
    }

    @property
    def _accepted_names(self) -> set[str]:
        return {"embed"}

    def process(self, ctx: Context) -> str | None:
        if (param := ctx.node.parameter) is None:
            return _return_embed(ctx, ctx.response.actions.get("embed", Embed()))

        parsed_param = ctx.interpret_segment(param)
        lowercase_param = parsed_param.lower()
        try:
            if lowercase_param.startswith("{") and lowercase_param.endswith("}"):
                embed = _json_to_embed(parsed_param)
            elif lowercase_param in self.ATTRIBUTE_HANDLERS:
                embed = ctx.response.actions.get("embed", Embed())
                if (payload := ctx.node.payload) is not None:
                    parsed_payload = ctx.interpret_segment(payload)
                else:
                    parsed_payload = None
                embed = self._update_embed(
                    embed,
                    lowercase_param,
                    parsed_payload if parsed_payload != "" else None,
                )
            else:
                return None
        except EmbedParseError as e:
            return f"Embed Parse Error: {e}"

        return _return_embed(ctx, embed)

    @classmethod
    def _update_embed(cls, embed: Embed, attribute: str, value: str | None) -> Embed:
        handler = cls.ATTRIBUTE_HANDLERS[attribute]
        try:
            handler(embed, attribute, value)
        except Exception as e:
            raise EmbedParseError(e) from e
        return embed
