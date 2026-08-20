#!/usr/bin/env python3
"""
One-off helper: obtain a permanent Admin API access token for a paid/production Shopify
store via the Authorization Code Grant OAuth flow, and write it straight into the local
env file — the token value is never printed to stdout, so it never lands in a chat
transcript or shell history.

Why this exists: the Client Credentials Grant (simple client_id + client_secret exchange,
no browser step) only works on **development stores** — it fails with
`shop_not_permitted: Client credentials cannot be performed on this shop` on any paid
store, confirmed against dandoy-sports on 5 août 2026 (see 05_DOCS/import/api-credentials.md).
Authorization Code Grant is the only path left for a Dev Dashboard custom app on a live
store, but it normally requires a public redirect URL + running web server to catch the
OAuth callback. This script runs that catcher locally and temporarily instead.

Prerequisite (one-time, in the Dev Dashboard, on the app's configuration page):
    Add `http://localhost:8787/callback` to the app's allowed redirect URLs.

Usage:
    python3 get_shopify_access_token.py \\
        --shop dandoy-sports.myshopify.com \\
        --client-id 025239ab4713830c3756345fa1b7e914 \\
        --scopes write_gift_cards,read_gift_cards \\
        --env-file /home/gregory/Documents/Labo/dandoy/.dandoy_shopify_env \\
        --token-var SHOPIFY_DANDOY_ACCESS_TOKEN

The client secret is read from $SHOPIFY_OAUTH_CLIENT_SECRET (set it in your shell just
before running this, or export it from the target env file first) — never pass it as a
CLI argument (it would land in shell history / `ps`).
"""

import argparse
import hashlib
import hmac as hmac_lib
import http.server
import json
import os
import secrets
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser

RESULT = {}


def make_handler(expected_state, shop):
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass  # keep the console quiet — no query strings echoed

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != '/callback':
                self.send_response(404)
                self.end_headers()
                return

            params = {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}
            RESULT.update(params)

            ok = params.get('state') == expected_state and params.get('shop') == shop and 'code' in params
            self.send_response(200 if ok else 400)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            msg = "Autorisation reçue, vous pouvez fermer cet onglet." if ok else "Échec — state/shop invalide."
            self.wfile.write(f"<html><body><p>{msg}</p></body></html>".encode('utf-8'))

    return Handler


def verify_hmac(params, client_secret):
    hmac_value = params.get('hmac', '')
    pairs = sorted((k, v) for k, v in params.items() if k != 'hmac')
    message = '&'.join(f"{k}={v}" for k, v in pairs)
    digest = hmac_lib.new(client_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
    return hmac_lib.compare_digest(digest, hmac_value)


def upsert_env_var(env_file, var_name, value):
    lines = []
    found = False
    if os.path.exists(env_file):
        with open(env_file, encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(f'export {var_name}=') or line.strip().startswith(f'{var_name}='):
                    lines.append(f'export {var_name}={value}\n')
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f'export {var_name}={value}\n')
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--shop', required=True, help="xxx.myshopify.com")
    ap.add_argument('--client-id', required=True)
    ap.add_argument('--scopes', required=True, help="Comma-separated, e.g. write_gift_cards,read_gift_cards")
    ap.add_argument('--env-file', required=True)
    ap.add_argument('--token-var', required=True, help="e.g. SHOPIFY_DANDOY_ACCESS_TOKEN")
    ap.add_argument('--port', type=int, default=8787)
    args = ap.parse_args()

    client_secret = os.environ.get('SHOPIFY_OAUTH_CLIENT_SECRET')
    if not client_secret:
        print("ERREUR: exportez SHOPIFY_OAUTH_CLIENT_SECRET dans votre shell avant de lancer ce script.")
        sys.exit(1)

    redirect_uri = f"http://localhost:{args.port}/callback"
    state = secrets.token_urlsafe(24)

    server = http.server.HTTPServer(('localhost', args.port), make_handler(state, args.shop))
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    authorize_url = (
        f"https://{args.shop}/admin/oauth/authorize?"
        + urllib.parse.urlencode({
            'client_id': args.client_id,
            'scope': args.scopes,
            'redirect_uri': redirect_uri,
            'state': state,
        })
    )
    print(f"Ouverture du navigateur pour autoriser l'app sur {args.shop} …")
    print(f"Si rien ne s'ouvre, copiez cette URL manuellement :\n{authorize_url}\n")
    webbrowser.open(authorize_url)

    thread.join(timeout=180)
    if not RESULT:
        print("ERREUR: aucun callback reçu (timeout 180s) — vérifiez que "
              f"{redirect_uri} est bien enregistrée comme redirect URL de l'app dans le Dev Dashboard.")
        sys.exit(1)

    if not verify_hmac(RESULT, client_secret):
        print("ERREUR: HMAC invalide sur le callback — abandon (sécurité).")
        sys.exit(1)

    if RESULT.get('state') != state or RESULT.get('shop') != args.shop or 'code' not in RESULT:
        print(f"ERREUR: state/shop incohérents ou code manquant — abandon. "
              f"reçu: state_match={RESULT.get('state') == state} "
              f"shop_recu={RESULT.get('shop')!r} shop_attendu={args.shop!r} "
              f"code_present={'code' in RESULT} params_recus={sorted(RESULT.keys())}")
        sys.exit(1)

    body = urllib.parse.urlencode({
        'client_id': args.client_id,
        'client_secret': client_secret,
        'code': RESULT['code'],
    }).encode('utf-8')
    req = urllib.request.Request(
        f"https://{args.shop}/admin/oauth/access_token",
        data=body, method='POST',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode('utf-8'))

    token = payload['access_token']
    upsert_env_var(args.env_file, args.token_var, token)
    print(f"OK — token écrit dans {args.env_file} sous {args.token_var} "
          f"(longueur {len(token)}, scopes: {payload.get('scope', '?')}). Valeur jamais affichée.")


if __name__ == '__main__':
    main()
