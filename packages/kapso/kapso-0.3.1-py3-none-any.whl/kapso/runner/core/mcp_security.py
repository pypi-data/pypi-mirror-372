import hashlib, ipaddress, json, re, urllib.parse, aiohttp, logging

log = logging.getLogger(__name__)

DANGEROUS_LOCAL = {"localhost", "127.0.0.1", "0.0.0.0"}
HASH_RE         = re.compile(r"^[a-f0-9]{64}$")
SSE_DATA_RE     = re.compile(r"^data:\s*(\{.*\})", re.M)

KNOWN_MANIFESTS: dict[str, str] = {}

def _is_private_host(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private
    except ValueError:
        return host in DANGEROUS_LOCAL


# ────────────────────────────────────────────────────────────────────────────
#  ✓ 1st choice: JSON-RPC describe   (HTTP POST {method:"describe"})
#  ✓ 2nd choice: first   data: {...} on SSE stream
# ────────────────────────────────────────────────────────────────────────────
async def _download_manifest(base_url: str) -> dict | None:
    """
    Return manifest dict or None if the server doesn't expose one.
    """
    parsed = urllib.parse.urlparse(base_url)
    base   = urllib.parse.urlunparse((parsed.scheme, parsed.netloc,
                                      parsed.path.rstrip("/"), "", "", ""))

    # ---------- 1. try JSON-RPC describe  ----------------------------------
    describe_body = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "describe", "params": []
    })
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=5)
        ) as s:
            async with s.post(base, data=describe_body,
                              headers={"Content-Type": "application/json",
                                       "Accept": "application/json"}) as r:
                if r.status == 200:
                    payload = await r.json()
                    if "result" in payload:
                        return payload["result"]
    except Exception as e:
        log.debug(f"describe() failed for {base}: {e!r}")

    # ---------- 2. try one-shot SSE connect -------------------------------
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=5)
        ) as s:
            async with s.get(base, headers={"Accept": "text/event-stream"}) as r:
                if r.headers.get("content-type", "").startswith("text/event-stream"):
                    text = await r.text()
                    match = SSE_DATA_RE.search(text)
                    if match:
                        return json.loads(match.group(1))
    except Exception as e:
        log.debug(f"SSE manifest fetch failed for {base}: {e!r}")

    # ---------- none found -------------------------------------------------
    log.info(f"No MCP manifest available at {base} (describe & SSE failed)")
    return None


async def validate_mcp_entry(cfg: dict) -> dict:
    # 1. forbid local process
    if "command" in cfg or cfg.get("transport") == "stdio":
        raise ValueError("Local/stdio MCP servers are not allowed")

    # 2. forbid private hosts
    if "url" not in cfg:
        raise ValueError("MCP entry missing 'url'")
    host = urllib.parse.urlparse(cfg["url"]).hostname or ""
    if _is_private_host(host):
        raise ValueError("MCP url points to a private/localhost host")

    # 3. optional manifest + light scan
    manifest = None # await _download_manifest(cfg["url"])
    if manifest:                                    # we got one 🎉
        digest = hashlib.sha256(
            json.dumps(manifest, sort_keys=True).encode()
        ).hexdigest()
        if (stored := KNOWN_MANIFESTS.get(cfg["url"])) and stored != digest:
            raise ValueError(
                f"Manifest hash drift for {cfg['url']} "
                f"(expected {stored}, got {digest})"
            )
        KNOWN_MANIFESTS.setdefault(cfg["url"], digest)

        # quick danger scan
        bad = [
            t for t in manifest.get("tools", [])
            if re.search(r"(shell|exec|terminal|fs|system|delete|rm\s)",
                         (t.get("name","") + t.get("description","")), re.I)
        ]
        if bad:
            names = [t["name"] for t in bad]
            raise ValueError(f"MCP server exposes dangerous tools: {names}")

    else:
        log.info(f"Proceeding without manifest verification for {cfg['url']}")

    return cfg
