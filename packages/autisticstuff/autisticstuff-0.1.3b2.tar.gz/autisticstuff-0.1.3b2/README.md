# autisticstuff
-- library from autists for... idek
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-GNUv3.0-green.svg)

[We are on pypi.org](https://pypi.org/project/autisticstuff/)

## Modules:

### fastapi - unified response system with exception handling and premade schemas for sqla.layer architecture; also some utils

### safe - RetryableClientSession, retey_wtih_backoff and more

### logs - logging utilities: InterceptHandler and more
- **InterceptHandler** class for low-level interception of `logging` loggers by name to `loguru` log engine
- **get_logger** function-factory for getting cached instances of `loguru.Logger` binded with `loguru_name` attribute, which is included in `extra` at log processing
- **Setup interceptions** for custom logging.Logger instances by name
- **Add your own logger factory** to InterceptHandler, if you do not like loguru. It just needs to have `.opt()` implemented.

### sqla - SQLAlchemy addons
- **Base for layered architecture**, containing **BaseMapping** with a couple of preimplemented methods and **BaseRepository** with mostly every operation on model possible included.
- **PydanticJSON** type for `mapped_column()` with automated serialization & validation on update.
- Updating models with callback depending on flow of environment (sync/async), also possible to pass updated attribute to callback
- Validate dictionary for model creation

### utils - .env parsing, cache-wraps for instances
- **LRU-Cache wrappers for object instances** - **cache** your DB, Settings or anything else - and fetch it with ease from **every** place in code
- **AppSettings base class** for **easy and type-checked** environment variables reading with **ability to fetch variables from property post-initialization**


## Contribute:
- Just branch out in the repository and submit a pull-request after completion.
