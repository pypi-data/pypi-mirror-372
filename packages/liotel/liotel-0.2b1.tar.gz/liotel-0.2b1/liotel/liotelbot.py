import requests
import time

version = "0.2"
API_BASE = "https://api.telegram.org/bot"

class LiotelBot:
    def __init__(self):
        self.token = None
        self._slots = {}
        self._offset = 0
        self._stop = False

    def _ensure_slot(self, idx: int):
        if idx not in self._slots:
            self._slots[idx] = {"cmd": None, "reply": None}

    def _register_cmd(self, idx: int, cmd: str | None = None, reply: str | None = None):
        self._ensure_slot(idx)
        if cmd is not None:
            self._slots[idx]["cmd"] = self._normalize_cmd(cmd)
        if reply is not None:
            self._slots[idx]["reply"] = reply

    def _normalize_cmd(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        t = text.strip()
        if t.startswith("/"):
            t = t[1:]
        return t

    def _api(self, method: str, params: dict | None = None):
        url = f"{API_BASE}{self.token}/{method}"
        return requests.get(url, params=params or {}, timeout=35)

    def _send_message(self, chat_id: int, text: str):
        try:
            self._api("sendMessage", {"chat_id": chat_id, "text": text})
        except Exception:
            pass

    def add_command(self, cmd: str):
        self._register_cmd(1, cmd=cmd)

    def reply_command(self, reply: str):
        self._register_cmd(1, reply=reply)

    def __getattr__(self, name: str):
        if name.startswith("add_command"):
            try:
                idx = int(name.replace("add_command", ""))
            except ValueError:
                raise AttributeError(name)

            def wrapper(cmd: str):
                self._register_cmd(idx, cmd=cmd)
            return wrapper

        if name.startswith("reply_command"):
            try:
                idx = int(name.replace("reply_command", ""))
            except ValueError:
                raise AttributeError(name)

            def wrapper(reply: str):
                self._register_cmd(idx, reply=reply)
            return wrapper

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def helps(self) -> str:
        return (
            "LiotelBot v" + version + "\n"
            "استفاده‌ی سریع:\n"
            "  from liotel import liotelbot\n"
            "  liotelbot.token = 'YOUR_TOKEN'\n"
            "  liotelbot.add_command('start')\n"
            "  liotelbot.reply_command('ربات فعال شد!')\n"
            "  liotelbot.add_command2('hello')\n"
            "  liotelbot.reply_command2('سلام!')\n"
            "  liotelbot.run_bot()\n\n"
            "نکات:\n"
            "  - دستورها بدون اسلش ذخیره می‌شوند.\n"
            "  - می‌توانید add_command3 و reply_command3 و ... استفاده کنید.\n"
        )

    def run_bot(self, poll_timeout: int = 20, verbose: bool = False) -> bool:
        if not self.token or not isinstance(self.token, str) or not self.token.strip():
            print(f"[Liotel v{version}] ❌ Bot failed to start: token not set")
            return False

        try:
            r = self._api("getMe")
            ok = r.ok and r.json().get("ok", False)
            if not ok:
                print(f"[Liotel v{version}] ❌ Invalid token or API blocked")
                return False
        except requests.exceptions.RequestException:
            pass

        if verbose:
            print(f"[Liotel v{version}] Starting ...")
        else:
            print(f"[Liotel v{version}] ✅ Bot started successfully")

        backoff = 1
        self._stop = False
        self._offset = 0

        try:
            while not self._stop:
                try:
                    resp = self._api("getUpdates", {
                        "offset": self._offset + 1,
                        "timeout": poll_timeout
                    })
                    if resp.status_code == 401:
                        print(f"[Liotel v{version}] ❌ Invalid token (401)")
                        return False

                    data = resp.json()
                    if not data.get("ok", False):
                        time.sleep(min(backoff, 5))
                        backoff = min(backoff * 2, 30)
                        continue

                    backoff = 1

                    for upd in data.get("result", []):
                        self._offset = upd.get("update_id", self._offset)
                        msg = upd.get("message") or {}
                        text = self._normalize_cmd(msg.get("text", ""))
                        chat = msg.get("chat") or {}
                        chat_id = chat.get("id")

                        if not text or chat_id is None:
                            continue

                        for slot in self._slots.values():
                            cmd = slot.get("cmd")
                            reply = slot.get("reply")
                            if cmd and reply and text == cmd:
                                self._send_message(chat_id, reply)
                                break

                except requests.exceptions.RequestException:
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 30)
                except Exception:
                    time.sleep(1)
        except KeyboardInterrupt:
            if verbose:
                print(f"[Liotel v{version}] Stopping ...")
        finally:
            if verbose:
                print(f"[Liotel v{version}] Stopped")

        return True

    def stop(self):
        self._stop = True