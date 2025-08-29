import hashlib
import hmac

from fastapi.requests import Request


_bot_token = None


def check_telegram_hash(params: Request, _token: str | None = None) -> None:
	bot_token = _token or _bot_token
	if bot_token is None:
		raise ValueError("bot_token is None, nothing to encode with")
	expected_hash = params.query_params.get("hash")
	query_dict = dict(params.query_params)
	query_dict.pop("hash", None)
	sorted_params = sorted(f"{x}={y}" for x, y in query_dict.items())
	data_check_bytes = "\n".join(sorted_params).encode()
	computed_hash = hmac.new(
		hashlib.sha256(bot_token.encode()).digest(),
		data_check_bytes,
		"sha256",
	)
	if hmac.compare_digest(computed_hash.hexdigest(), expected_hash):
		return
	raise AssertionError("invalid hash")
