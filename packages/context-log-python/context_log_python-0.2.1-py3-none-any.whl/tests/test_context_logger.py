import unittest
import logging
import sys
import time
import json
from unittest.mock import MagicMock, patch
from context_logger import ContextLogger, SmartProfiler, ContextFilter

class TestContextLogger(unittest.TestCase):
    def setUp(self):
        patcher = patch('context_logger.logger.generator', MagicMock())
        self.mock_generator = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_generator.return_value = [{'generated_text': 'Mock suggestion'}]

        self.mock_logger = logging.getLogger("test_logger")
        self.mock_logger.handlers = []
        self.mock_logger.filters = []
        self.mock_logger.setLevel(logging.DEBUG)
        self.log_output = []
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.emit = lambda record: self.log_output.append(record.getMessage())
        self.mock_logger.addHandler(handler)

    def test_init_adds_context_filter(self):
        cl = ContextLogger(self.mock_logger)
        self.assertTrue(any(isinstance(f, ContextFilter) for f in self.mock_logger.filters))

    def test_info_logging(self):
        cl = ContextLogger(self.mock_logger)
        cl.info("Test info message")
        
        self.assertTrue(any("Test info message" in msg for msg in self.log_output))

    def test_debug_logging(self):
        cl = ContextLogger(self.mock_logger)
        cl.debug("Debug message")
        
        self.assertTrue(any("Debug message" in msg for msg in self.log_output))

    def test_warning_logging(self):
        cl = ContextLogger(self.mock_logger)
        cl.warning("Warning message")
        
        self.assertTrue(any("Warning message" in msg for msg in self.log_output))

    def test_critical_logging(self):
        cl = ContextLogger(self.mock_logger)
        cl.critical("Critical message")
        
        self.assertTrue(any("Critical message" in msg for msg in self.log_output))

    def test_error_logging_with_exception(self):
        cl = ContextLogger(self.mock_logger)
        
        try:
            raise ValueError("Test error")
        except Exception:
            cl.error("Error occurred")
        
        self.assertTrue(any("Error occurred" in msg for msg in self.log_output))
        self.assertTrue(any("Traceback:" in msg for msg in self.log_output))
        self.assertTrue(any("Suggestion:" in msg for msg in self.log_output))

    def test_error_logging_without_exception(self):
        cl = ContextLogger(self.mock_logger)
        cl.error("Error without exc_info")
        
        self.assertTrue(any("Error without exc_info" in msg for msg in self.log_output))

    def test_format_message_json_mode(self):
        cl = ContextLogger(self.mock_logger, json_mode=True)
        record = self.mock_logger.makeRecord(
            self.mock_logger.name, logging.INFO, fn="", lno=0, msg="", args=(), exc_info=None
        )
        msg = cl._format_message(logging.INFO, "json test", record, extra_context={"foo": "bar"}, suggestion="Try again")
        data = json.loads(msg)
        
        self.assertEqual(data["message"], "json test")
        self.assertEqual(data["extra"]["foo"], "bar")
        self.assertEqual(data["suggestion"], "Try again")

    def test_format_message_text_mode(self):
        cl = ContextLogger(self.mock_logger, json_mode=False)
        record = self.mock_logger.makeRecord(
            self.mock_logger.name, logging.INFO, fn="", lno=0, msg="", args=(), exc_info=None
        )
        msg = cl._format_message(logging.INFO, "text test", record, extra_context={"foo": "bar"}, suggestion="Try again")
        
        self.assertIn("text test", msg)
        self.assertIn("Suggestion: Try again", msg)

    def test_timeit_decorator(self):
        cl = ContextLogger(self.mock_logger)
        @cl.timeit
        def sample_func(x):
            time.sleep(0.01)
            return x * 2
        result = sample_func(5)
        self.assertEqual(result, 10)
        self.assertTrue(any("executed in" in msg for msg in self.log_output))

class TestSmartProfiler(unittest.TestCase):
    def test_profiler_timings(self):
        profiler = SmartProfiler()

        def dummy():
            sum(i * i for i in range(1000))

        with profiler:
            dummy()
        self.assertTrue(any(t > 0 for t in profiler.timings.values()), profiler.timings)

class TestContextFilter(unittest.TestCase):
    def test_filter_injects_context(self):
        logger = logging.getLogger("context_test")
        record = logger.makeRecord(
            logger.name, logging.INFO, fn="foo.py", lno=10, msg="", args=(), exc_info=None
        )
        cf = ContextFilter()
        cf.filter(record)
        
        self.assertTrue(hasattr(record, "context"))
        self.assertTrue(isinstance(record.context, str))

if __name__ == "__main__":
    unittest.main()