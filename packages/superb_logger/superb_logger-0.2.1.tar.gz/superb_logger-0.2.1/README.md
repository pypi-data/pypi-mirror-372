# superb_logger

---

## 🐍 Basic Usage

```python
from logging import Formatter

from superb_logger import Configurator, Level
from colorlog import ColoredFormatter

colored_formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
    log_colors={
        'DEBUG':    'light_black',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red',
    }
)

configurator = Configurator(
    base_level=Level.DEBUG, 
    console_formatter=colored_formatter
)
log = configurator.get_root_logger()
log.debug("Testing")
log.info("Testing")
log.error("Testing")
log.critical("Testing")
```

---

## 🛠️ Configuration

All configurations are handled through the `Configurator` class:

- Set base logging level (INFO by default)
- Dynamically add/remove loggers
- Use `set_loggers()` to configure multiple loggers at once
- Customize format and date format

---

## 🧪 Testing & Quality

- 100% test coverage with pytest ✅
- Fully documented code 📘
- Safe for production use 💼

---

## 📄 License

MIT License — feel free to use it in any project! 🎉

---

## 🧑‍💻 Made with ❤️ by [@dkurchigin](https://gitverse.ru/dkurchigin)

Let’s make logging fun again! 😄  
Have questions? Open an issue or contribute to the repo!

## 🐙 GITVERSE

🔗 [https://gitverse.ru/dkurchigin/superb_logger](https://gitverse.ru/dkurchigin/superb_logger)
