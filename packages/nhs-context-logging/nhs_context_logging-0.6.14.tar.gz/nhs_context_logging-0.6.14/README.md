# NHS Context Logging

this context logging library is designed to make adding good quality *structured* logs EASY and make source code easy to read, removing 'boilerplate' logging from the code and allowing the eye to focus on what the code does.
NOTE: when using context logging, logs are emitted when exiting the context (when the function call ends or wrapped context otherwise exits)

# quick start

### contributing
contributors see [contributing](CONTRIBUTING.md)

### installing

```shell
pip install nhs-context-logging
```

### logging
out of the box this framework will create structured logs with some default behaviours that we think work well

```python
from nhs_context_logging import app_logger, log_action

@log_action(log_reference="MYLOGREF", log_args=["my_arg"])
def do_a_thing(my_arg: int,  another_arg: str):
    pass

if __name__ == "__main__":
    app_logger.setup("mytool")
```


## action logging



###  log_action decorator

you can decorate a function with the `log_action` decorator
```python
from nhs_context_logging import log_action

@log_action(log_reference="MYLOGREF")
def do_a_thing(my_arg: int,  another_arg: str):
    pass

```

out of the box this will give you rich logs associated with this logged action,
for example:
- timestamp - unix timestamp
- internal_id - a unique id preserved through nested log contexts
- action_duration - action duration in seconds
- action_status -  "succeeded|failed|error"  (failed/error being expected or unexpected exceptions .. see below)
- log_info - structure with log level, code path, line no, function name, thread, process id etc. 

```json
{"timestamp": 1687435847.340391, "internal_id": "d2c867f7f89a4a10b3257355dc558447", "action_duration": 0.00001, "action_status": "succeeded", "log_info": {"level": "INFO", "path": "/home/zaphod/spine/nhs-context-logging/tests/logger_tests.py", "line_no": 171, "func": "do_a_thing", "pid": 4118793, "thread": 139808108545856}}
```

when decorating a function it's also easy to capture function args
```python
from nhs_context_logging import log_action

@log_action(log_reference="MYLOGREF", log_args=["my_arg"])
def do_a_thing(my_arg: int,  another_arg: str):
    pass

```

adding log_args will capture named arguments and add to the logged action context. e.g.
```json
{"timestamp": 1687435847.340391, "internal_id": "...", "my_arg": 12354}
```


within a logged action context .. you can also add additional fields to log 
```python
from nhs_context_logging import log_action, add_fields
from mylib import another_thing


@log_action(log_reference="MYLOGREF", log_args=["my_arg"])
def do_a_thing(my_arg: int,  another_arg: str):
    result = another_thing(my_arg)
    add_fields(another_thing_result=result)
    return result

```

this allows you to incrementally build up the data in a log line 
```json
{"timestamp": 1687435847.340391, "internal_id": "...", "my_arg": 12354, "another_thing_result": "win!"}
```

You can also log the action result directly with `log_result=True` (for non-generator functions):

```python 
@log_action(log_reference="MYLOGREF", log_args=["my_arg"], log_result=True)
def do_a_thing(my_arg: int, another_arg: str):
    result = another_thing(my_arg)
    return result
```

which appends `action_result` to your log:
```json
{"timestamp": 1687435847.340391, "internal_id": "...", "my_arg": 12354, "action_result": "win!"}
```

### Exceptions and Errors

#### Unexpected Exceptions
by default the log action context will also log exceptions info when raised in a wrapped context

```python
from nhs_context_logging import log_action

@log_action(log_reference="MYLOGREF", log_args=["my_arg"])
def do_a_thing(my_arg: int,  another_arg: str):
    raise ValueError(f'eek! {my_arg}')
```
unexpected exceptions will result in `action_status=failed` and include exception detail and INCLUDE STACK TRACE
```json
{"timestamp": 1687435847.340391, "action_status": "failed", "internal_id": "...", "my_arg": 12354,"error_info": { "args": [1,2,3], "error": "ValueError('eek 1232')", "line_no": 69, "traceback": "file '/home..."}}
```

![failed action error info](img-action-failed.png)

#### Expected Exceptions
with the `expected_errors` argument, which takes a `tuple` of types, you can use exceptions for business process flow without filling your logs with stack trace information

```python
from nhs_context_logging import log_action

@log_action(log_reference="MYLOGREF", log_args=["my_arg"], expected_errors=(ValueError,))
def do_a_thing(my_arg: int,  another_arg: str):
    raise ValueError(f'eek! {my_arg}')
```
expected exceptions are considered as business errors and will result in `action_status=error` and include exception detail and  NO STACK TRACE
```json
{"timestamp": 1687435847.340391, "action_status": "failed", "internal_id": "...", "my_arg": 12354,"error_info": { "args": [1,2,3], "error": "ValueError('eek 1232')", "line_no": 69, "traceback": "file '/home..."}}
```


![expected error info](img-action-error.png)

## testing

the library comes with a some pytest log capture fixtures .. 


```python
# conftest.py
# noinspection PyUnresolvedReferences
from nhs_context_logging.fixtures import *   # noqa: F403

# mytest.py
from nhs_context_logging import add_fields, log_action


@log_action(log_args=["my_arg"])
def another_thing(my_arg) -> bool:
    return my_arg == 1


@log_action(log_reference="MYLOGREF", log_args=["my_arg"])
def do_a_thing(my_arg: int, _another_arg: str):
    result = another_thing(my_arg)
    add_fields(result=result)
    return result


def test_capture_some_logs(log_capture):
    std_out, std_err = log_capture
    expected = 1232212
    do_a_thing(expected, 123)

    log = std_out[0]
    assert log["action"] == "another_thing"
    assert log["action_status"] == "succeeded"
    assert log["my_arg"] == expected

    log = std_out[1]
    assert log["action"] == "do_a_thing"
    assert log["my_arg"] == expected
    assert log["action_status"] == "succeeded"
    assert log["result"] is False



```



## temporary global fields

you can also add in global fields (global to the the current log context that is)

```python
from nhs_context_logging import temporary_global_fields, log_action


@log_action()
def another_thing():
    pass

@log_action(log_reference="MYLOGREF", log_args=["my_arg"])
def do_a_thing(my_arg: int,  another_arg: str):
    result = another_thing(my_arg)
    return result


@log_action()
def main():
    with temporary_global_fields(add_this_to_all_child_logs="AAAA"):
        do_a_thing(1234)

```
will add the `add_this_to_all_child_logs` field to all child log contexts created within the global fields context manager.


## logger setup

### simple setup

```python
from nhs_context_logging import app_logger, log_action


@log_action()
def main():
    # this does the work with logging
    pass

if __name__ == "__main__":
    app_logger.setup("my_awesome_app")
    main()
```

### async support

since with `asyncio` different tasks will be running concurrently within the same thread, to ensure that logging works as intended  passing `is_async=True` to `app_logger.setup` will register the `_TaskIsolatedContextStorage` so action contexts within different async tasks will not interfere with each other

```python
import asyncio
from nhs_context_logging import app_logger, log_action


@log_action()
async def child_action():
    await asyncio.sleep(10)

@log_action()
async def main():
    # this does the work with logging
    await child_action()

if __name__ == "__main__":
    app_logger.setup("my_awesome_app", is_async=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```



## traditional logging
the logger also supports all the 'standard' logging interfaces ..
```python
from nhs_context_logging import app_logger
from mylib import another_thing

def do_a_thing(my_arg: int, another_arg: str):
  app_logger.info(message=f"started doing a thing, with args {my_arg} and {another_arg}")
  try:
    result = another_thing(my_arg)
  except Exception as err:
      app_logger.exception()
      raise 
  app_logger.info(message=f"another thing result = {result}")
  return result
  
```

but will also accept an args dict as the first arg
```python

from nhs_context_logging import app_logger
app_logger.info(dict(arg1='aaa'))
```

and a callable args source 

```python

from nhs_context_logging import app_logger
app_logger.info(lambda: dict(arg1='aaa'))
```

or a mix with kwargs
```python
from nhs_context_logging import app_logger
def lazy_args():
    return dict(message=1234, thing="bob")

app_logger.info(lazy_args, log_reference="MESH1234")

```