#!/usr/bin/env python3
"""장기 토큰(60일)을 새로 받아 표준 출력으로 낸다. 워크플로가 GitHub 비밀값 IG_TOKEN을 바꾼다."""
import json, os, sys, urllib.parse, urllib.request
q = urllib.parse.urlencode({"grant_type": "ig_refresh_token", "access_token": os.environ["IG_TOKEN"]})
with urllib.request.urlopen("https://graph.instagram.com/refresh_access_token?" + q, timeout=60) as r:
    d = json.load(r)
print(f"새 토큰 유효 기간 {int(d['expires_in'])//86400}일", file=sys.stderr)
print(d["access_token"])
