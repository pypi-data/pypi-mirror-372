"""pretty sure this is all set in the AM core repo, but this was helpful in my repo for a time"""


def global_playground_session():
    session_context = global_session()
    session_context.__enter__()

    return session_context


def global_playground_session_2():
    "setup a global session to lazy field don't fail on us"
    from contextlib import nullcontext

    return nullcontext(global_session())


async def aglobal_playground_session():
    """Setup a global async session that persists for interactive development"""
    from contextlib import nullcontext

    session_context = aglobal_session()
    # Get the first yield value from the async generator
    context = await anext(session_context.__aiter__())
    return nullcontext(context)


# aglobal_playground_session()
ctx = global_playground_session()
