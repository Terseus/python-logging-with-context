# Logging with context (contextual logging)

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

## Documentation

You can read the docs at https://terseus.github.io/python-logging-with-context/

## License

MIT
