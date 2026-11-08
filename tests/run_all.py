"""Führt alle Headless-Tests nacheinander aus. Aufruf aus dem Repository: python tests/run_all.py"""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = ["widget_regression.py", "export_import.py", "obs_dialogs.py", "gemini_parts.py", "chat_section.py", "history_pairs.py", "summary_condense.py", "answer_header.py",
         "benchmark_gemini.py", "benchmark_providers.py"]
env = dict(os.environ, BDU_TEST_OUT=os.environ.get("BDU_TEST_OUT") or tempfile.mkdtemp(prefix="bdu-tests-"))
failed = []
for t in TESTS:
    print(f"\n===== {t}", flush=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, t)], env=env, capture_output=True, text=True)
    lines = (r.stdout + r.stderr).strip().splitlines()
    for line in lines:
        if not line.startswith(("PASS", "OK  ")):
            print(line)
    if r.returncode != 0:
        failed.append(t)
print("\n" + ("ALLE TESTS BESTANDEN" if not failed else "FEHLGESCHLAGEN: " + ", ".join(failed)))
print("Screenshots und Testdaten: " + env["BDU_TEST_OUT"])
sys.exit(1 if failed else 0)
