import uvicorn
from litestar import Litestar, get


@get("/echo")
async def echo(
    message: str = "The message to echo", shout: bool = False, repeat: int = 1
) -> dict:
    """Echos the message with options to shout and repeat.

    :param message: The message to echo.
    :param shout: If True, the message will be in uppercase.
    :param repeat: Number of times to repeat the message.
    :return: A dictionary containing the echo result.
    """
    if shout:
        message = message.upper()

    result = [message] * repeat
    return {"echo": "\n".join(result)}


def run_server() -> None:
    app = Litestar([echo])
    uvicorn.run(app)
