from dotenv import load_dotenv

load_dotenv()

import os
from supabase import create_client


url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

print("SUPABASE_URL loaded:", url is not None)
print("SUPABASE_SERVICE_KEY loaded:", key is not None)

if not url or not key:
    raise RuntimeError("Missing Supabase environment variables")

supabase = create_client(url, key)

result = supabase.table("documents").insert(
    {
        "content": "Supabase connection test chunk. No embedding yet.",
        "metadata": {
            "source": "test_supabase.py",
            "type": "connection_test",
        },
    }
).execute()

print(result)