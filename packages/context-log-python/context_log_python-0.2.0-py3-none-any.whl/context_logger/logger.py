import logging
import time
import functools
import inspect
import sys
import traceback
import json
from collections import defaultdict
from transformers import pipeline

generator = pipeline("text-generation", model="distilgpt2")
class SmartProfiler:
    """
    Lightweight profiler that captures nested function timings
    using sys.setprofile.
    """
    def __init__(self):
        self.call_stack = []
        self.timings = defaultdict(float)

    def tracer(self, frame, event, arg):
        if event == "call":
            func_name = f"{frame.f_code.co_name} ({frame.f_code.co_filename}:{frame.f_lineno})"
            self.call_stack.append((func_name, time.time()))
        elif event == "return":
            func_name = f"{frame.f_code.co_name} ({frame.f_code.co_filename}:{frame.f_lineno})"
            if self.call_stack:
                name, start = self.call_stack.pop()
                if name == func_name:
                    self.timings[name] += time.time() - start
        return self.tracer

    def __enter__(self):
        sys.setprofile(self.tracer)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        sys.setprofile(None)


class ContextFilter(logging.Filter):
    """Injects caller context automatically into log records."""
    def filter(self, record):
        frame = inspect.currentframe()
        outer_frames = inspect.getouterframes(frame)

        # Pick the right outer frame (skip logging internals)
        if len(outer_frames) > 8:
            caller = outer_frames[8]
            record.context = f"{caller.function} ({caller.filename}:{caller.lineno})"
        else:
            record.context = f"{record.funcName} ({record.filename}:{record.lineno})"
        return True


class ContextLogger:
    def __init__(self, logger, json_mode=False):
        self.logger = logger
        self.json_mode = json_mode
        if not any(isinstance(f, ContextFilter) for f in self.logger.filters):
            self.logger.addFilter(ContextFilter())


    def _suggest_fix(self, error_message: str) -> str:
        prompt = f"Suggest a fix for this Python error:\n{error_message}"
        response = generator(prompt, max_length=50, num_return_sequences=1)
        return response[0]['generated_text']

    def _format_message(
        self, level, msg, record, exc_info=None, extra_context=None, suggestion=None
    ):
        log_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "level": logging.getLevelName(level),
            "message": msg,
            "context": getattr(record, "context", None),
        }

        # If error, capture traceback + auto-suggest
        if exc_info:
            tb_str = "".join(traceback.format_exception(*exc_info))
            log_data["traceback"] = tb_str
            auto_suggestion = self._suggest_fix(str(exc_info[1]))
            if auto_suggestion:
                log_data["suggestion"] = auto_suggestion

        # If manual suggestion is passed explicitly
        elif suggestion:
            log_data["suggestion"] = suggestion

        # Extra context
        if extra_context:
            log_data["extra"] = extra_context

        if self.json_mode:
            return json.dumps(log_data)
        else:
            return (
                f"{log_data['timestamp']} - {log_data['level']} - {log_data['context']} - "
                f"{log_data['message']}"
                + (f"\nTraceback:\n{log_data['traceback']}" if "traceback" in log_data else "")
                + (f"\nSuggestion: {log_data['suggestion']}" if "suggestion" in log_data else "")
            )

    def _log(self, level, msg, *args, exc_info=None, suggestion=None, **kwargs):
        record = self.logger.makeRecord(
            self.logger.name, level, fn="", lno=0, msg="", args=(), exc_info=None
        )
        formatted = self._format_message(
            level, msg, record, exc_info, kwargs.get("extra"), suggestion
        )
        self.logger.log(level, formatted, *args, exc_info=False)

    def info(self, msg, *args, **kwargs):
        self._log(logging.INFO, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._log(logging.DEBUG, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        exc_info = kwargs.pop("exc_info", None) or sys.exc_info()
        self._log(logging.ERROR, msg, *args, exc_info=exc_info, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log(logging.WARNING, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._log(logging.CRITICAL, msg, *args, **kwargs)

    def timeit(self, func):
        """Decorator that profiles nested calls inside a function."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with SmartProfiler() as profiler:
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time

            self.info(f"Function {func.__name__} executed in {duration:.6f} seconds")

            for fn, t in profiler.timings.items():
                self.debug(f"   └── {fn} took {t:.6f} seconds")

            return result

        return wrapper
