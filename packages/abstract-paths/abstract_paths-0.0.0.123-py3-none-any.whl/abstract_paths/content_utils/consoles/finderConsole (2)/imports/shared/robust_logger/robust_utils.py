import  threading, traceback, logging, os, sys
from logging.handlers import RotatingFileHandler
from PyQt6.QtCore import QObject, QTimer,  pyqtSignal
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import qInstallMessageHandler, QtMsgType
LOG_DIR = os.path.join(os.path.expanduser("~"), ".cache", "abstract_finder")
LOG_FILE = os.path.join(LOG_DIR, "finder.log")
os.makedirs(LOG_DIR, exist_ok=True)
def get_log_file_path():
    return LOG_FILE

class QtLogEmitter(QObject):
    new_log = pyqtSignal(str)

class QtLogHandler(logging.Handler):
    def __init__(self, emitter: QtLogEmitter):
        super().__init__()
        self.emitter = emitter
    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
        except Exception:
            msg = record.getMessage()
        self.emitter.new_log.emit(msg + "\n")
# ---- singletons ----
_emitter: QtLogEmitter | None = None
_handler: QtLogHandler | None = None
class CompactFormatter(logging.Formatter):
    def format(self, record):
        return f"{self.formatTime(record)} [{record.levelname}] {record.getMessage()}"

def get_log_emitter() -> QtLogEmitter:
    global _emitter
    if _emitter is None:
        _emitter = QtLogEmitter()
    return _emitter

def ensure_qt_log_handler_attached() -> QtLogHandler:
    """Attach one QtLogHandler to the root logger (idempotent)."""
    global _handler
    if _handler is None:
        _handler = QtLogHandler(get_log_emitter())
        _handler.setLevel(logging.DEBUG)
        _handler.setFormatter(CompactFormatter("%(asctime)s [%(levelname)s] %(message)s"))
        logging.getLogger().addHandler(_handler)
    return _handler
def set_self_log(self):
    self.log = QTextEdit()
    self.log.setReadOnly(True)
    self.log.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # File: rotating, safe in long sessions
    f = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    f.setLevel(logging.DEBUG)
    f.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
    ))
    logger.addHandler(f)

    # Console (stderr) for dev runs
    c = logging.StreamHandler(sys.stderr)
    c.setLevel(logging.INFO)
    c.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(c)

setup_logging()

# ---- crash handlers: keep app alive, log, and surface in GUI ----
def _format_exc(exctype, value, tb):
    return "".join(traceback.format_exception(exctype, value, tb))

def excepthook(exctype, value, tb):
    msg = _format_exc(exctype, value, tb)
    logging.critical("UNCAUGHT EXCEPTION:\n%s", msg)
    # Don't kill the app; just warn. You can emit to a Qt signal if desired.
    # (Qt will keep running.)

sys.excepthook = excepthook

def threading_excepthook(args):
    # Python 3.8+: threading.excepthook
    msg = _format_exc(args.exc_type, args.exc_value, args.exc_traceback)
    logging.critical("THREAD EXCEPTION:\n%s", msg)

setattr(threading, "excepthook", threading_excepthook)



def qt_message_handler(mode, ctx, message):
    level = {
        QtMsgType.QtDebugMsg: logging.DEBUG,
        QtMsgType.QtInfoMsg: logging.INFO,
        QtMsgType.QtWarningMsg: logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,
        QtMsgType.QtFatalMsg: logging.CRITICAL,
    }.get(mode, logging.INFO)
    logging.log(level, "Qt: %s (%s:%d)", message, ctx.file, ctx.line)

qInstallMessageHandler(qt_message_handler)




def attach_textedit_to_logs(textedit: QTextEdit, tail_file: str | None = None):
    """
    - Routes live Python/Qt logs to the given QTextEdit.
    - Optionally tails a file (e.g., the rotating log) to show external lines too.
    """
    ensure_qt_log_handler_attached()  # idempotent
    emitter = get_log_emitter()
    emitter.new_log.connect(textedit.append)

    if tail_file:
        # simple non-blocking tail
        textedit._tail_pos = 0
        timer = QTimer(textedit)
        timer.setInterval(500)
        def _poll():
            try:
                with io.open(tail_file, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(getattr(textedit, "_tail_pos", 0))
                    chunk = f.read()
                    textedit._tail_pos = f.tell()
                if chunk:
                    textedit.moveCursor(textedit.textCursor().MoveOperation.End)
                    textedit.insertPlainText(chunk)
            except FileNotFoundError:
                pass
        timer.timeout.connect(_poll)
        timer.start()
        # keep a ref
        textedit._tail_timer = timer
