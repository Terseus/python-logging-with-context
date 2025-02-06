# How to use it

The expected workflow is:

* set up your logging system.
* initialize the global context.
* add global context values before writing messages or calling methods or functions that may write messages.
* shutdown the global context before shutting down the application (optional, but recommended).


## Using the global context as a context manager

After configuring your application's logging, initialize the global context:

```python
import logging

from logging_with_context.global_context import global_context_initialized


def main():
    logging.basicConfig(level=logging.INFO)  # Or any other way to setup logging.
    with global_context_initialized():
        # The global context will be available inside this context manager.
```

Once you've initialized it you can add global context to all the loggers using the context manager `add_global_context`.

It accepts a dictionary with the values you want to include in all the logging messages, which will get removed from the loggers once the context manager finishes:

```python
import logging

from logging_with_context.global_context import add_global_context


# ... somewhere in your app ...

logger = logging.getLogger(__name__)


with add_global_context({"user_id": user_id, "request_id": request_id}):
    # This message will include the keys "user_id" and "request_id" in its `extra` fields.
    logger.info("The user tried to authenticate with an invalid access token")
```


## Using the automatic init

If you don't want to customise the initialization you can let `add_global_context` automatically handle the init and shutdown for you:

```python
import logging

from logging_with_context.global_context import add_global_context


def main():
    logging.basicConfig(level=logging.INFO)  # Or any other way to setup logging.
    with add_global_context({"user_id": 10}):
        # Here the context is automatically initialized.
        # It'll also be automatically shutdown once this context manager finishes.
```


## Using the init/shutdown API

In case you want to customise the initialization but can't use the context manager, you can use the manual initialization and shutdown API:

```python
import logging

from logging_with_context.global_context import init_global_context, shutdown_global_context


def main():
    logging.basicConfig(level=logging.INFO)  # Or any other way to setup logging.
    init_global_context()


# ... somewhere in your app ...
logger = logging.getLogger(__name__)


with add_global_context({"user_id": user_id, "request_id": request_id}):
    # The `add_global_context` usage is the same.
    logger.info("The user tried to authenticate with an invalid access token")


# Your app shutdown routine.
def app_shutdown():
    # ... other cleanup ...
    shutdown_global_context()
```

However in complex setups where you need to use specific loggers you'll need to send the same loggers to `init_global_context` and `shutdown_global_context`; see [Caveats](#caveats) section.


## Showing the context

To show the context you need a `Formatter` that somehow uses the context in the log messages produced.

For example, the logging handler in Python applications running at AWS Lambda handles this automatically by adding the context provided in `extra` as labels to the log struct, separated from the message.

If you're logging to a `StreamHandler` you can use `logging_with_context.formatters.ExtraTextFormatter`, which accepts the same options as the standard library `Formatter`.

You can use it instead of the default `Formatter` in your logging setup:

```yaml
version: 1

formatters:
    contextual:
        class: logging_with_context.formatters.ExtraTextFormatter
        format: '%(levelname)s %(message)s'

handlers:
    console:
        class: logging.StreamHandler
        level: DEBUG
        formatter: contextual
        stream: ext://sys.stdout

root:
    level: DEBUG
    handlers: [console]
```

If you're modifying the logging setup made by other part of an application, you can attach the `ExtraTextFormatter` and keep using your defined formatting options by passing it the existing `Formatter` as a parent:
```python
import logging

from logging_with_context.formatters import ExtraTextFormatter

def main():
    logging.basicConfig(level=logging.INFO)
    for handler in logging.getLogger().handlers:
        handler.setFormatter(ExtraTextFormatter(parent=handler.formatter))
```

`ExtraTextFormatter` uses the format `<message> |context_var_1|value|context_var_2|value|`, which is expected to be machine-processing friendly.

It delegates on the `repr` method of most values to produce the value output; this behavior can be extended to handle custom types.


## Caveats

The global context implementation works by attaching a `Filter` object which reads the context and add it to each message.

This works in simple cases (e.g. CLI applications) but can fall short in application with more complex logging setups which attach handlers to specific loggers other than the root logger.

The API accepts a list of loggers where the `Filter` will be attached in these cases:

```python
import logging

from logging_with_context.global_context import global_context_initialized


def app_entrypoint():
    # Attach the global context to the handlers of the root logger and the "app" logger.
    with global_context_initialized(logging.getLogger(), logging.getLogger("app")):
        ...
```
