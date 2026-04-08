"""Generate deterministic merge conflict scenarios for each difficulty level."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ConflictScenario:
    """A single merge conflict scenario."""

    filename: str
    conflicted_content: str
    ground_truth: str
    branch_info: str
    conflict_count: int
    key_lines: List[str] = field(default_factory=list)
    reject_lines: List[str] = field(default_factory=list)


@dataclass
class Task:
    """A task consisting of one or more conflict scenarios."""

    task_id: str
    scenarios: List[ConflictScenario]
    description: str


# ──────────────────────────────────────────────────────────
#  EASY TASKS: Single conflict — both sides add new things,
#  agent must merge ALL additions (not just pick one side)
# ──────────────────────────────────────────────────────────

EASY_SCENARIOS = [
    ConflictScenario(
        filename="app_config.py",
        conflicted_content="""\
# Application Configuration
APP_NAME = "MyApp"
VERSION = "1.0.0"

<<<<<<< HEAD
# Cache settings
CACHE_TTL = 300
CACHE_MAX_SIZE = 1000
CACHE_BACKEND = "redis"
=======
# Session settings
SESSION_TIMEOUT = 1800
SESSION_COOKIE_NAME = "app_session"
SESSION_SECURE = True
>>>>>>> feature/session-config

DEBUG = False
""",
        ground_truth="""\
# Application Configuration
APP_NAME = "MyApp"
VERSION = "1.0.0"

# Cache settings
CACHE_TTL = 300
CACHE_MAX_SIZE = 1000
CACHE_BACKEND = "redis"

# Session settings
SESSION_TIMEOUT = 1800
SESSION_COOKIE_NAME = "app_session"
SESSION_SECURE = True

DEBUG = False
""",
        branch_info="HEAD branch added cache configuration (CACHE_TTL, CACHE_MAX_SIZE, CACHE_BACKEND). "
        "feature/session-config branch added session configuration (SESSION_TIMEOUT, SESSION_COOKIE_NAME, SESSION_SECURE). "
        "These are independent configuration sections.",
        conflict_count=1,
        key_lines=[
            "CACHE_TTL = 300",
            "CACHE_MAX_SIZE = 1000",
            "CACHE_BACKEND",
            "SESSION_TIMEOUT = 1800",
            "SESSION_COOKIE_NAME",
            "SESSION_SECURE = True",
        ],
        reject_lines=[],
    ),
    ConflictScenario(
        filename="validators.py",
        conflicted_content="""\
import re

<<<<<<< HEAD
def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def validate_username(username: str) -> bool:
    return len(username) >= 3 and username.isalnum()
=======
def validate_phone(phone: str) -> bool:
    digits = re.sub(r"[\s\-\(\)]", "", phone)
    return digits.isdigit() and len(digits) >= 10

def validate_postal_code(code: str) -> bool:
    return bool(re.match(r"^\d{5}(-\d{4})?$", code))
>>>>>>> feature/address-validators

def validate_url(url: str) -> bool:
    return url.startswith(("http://", "https://"))
""",
        ground_truth="""\
import re

def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def validate_username(username: str) -> bool:
    return len(username) >= 3 and username.isalnum()

def validate_phone(phone: str) -> bool:
    digits = re.sub(r"[\s\-\(\)]", "", phone)
    return digits.isdigit() and len(digits) >= 10

def validate_postal_code(code: str) -> bool:
    return bool(re.match(r"^\d{5}(-\d{4})?$", code))

def validate_url(url: str) -> bool:
    return url.startswith(("http://", "https://"))
""",
        branch_info="HEAD branch added validate_email() and validate_username() functions. "
        "feature/address-validators branch added validate_phone() and validate_postal_code() functions. "
        "Both branches extended the validators module independently.",
        conflict_count=1,
        key_lines=[
            "def validate_email(",
            "def validate_username(",
            "def validate_phone(",
            "def validate_postal_code(",
        ],
        reject_lines=[],
    ),
    ConflictScenario(
        filename="string_utils.py",
        conflicted_content="""\
<<<<<<< HEAD
def slugify(text: str) -> str:
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)

def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def count_words(text: str) -> int:
    return len(text.split())
=======
def camel_to_snake(name: str) -> str:
    import re
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

def snake_to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])

def pad_string(text: str, width: int, char: str = " ") -> str:
    return text.center(width, char)
>>>>>>> feature/naming-utils
""",
        ground_truth="""\
def slugify(text: str) -> str:
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)

def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def count_words(text: str) -> int:
    return len(text.split())

def camel_to_snake(name: str) -> str:
    import re
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

def snake_to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])

def pad_string(text: str, width: int, char: str = " ") -> str:
    return text.center(width, char)
""",
        branch_info="HEAD branch added slugify(), truncate(), and count_words() utility functions. "
        "feature/naming-utils branch added camel_to_snake(), snake_to_camel(), and pad_string() utility functions.",
        conflict_count=1,
        key_lines=[
            "def slugify(",
            "def truncate(",
            "def count_words(",
            "def camel_to_snake(",
            "def snake_to_camel(",
            "def pad_string(",
        ],
        reject_lines=[],
    ),
]

# ──────────────────────────────────────────────────────────
#  MEDIUM TASKS: Multiple conflicts, semantic merging needed
# ──────────────────────────────────────────────────────────

MEDIUM_SCENARIOS = [
    ConflictScenario(
        filename="user_service.py",
        conflicted_content="""\
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
<<<<<<< HEAD
    name: str
    email: str
    role: str = "viewer"
=======
    name: str
    email: str
    age: int = 0
>>>>>>> feature/user-profile

<<<<<<< HEAD
def create_user(name: str, email: str, role: str = "viewer") -> User:
    if not email or "@" not in email:
        raise ValueError("Invalid email")
    return User(name=name, email=email, role=role)
=======
def create_user(name: str, email: str, age: int = 0) -> User:
    if not name:
        raise ValueError("Name is required")
    return User(name=name, email=email, age=age)
>>>>>>> feature/user-profile

def get_user_display(user: User) -> str:
    return f"{user.name} <{user.email}>"
""",
        ground_truth="""\
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    name: str
    email: str
    role: str = "viewer"
    age: int = 0

def create_user(name: str, email: str, role: str = "viewer", age: int = 0) -> User:
    if not name:
        raise ValueError("Name is required")
    if not email or "@" not in email:
        raise ValueError("Invalid email")
    return User(name=name, email=email, role=role, age=age)

def get_user_display(user: User) -> str:
    return f"{user.name} <{user.email}>"
""",
        branch_info="HEAD branch: User dataclass gained a role field; create_user() validates email format. "
        "feature/user-profile branch: User dataclass gained an age field; create_user() validates that name is non-empty.",
        conflict_count=2,
        key_lines=[
            'role: str = "viewer"',
            "age: int = 0",
            'raise ValueError("Name is required")',
            'raise ValueError("Invalid email")',
            "name: str, email: str, role: str",
            "age: int = 0) -> User",
            "return User(name=name, email=email, role=role, age=age)",
        ],
        reject_lines=[
            "return User(name=name, email=email, role=role)",
            "return User(name=name, email=email, age=age)",
        ],
    ),
    ConflictScenario(
        filename="calculator.py",
        conflicted_content="""\
import math

class Calculator:
    def __init__(self):
        self.history = []

<<<<<<< HEAD
    def add(self, a: float, b: float) -> float:
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a: float, b: float) -> float:
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
=======
    def add(self, a: float, b: float) -> float:
        result = a + b
        return round(result, 2)

    def multiply(self, a: float, b: float) -> float:
        result = a * b
        return round(result, 2)
>>>>>>> feature/precision

<<<<<<< HEAD
    def get_history(self) -> list:
        return self.history.copy()
=======
    def clear(self) -> None:
        self.history = []
>>>>>>> feature/precision

    def square_root(self, x: float) -> float:
        if x < 0:
            raise ValueError("Cannot take square root of negative number")
        return math.sqrt(x)
""",
        ground_truth="""\
import math

class Calculator:
    def __init__(self):
        self.history = []

    def add(self, a: float, b: float) -> float:
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return round(result, 2)

    def subtract(self, a: float, b: float) -> float:
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result

    def multiply(self, a: float, b: float) -> float:
        result = a * b
        return round(result, 2)

    def get_history(self) -> list:
        return self.history.copy()

    def clear(self) -> None:
        self.history = []

    def square_root(self, x: float) -> float:
        if x < 0:
            raise ValueError("Cannot take square root of negative number")
        return math.sqrt(x)
""",
        branch_info="HEAD branch: add() and subtract() now append to self.history; get_history() method added. "
        "feature/precision branch: add() now returns round(result, 2); multiply() and clear() methods added.",
        conflict_count=2,
        key_lines=[
            "self.history.append(",
            "return round(result, 2)",
            "def multiply(",
            "def get_history(",
            "def clear(",
        ],
        reject_lines=[],
    ),
]

# ──────────────────────────────────────────────────────────
#  HARD TASKS: Multi-file conflicts with cross-file deps
# ──────────────────────────────────────────────────────────

HARD_SCENARIOS = [
    ConflictScenario(
        filename="auth_service.py",
        conflicted_content="""\
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict

<<<<<<< HEAD
TOKEN_EXPIRY_HOURS = 24
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 30

class AuthService:
    def __init__(self):
        self._users: Dict[str, dict] = {}
        self._tokens: Dict[str, dict] = {}
        self._failed_attempts: Dict[str, int] = {}

    def register(self, username: str, password: str, email: str) -> bool:
        if username in self._users:
            return False
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        self._users[username] = {
            "password_hash": hashed,
            "salt": salt,
            "email": email,
            "created_at": datetime.utcnow().isoformat(),
        }
        return True

    def login(self, username: str, password: str) -> Optional[str]:
        if username not in self._users:
            return None
        if self._failed_attempts.get(username, 0) >= MAX_LOGIN_ATTEMPTS:
            return None
        user = self._users[username]
        hashed = hashlib.sha256(f"{user['salt']}{password}".encode()).hexdigest()
        if hashed != user["password_hash"]:
            self._failed_attempts[username] = self._failed_attempts.get(username, 0) + 1
            return None
        self._failed_attempts[username] = 0
        token = secrets.token_urlsafe(32)
        self._tokens[token] = {
            "username": username,
            "expires": (datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)).isoformat(),
        }
        return token

    def validate_token(self, token: str) -> Optional[str]:
        if token not in self._tokens:
            return None
        data = self._tokens[token]
        if datetime.fromisoformat(data["expires"]) < datetime.utcnow():
            del self._tokens[token]
            return None
        return data["username"]
=======
TOKEN_EXPIRY_HOURS = 8
REQUIRE_2FA = True

class AuthService:
    def __init__(self):
        self._users: Dict[str, dict] = {}
        self._tokens: Dict[str, dict] = {}
        self._totp_secrets: Dict[str, str] = {}

    def register(self, username: str, password: str, role: str = "user") -> bool:
        if username in self._users:
            return False
        if len(password) < 12:
            raise ValueError("Password must be at least 12 characters")
        salt = secrets.token_hex(32)
        hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        self._users[username] = {
            "password_hash": hashed,
            "salt": salt,
            "role": role,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
        }
        if REQUIRE_2FA:
            self._totp_secrets[username] = secrets.token_hex(20)
        return True

    def login(self, username: str, password: str, totp_code: Optional[str] = None) -> Optional[str]:
        if username not in self._users:
            return None
        user = self._users[username]
        hashed = hashlib.sha256(f"{user['salt']}{password}".encode()).hexdigest()
        if hashed != user["password_hash"]:
            return None
        if REQUIRE_2FA and username in self._totp_secrets:
            if totp_code is None:
                return None
        user["last_login"] = datetime.utcnow().isoformat()
        token = secrets.token_urlsafe(32)
        self._tokens[token] = {
            "username": username,
            "role": user["role"],
            "expires": (datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)).isoformat(),
        }
        return token

    def validate_token(self, token: str) -> Optional[dict]:
        if token not in self._tokens:
            return None
        data = self._tokens[token]
        if datetime.fromisoformat(data["expires"]) < datetime.utcnow():
            del self._tokens[token]
            return None
        return {"username": data["username"], "role": data["role"]}
>>>>>>> feature/security-hardening
""",
        ground_truth="""\
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict

TOKEN_EXPIRY_HOURS = 8
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 30
REQUIRE_2FA = True

class AuthService:
    def __init__(self):
        self._users: Dict[str, dict] = {}
        self._tokens: Dict[str, dict] = {}
        self._failed_attempts: Dict[str, int] = {}
        self._totp_secrets: Dict[str, str] = {}

    def register(self, username: str, password: str, email: str, role: str = "user") -> bool:
        if username in self._users:
            return False
        if len(password) < 12:
            raise ValueError("Password must be at least 12 characters")
        salt = secrets.token_hex(32)
        hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        self._users[username] = {
            "password_hash": hashed,
            "salt": salt,
            "email": email,
            "role": role,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
        }
        if REQUIRE_2FA:
            self._totp_secrets[username] = secrets.token_hex(20)
        return True

    def login(self, username: str, password: str, totp_code: Optional[str] = None) -> Optional[str]:
        if username not in self._users:
            return None
        if self._failed_attempts.get(username, 0) >= MAX_LOGIN_ATTEMPTS:
            return None
        user = self._users[username]
        hashed = hashlib.sha256(f"{user['salt']}{password}".encode()).hexdigest()
        if hashed != user["password_hash"]:
            self._failed_attempts[username] = self._failed_attempts.get(username, 0) + 1
            return None
        if REQUIRE_2FA and username in self._totp_secrets:
            if totp_code is None:
                return None
        self._failed_attempts[username] = 0
        user["last_login"] = datetime.utcnow().isoformat()
        token = secrets.token_urlsafe(32)
        self._tokens[token] = {
            "username": username,
            "role": user["role"],
            "expires": (datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)).isoformat(),
        }
        return token

    def validate_token(self, token: str) -> Optional[dict]:
        if token not in self._tokens:
            return None
        data = self._tokens[token]
        if datetime.fromisoformat(data["expires"]) < datetime.utcnow():
            del self._tokens[token]
            return None
        return {"username": data["username"], "role": data["role"]}
""",
        branch_info="HEAD (main) added brute-force protection (login attempt tracking, "
        "lockout after MAX_LOGIN_ATTEMPTS, failed_attempts counter) and email field in register(). "
        "feature/security-hardening added 2FA support, role-based access, password length validation, "
        "last_login tracking, shorter token expiry (8h), stronger salt (32 bytes), and role in tokens. "
        "Both branches modified register(), login(), and validate_token().",
        conflict_count=1,
        key_lines=[
            "TOKEN_EXPIRY_HOURS = 8",
            "MAX_LOGIN_ATTEMPTS = 5",
            "LOCKOUT_MINUTES = 30",
            "REQUIRE_2FA = True",
            "self._failed_attempts: Dict[str, int]",
            "self._totp_secrets: Dict[str, str]",
            "len(password) < 12",
            'secrets.token_hex(32)',
            '"last_login": None',
            "user[\"last_login\"] = datetime.utcnow().isoformat()",
            "self._failed_attempts[username] = 0",
            'Optional[dict]',
        ],
        reject_lines=[
            "TOKEN_EXPIRY_HOURS = 24",
            "secrets.token_hex(16)",
        ],
    ),
    ConflictScenario(
        filename="api_routes.py",
        conflicted_content="""\
from typing import Optional
from datetime import datetime

<<<<<<< HEAD
from .auth_service import AuthService

auth = AuthService()

def handle_register(data: dict) -> dict:
    username = data.get("username", "")
    password = data.get("password", "")
    email = data.get("email", "")
    if not username or not password or not email:
        return {"error": "Missing required fields", "status": 400}
    try:
        success = auth.register(username, password, email)
    except Exception as e:
        return {"error": str(e), "status": 400}
    if not success:
        return {"error": "Username already exists", "status": 409}
    return {"message": "User registered", "status": 201}

def handle_login(data: dict) -> dict:
    username = data.get("username", "")
    password = data.get("password", "")
    if not username or not password:
        return {"error": "Missing credentials", "status": 400}
    token = auth.login(username, password)
    if token is None:
        return {"error": "Invalid credentials", "status": 401}
    return {"token": token, "status": 200}

def handle_protected(token: str) -> dict:
    username = auth.validate_token(token)
    if username is None:
        return {"error": "Unauthorized", "status": 401}
    return {"message": f"Hello {username}", "status": 200}
=======
from .auth_service import AuthService

auth = AuthService()

def handle_register(data: dict) -> dict:
    username = data.get("username", "")
    password = data.get("password", "")
    role = data.get("role", "user")
    if not username or not password:
        return {"error": "Missing required fields", "status": 400}
    if role not in ("user", "admin", "moderator"):
        return {"error": "Invalid role", "status": 400}
    try:
        success = auth.register(username, password, role)
    except ValueError as e:
        return {"error": str(e), "status": 400}
    if not success:
        return {"error": "Username already exists", "status": 409}
    return {"message": "User registered", "status": 201}

def handle_login(data: dict) -> dict:
    username = data.get("username", "")
    password = data.get("password", "")
    totp_code = data.get("totp_code")
    if not username or not password:
        return {"error": "Missing credentials", "status": 400}
    token = auth.login(username, password, totp_code)
    if token is None:
        return {"error": "Invalid credentials or missing 2FA", "status": 401}
    return {"token": token, "status": 200}

def handle_protected(token: str, required_role: Optional[str] = None) -> dict:
    auth_data = auth.validate_token(token)
    if auth_data is None:
        return {"error": "Unauthorized", "status": 401}
    if required_role and auth_data["role"] != required_role:
        return {"error": "Forbidden", "status": 403}
    return {"message": f"Hello {auth_data['username']}", "role": auth_data["role"], "status": 200}
>>>>>>> feature/security-hardening
""",
        ground_truth="""\
from typing import Optional
from datetime import datetime

from .auth_service import AuthService

auth = AuthService()

def handle_register(data: dict) -> dict:
    username = data.get("username", "")
    password = data.get("password", "")
    email = data.get("email", "")
    role = data.get("role", "user")
    if not username or not password or not email:
        return {"error": "Missing required fields", "status": 400}
    if role not in ("user", "admin", "moderator"):
        return {"error": "Invalid role", "status": 400}
    try:
        success = auth.register(username, password, email, role)
    except ValueError as e:
        return {"error": str(e), "status": 400}
    if not success:
        return {"error": "Username already exists", "status": 409}
    return {"message": "User registered", "status": 201}

def handle_login(data: dict) -> dict:
    username = data.get("username", "")
    password = data.get("password", "")
    totp_code = data.get("totp_code")
    if not username or not password:
        return {"error": "Missing credentials", "status": 400}
    token = auth.login(username, password, totp_code)
    if token is None:
        return {"error": "Invalid credentials or missing 2FA", "status": 401}
    return {"token": token, "status": 200}

def handle_protected(token: str, required_role: Optional[str] = None) -> dict:
    auth_data = auth.validate_token(token)
    if auth_data is None:
        return {"error": "Unauthorized", "status": 401}
    if required_role and auth_data["role"] != required_role:
        return {"error": "Forbidden", "status": 403}
    return {"message": f"Hello {auth_data['username']}", "role": auth_data["role"], "status": 200}
""",
        branch_info="HEAD (main) has register(username, password, email) with email validation "
        "and login(username, password). feature/security-hardening has register(username, password, role) "
        "with role validation, login with totp_code, and role-based access in handle_protected. "
        "Both branches modified register, login, and handle_protected.",
        conflict_count=1,
        key_lines=[
            'email = data.get("email"',
            'role = data.get("role"',
            "totp_code = data.get(",
            "auth.register(username, password, email, role)",
            'if not username or not password or not email',
            'role not in ("user", "admin", "moderator")',
            '"Invalid credentials or missing 2FA"',
            "required_role",
            'auth_data["role"]',
        ],
        reject_lines=[
            "auth.register(username, password, role)",
            "auth.register(username, password, email)",
            '"Invalid credentials"',
        ],
    ),
]

# ──────────────────────────────────────────────────────────
#  EXPERT TASKS: Ambiguous merge requiring judgment
# ──────────────────────────────────────────────────────────

EXPERT_SCENARIOS = [
    ConflictScenario(
        filename="data_processor.py",
        conflicted_content="""\
import logging
from typing import List, Dict, Any, Optional
<<<<<<< HEAD
from datetime import datetime

logger = logging.getLogger(__name__)
=======
from functools import lru_cache
>>>>>>> feature/optimized-pipeline

class DataProcessor:
<<<<<<< HEAD
    def __init__(self, source: str):
        self.source = source
        self.errors: List[str] = []

    def validate(self, data: dict) -> bool:
        if not data or "id" not in data or "value" not in data:
            self.errors.append("Invalid data")
            return False
        return True

    def process(self, data: dict) -> Optional[dict]:
        if not self.validate(data):
            logger.error(f"Validation failed: {self.errors[-1]}")
            return None
        try:
            return {"id": data["id"], "result": data["value"] * 2, "source": self.source}
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return None
=======
    def __init__(self, source: str, batch_size: int = 100):
        self.source = source
        self.batch_size = batch_size
        self._cache: Dict[str, Any] = {}

    def process(self, data: dict) -> dict:
        key = str(data["id"])
        if key in self._cache:
            return self._cache[key]
        result = {"id": data["id"], "result": data["value"] * 2 + 1, "source": self.source}
        self._cache[key] = result
        return result

    def process_batch(self, items: List[dict]) -> List[dict]:
        return [self.process(item) for item in items]
>>>>>>> feature/optimized-pipeline

<<<<<<< HEAD
    def get_errors(self) -> List[str]:
        return self.errors.copy()
=======
    def clear_cache(self) -> None:
        self._cache.clear()
>>>>>>> feature/optimized-pipeline
""",
        ground_truth="""\
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, source: str, batch_size: int = 100):
        self.source = source
        self.batch_size = batch_size
        self.errors: List[str] = []
        self._cache: Dict[str, Any] = {}

    def validate(self, data: dict) -> bool:
        if not data or "id" not in data or "value" not in data:
            self.errors.append("Invalid data")
            return False
        return True

    def process(self, data: dict) -> Optional[dict]:
        if not self.validate(data):
            logger.error(f"Validation failed: {self.errors[-1]}")
            return None
        key = str(data["id"])
        if key in self._cache:
            return self._cache[key]
        try:
            result = {"id": data["id"], "result": data["value"] * 2 + 1, "source": self.source}
            self._cache[key] = result
            return result
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return None

    def process_batch(self, items: List[dict]) -> List[dict]:
        return [r for r in (self.process(item) for item in items) if r is not None]

    def get_errors(self) -> List[str]:
        return self.errors.copy()

    def clear_cache(self) -> None:
        self._cache.clear()
""",
        branch_info="HEAD (main) added input validation, error handling with logging, and an errors list. "
        "feature/optimized-pipeline added batch processing, result caching, and changed the processing "
        "algorithm. Both branches modified __init__() and process().",
        conflict_count=3,
        key_lines=[
            "def validate(",
            "self._cache",
            'data["value"] * 2 + 1',
            "if not self.validate(data)",
            "def process_batch(",
            "logger.error(",
            "def get_errors(",
            "def clear_cache(",
        ],
        reject_lines=[],
    ),
    ConflictScenario(
        filename="report_generator.py",
        conflicted_content="""\
from typing import List, Dict, Any
from datetime import datetime

class ReportGenerator:
    def __init__(self, title: str):
        self.title = title
        self.data: List[Dict[str, Any]] = []

    def add_record(self, record: Dict[str, Any]) -> None:
        self.data.append(record)

<<<<<<< HEAD
    def filter_by_date(self, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        return [r for r in self.data
                if start <= r.get("date", datetime.min) <= end]

    def generate(self, format: str = "text") -> str:
        lines = [f"=== {self.title} ==="]
        lines.append(f"Records: {len(self.data)}")
        for record in self.data:
            lines.append(f"  {record.get('name', 'N/A')}: {record.get('value', 0)}")
        lines.append(f"Total: {sum(r.get('value', 0) for r in self.data)}")
        return "\\n".join(lines)
=======
    def group_by_category(self, key: str = "category") -> Dict[str, List[Dict[str, Any]]]:
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for record in self.data:
            cat = record.get(key, "uncategorized")
            groups.setdefault(cat, []).append(record)
        return groups

    def generate(self, format: str = "text") -> str:
        if format == "json":
            import json
            return json.dumps({"title": self.title, "data": self.data, "count": len(self.data)})
        lines = [f"=== {self.title} ==="]
        lines.append(f"Records: {len(self.data)}")
        for record in self.data:
            lines.append(f"  [{record.get('category', '?')}] {record.get('name', 'N/A')}: {record.get('value', 0)}")
        return "\\n".join(lines)
>>>>>>> feature/categorization

<<<<<<< HEAD
    def export_csv(self) -> str:
        if not self.data:
            return ""
        headers = sorted(self.data[0].keys())
        lines = [",".join(headers)]
        for record in self.data:
            lines.append(",".join(str(record.get(h, "")) for h in headers))
        return "\\n".join(lines)
=======
    def get_summary(self) -> Dict[str, Any]:
        groups = self.group_by_category()
        return {
            "title": self.title,
            "total_records": len(self.data),
            "categories": {k: len(v) for k, v in groups.items()},
        }
>>>>>>> feature/categorization
""",
        ground_truth="""\
from typing import List, Dict, Any
from datetime import datetime

class ReportGenerator:
    def __init__(self, title: str):
        self.title = title
        self.data: List[Dict[str, Any]] = []

    def add_record(self, record: Dict[str, Any]) -> None:
        self.data.append(record)

    def filter_by_date(self, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        return [r for r in self.data
                if start <= r.get("date", datetime.min) <= end]

    def group_by_category(self, key: str = "category") -> Dict[str, List[Dict[str, Any]]]:
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for record in self.data:
            cat = record.get(key, "uncategorized")
            groups.setdefault(cat, []).append(record)
        return groups

    def generate(self, format: str = "text") -> str:
        if format == "json":
            import json
            return json.dumps({"title": self.title, "data": self.data, "count": len(self.data)})
        lines = [f"=== {self.title} ==="]
        lines.append(f"Records: {len(self.data)}")
        for record in self.data:
            lines.append(f"  [{record.get('category', '?')}] {record.get('name', 'N/A')}: {record.get('value', 0)}")
        lines.append(f"Total: {sum(r.get('value', 0) for r in self.data)}")
        return "\\n".join(lines)

    def export_csv(self) -> str:
        if not self.data:
            return ""
        headers = sorted(self.data[0].keys())
        lines = [",".join(headers)]
        for record in self.data:
            lines.append(",".join(str(record.get(h, "")) for h in headers))
        return "\\n".join(lines)

    def get_summary(self) -> Dict[str, Any]:
        groups = self.group_by_category()
        return {
            "title": self.title,
            "total_records": len(self.data),
            "categories": {k: len(v) for k, v in groups.items()},
        }
""",
        branch_info="HEAD (main) added date filtering, CSV export, and a total line in text reports. "
        "feature/categorization added category grouping, JSON output format, category display in "
        "text reports, and a summary method. Both branches modified generate().",
        conflict_count=2,
        key_lines=[
            "def filter_by_date(",
            "def group_by_category(",
            "def export_csv(",
            "def get_summary(",
            'format == "json"',
            "Total:",
        ],
        reject_lines=[],
    ),
]

# ──────────────────────────────────────────────────────────
#  NIGHTMARE TASKS: Multi-file with cross-file consistency
# ──────────────────────────────────────────────────────────

NIGHTMARE_SCENARIOS = [
    ConflictScenario(
        filename="order_models.py",
        conflicted_content="""\
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
<<<<<<< HEAD
    DELIVERED = "delivered"
    REFUNDED = "refunded"
=======
    DELIVERED = "delivered"
    PROCESSING = "processing"
    CANCELLED = "cancelled"
>>>>>>> feature/order-revamp

<<<<<<< HEAD
@dataclass
class Order:
    order_id: str
    customer: str
    items: List[str]
    total: float
    status: OrderStatus = OrderStatus.PENDING
    discount: float = 0.0

    def final_total(self) -> float:
        return round(self.total * (1 - self.discount), 2)

    def is_refundable(self) -> bool:
        return self.status in (OrderStatus.CONFIRMED, OrderStatus.DELIVERED)
=======
@dataclass
class CustomerOrder:
    order_id: str
    customer: str
    items: List[str]
    total: float
    status: OrderStatus = OrderStatus.PENDING
    tags: List[str] = field(default_factory=list)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags

    def serialize(self) -> dict:
        return {"order_id": self.order_id, "customer": self.customer,
                "items": self.items, "total": self.total,
                "status": self.status.value, "tags": self.tags}
>>>>>>> feature/order-revamp
""",
        ground_truth="""\
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    REFUNDED = "refunded"
    PROCESSING = "processing"
    CANCELLED = "cancelled"

@dataclass
class CustomerOrder:
    order_id: str
    customer: str
    items: List[str]
    total: float
    status: OrderStatus = OrderStatus.PENDING
    discount: float = 0.0
    tags: List[str] = field(default_factory=list)

    def final_total(self) -> float:
        return round(self.total * (1 - self.discount), 2)

    def is_refundable(self) -> bool:
        return self.status in (OrderStatus.CONFIRMED, OrderStatus.DELIVERED)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags

    def serialize(self) -> dict:
        return {"order_id": self.order_id, "customer": self.customer,
                "items": self.items, "total": self.total,
                "status": self.status.value, "tags": self.tags,
                "discount": self.discount}
""",
        branch_info="HEAD (main) added discount field, REFUNDED status, final_total(), and "
        "is_refundable(). feature/order-revamp renamed the main data class, added tags field, "
        "PROCESSING and CANCELLED statuses, has_tag(), and serialize(). Both branches modified "
        "the class definition and added new methods.",
        conflict_count=2,
        key_lines=[
            "class CustomerOrder:",
            "discount: float",
            "tags: List[str]",
            "REFUNDED",
            "PROCESSING",
            "CANCELLED",
            "def final_total(",
            "def has_tag(",
            "def serialize(",
        ],
        reject_lines=["class Order:"],
    ),
    ConflictScenario(
        filename="order_service.py",
        conflicted_content="""\
from typing import List, Optional

<<<<<<< HEAD
from .order_models import Order, OrderStatus

class OrderService:
    def __init__(self):
        self._orders: dict = {}

    def create_order(self, order_id: str, customer: str, items: List[str], total: float) -> Order:
        order = Order(order_id=order_id, customer=customer, items=items, total=total)
        self._orders[order_id] = order
        return order

    def apply_discount(self, order_id: str, discount: float) -> bool:
        order = self._orders.get(order_id)
        if not order:
            return False
        order.discount = discount
        return True

    def refund(self, order_id: str) -> bool:
        order = self._orders.get(order_id)
        if not order or not order.is_refundable():
            return False
        order.status = OrderStatus.REFUNDED
        return True

    def get_order(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)
=======
from .order_models import CustomerOrder, OrderStatus

class OrderService:
    def __init__(self):
        self._orders: dict = {}

    def place_order(self, order_id: str, customer: str, items: List[str], total: float, tags: List[str] = None) -> CustomerOrder:
        order = CustomerOrder(order_id=order_id, customer=customer, items=items, total=total, tags=tags or [])
        self._orders[order_id] = order
        return order

    def add_tags(self, order_id: str, tags: List[str]) -> bool:
        order = self._orders.get(order_id)
        if not order:
            return False
        order.tags.extend(tags)
        return True

    def find_by_tag(self, tag: str) -> List[CustomerOrder]:
        return [o for o in self._orders.values() if o.has_tag(tag)]

    def get_order(self, order_id: str) -> Optional[CustomerOrder]:
        return self._orders.get(order_id)
>>>>>>> feature/order-revamp
""",
        ground_truth="""\
from typing import List, Optional

from .order_models import CustomerOrder, OrderStatus

class OrderService:
    def __init__(self):
        self._orders: dict = {}

    def place_order(self, order_id: str, customer: str, items: List[str], total: float, tags: List[str] = None) -> CustomerOrder:
        order = CustomerOrder(order_id=order_id, customer=customer, items=items, total=total, tags=tags or [])
        self._orders[order_id] = order
        return order

    def apply_discount(self, order_id: str, discount: float) -> bool:
        order = self._orders.get(order_id)
        if not order:
            return False
        order.discount = discount
        return True

    def add_tags(self, order_id: str, tags: List[str]) -> bool:
        order = self._orders.get(order_id)
        if not order:
            return False
        order.tags.extend(tags)
        return True

    def refund(self, order_id: str) -> bool:
        order = self._orders.get(order_id)
        if not order or not order.is_refundable():
            return False
        order.status = OrderStatus.REFUNDED
        return True

    def find_by_tag(self, tag: str) -> List[CustomerOrder]:
        return [o for o in self._orders.values() if o.has_tag(tag)]

    def get_order(self, order_id: str) -> Optional[CustomerOrder]:
        return self._orders.get(order_id)
""",
        branch_info="HEAD (main) has order creation, discount application, and refund methods. "
        "feature/order-revamp renamed the creation method, added tag management and search methods. "
        "Both use different class names matching their version of the models file.",
        conflict_count=1,
        key_lines=[
            "import CustomerOrder",
            "def place_order(",
            "def apply_discount(",
            "def add_tags(",
            "def refund(",
            "def find_by_tag(",
        ],
        reject_lines=["def create_order("],
    ),
    ConflictScenario(
        filename="test_orders.py",
        conflicted_content="""\
<<<<<<< HEAD
from .order_models import Order, OrderStatus
from .order_service import OrderService

def test_create_and_discount():
    svc = OrderService()
    order = svc.create_order("O1", "Alice", ["A"], 100.0)
    assert isinstance(order, Order)
    svc.apply_discount("O1", 0.1)
    assert order.final_total() == 90.0

def test_refund():
    svc = OrderService()
    order = svc.create_order("O2", "Bob", ["B"], 50.0)
    order.status = OrderStatus.CONFIRMED
    assert svc.refund("O2") is True
    assert order.status == OrderStatus.REFUNDED
=======
from .order_models import CustomerOrder, OrderStatus
from .order_service import OrderService

def test_place_with_tags():
    svc = OrderService()
    order = svc.place_order("O1", "Alice", ["A"], 100.0, tags=["vip"])
    assert isinstance(order, CustomerOrder)
    assert order.has_tag("vip")

def test_find_by_tag():
    svc = OrderService()
    svc.place_order("O2", "Bob", ["B"], 50.0, tags=["bulk"])
    svc.place_order("O3", "Charlie", ["C"], 75.0, tags=["bulk"])
    assert len(svc.find_by_tag("bulk")) == 2
>>>>>>> feature/order-revamp
""",
        ground_truth="""\
from .order_models import CustomerOrder, OrderStatus
from .order_service import OrderService

def test_place_with_tags():
    svc = OrderService()
    order = svc.place_order("O1", "Alice", ["A"], 100.0, tags=["vip"])
    assert isinstance(order, CustomerOrder)
    assert order.has_tag("vip")

def test_discount():
    svc = OrderService()
    order = svc.place_order("O2", "Bob", ["B"], 100.0)
    svc.apply_discount("O2", 0.1)
    assert order.final_total() == 90.0

def test_refund():
    svc = OrderService()
    order = svc.place_order("O3", "Charlie", ["C"], 50.0)
    order.status = OrderStatus.CONFIRMED
    assert svc.refund("O3") is True
    assert order.status == OrderStatus.REFUNDED

def test_find_by_tag():
    svc = OrderService()
    svc.place_order("O4", "Diana", ["D"], 50.0, tags=["bulk"])
    svc.place_order("O5", "Eve", ["E"], 75.0, tags=["bulk"])
    assert len(svc.find_by_tag("bulk")) == 2
""",
        branch_info="HEAD (main) tests discount calculation and refund with original class and method names. "
        "feature/order-revamp tests tagging and search with renamed class and methods. All tests "
        "must use consistent naming matching the merged models and service files.",
        conflict_count=1,
        key_lines=[
            "import CustomerOrder",
            "place_order(",
            "apply_discount(",
            "svc.refund(",
            "has_tag(",
            "find_by_tag(",
            "final_total()",
        ],
        reject_lines=["create_order("],
    ),
]

# ──────────────────────────────────────────────────────────
#  TASK REGISTRY
# ──────────────────────────────────────────────────────────

TASKS: Dict[str, Task] = {
    "easy": Task(
        task_id="easy",
        scenarios=EASY_SCENARIOS,
        description="Simple single-conflict resolution. Pick the correct side.",
    ),
    "medium": Task(
        task_id="medium",
        scenarios=MEDIUM_SCENARIOS,
        description="Multiple conflicts requiring semantic merging of both sides.",
    ),
    "hard": Task(
        task_id="hard",
        scenarios=HARD_SCENARIOS,
        description="Multi-file conflicts with cross-file dependencies. Both files must be resolved consistently.",
    ),
    "expert": Task(
        task_id="expert",
        scenarios=EXPERT_SCENARIOS,
        description="Ambiguous merge requiring deep code understanding. Combine overlapping changes from both branches.",
    ),
    "nightmare": Task(
        task_id="nightmare",
        scenarios=NIGHTMARE_SCENARIOS,
        description="Multi-file merge with cross-file naming consistency. Class and method renames must be consistent across all files.",
    ),
}


def get_task(task_id: str) -> Task:
    if task_id not in TASKS:
        raise ValueError(f"Unknown task: {task_id}. Available: {list(TASKS.keys())}")
    return TASKS[task_id]


def get_all_task_ids() -> List[str]:
    return list(TASKS.keys())
