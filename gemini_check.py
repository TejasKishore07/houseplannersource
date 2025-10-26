import os, sys, google.generativeai as genai

print("GEMINI_API_KEY set:", bool(os.environ.get("GEMINI_API_KEY")))
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

for name in ["gemini-1.5-flash-latest","gemini-1.5-pro-latest","gemini-1.5-flash","gemini-1.5-pro","gemini-1.0-pro","gemini-pro"]:
    try:
        m = genai.GenerativeModel(name)
        r = m.generate_content("Say ONLY OK")
        print("OK:", name, (r.text or "").strip())
        break
    except Exception as e:
        print("Fail:", name, "|", str(e)[:200])
else:
    sys.exit(2)
