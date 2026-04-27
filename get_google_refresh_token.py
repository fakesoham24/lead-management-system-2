"""
Google OAuth Refresh Token Generator
=====================================
Run this script ONCE to get a valid refresh token for Google Calendar.

Steps:
  1. Open Google Cloud Console → Your Project → APIs & Services → Credentials
  2. Find your OAuth 2.0 Client (Desktop app type) → Download or note Client ID + Secret
  3. Run:  python get_google_refresh_token.py
  4. A browser window opens → sign in with the Google account whose calendar you want to use
  5. Approve the permissions → copy the refresh token shown
  6. Paste it into Admin Panel → Google Calendar Settings → Refresh Token

Requirements: pip install google-auth-oauthlib
"""

import sys
import webbrowser
import json
import urllib.request
import urllib.parse

SCOPES = ["https://www.googleapis.com/auth/calendar"]
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"   # out-of-band (copy-paste flow)

def main():
    print("=" * 60)
    print("  Google Calendar Refresh Token Generator")
    print("=" * 60)

    client_id     = input("\nEnter Client ID     : ").strip()
    client_secret = input("Enter Client Secret : ").strip()

    if not client_id or not client_secret:
        print("❌ Client ID and Secret are required.")
        sys.exit(1)

    # Step 1: Build the authorization URL
    params = {
        "client_id":     client_id,
        "redirect_uri":  REDIRECT_URI,
        "response_type": "code",
        "scope":         " ".join(SCOPES),
        "access_type":   "offline",
        "prompt":        "consent",    # Force consent to always get refresh token
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)

    print("\n📌 Step 1: Opening browser for Google sign-in...")
    print("   If browser does not open, manually visit:\n")
    print(f"   {auth_url}\n")
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    print("📌 Step 2: Sign in with your Google account and approve Calendar access.")
    print("           After approval, Google shows an authorization code.\n")
    auth_code = input("Paste the Authorization Code here: ").strip()

    if not auth_code:
        print("❌ Authorization code is required.")
        sys.exit(1)

    # Step 3: Exchange auth code for tokens
    token_data = urllib.parse.urlencode({
        "code":           auth_code,
        "client_id":      client_id,
        "client_secret":  client_secret,
        "redirect_uri":   REDIRECT_URI,
        "grant_type":     "authorization_code",
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=token_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"\n❌ Token exchange failed ({e.code}): {body}")
        sys.exit(1)

    if "refresh_token" not in result:
        print(f"\n❌ No refresh token in response: {result}")
        print("   Make sure prompt=consent was used and you approved the request.")
        sys.exit(1)

    refresh_token = result["refresh_token"]
    access_token  = result.get("access_token", "")

    print("\n" + "=" * 60)
    print("  ✅ SUCCESS! Your credentials:")
    print("=" * 60)
    print(f"\n  Client ID     : {client_id}")
    print(f"  Client Secret : {client_secret}")
    print(f"  Refresh Token : {refresh_token}")
    print(f"\n  Access Token (short-lived): {access_token[:40]}...")
    print("\n📋 Copy the Refresh Token above and paste it into:")
    print("   Admin Panel → Google Calendar Settings → Refresh Token")
    print("=" * 60)

if __name__ == "__main__":
    main()
