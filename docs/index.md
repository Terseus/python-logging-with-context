# Introduction

This library provides utilities to easily add context to logging messages and to show them, promoting a logging style that separates the log message from its contextual values.

It helps you turning this:

```python
logger.info("Reading user %s posts", user_id)
posts = get_posts(user_id)
logger.info("User %s have %d posts", user_id, len(posts))
```

Into this:

```python
with add_global_context({"user_id": user_id}):
    logger.info("Reading user posts")
    posts = get_posts(user_id)
    logger.info("User posts readed", extra={"posts_count": len(posts)})
```

## Motivation

When adding logging messages it's common to show some contextual information on it not directly related to the message, for example `The user <user-id> tried to authenticate with an invalid access token`.

Orchestrate a monitorization platform that extracts information from the logs with these kind of messages is really hard:

- Sometimes it's impossible to match a single message with a regular expression due to reuse the same format over and over again (e.g. `The user <user-id> ...`).
- The programmers don't always follow the same format (e.g. `The user <user-id>`, `User: <user-id>`, `user=<user-id>`, etc).

This problem can be fixed by using a well-defined format where the log message and the context values of the message are served separately.

The Python logging module in the standard library already provides a way for doing this: instead of adding placeholders to the message, you can use the `extra` keyword to provide the contextual values of the message, then it's up to the configured formatter to format the values.

This library provides utilities and logging abstractions to ease the use of this practice.

## Prerrequisites

Python 3.9 or greater


## Install

Install the package [logging-with-context](https://pypi.org/project/logging-with-context).

Using pip:

```bash
$ pip install logging-with-context
```

Or using [uv](https://docs.astral.sh/uv/):

```bash
$ uv add logging-with-context
```

## License

MIT
