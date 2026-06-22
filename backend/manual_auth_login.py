"""Manual Appwrite login check (not run by Django test discovery)."""


import requests

BASE_URL = "http://localhost:8000/api/accounts"

test_users = [
    {
        "email": "admin@sgep.cm",
        "password": "AdminPassword123!",
        "role": "superadmin",
    },
    {
        "email": "comptable@sgep.cm",
        "password": "ComptablePassword123!",
        "role": "comptable",
    },
]


def main() -> None:
    print("=" * 60)
    print("Testing Appwrite Authentication")
    print("=" * 60)

    for user in test_users:
        print(f"\n🔐 Testing login for {user['email']}...")

        try:
            response = requests.post(
                f"{BASE_URL}/login/",
                json={
                    "email": user["email"],
                    "password": user["password"],
                },
                timeout=5,
            )

            if response.status_code == 200:
                data = response.json()
                print("✅ Login successful!")
                print(f"   Access Token: {data.get('access_token', '')[:50]}...")
                print(f"   Refresh Token: {data.get('refresh_token', '')[:50]}...")
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    print("\n" + "=" * 60)
    print("✨ Authentication test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
