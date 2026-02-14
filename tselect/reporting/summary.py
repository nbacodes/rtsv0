def generate_summary(components, total_tests, duration, status, baseline=None):
    print("\n=== TSELECT REPORT ===")
    print("Components:", components)
    print("Tests executed:", total_tests)
    print(f"Execution time: {duration:.2f}s")
    print("Status:", status)

    if baseline:
        saved = baseline - duration
        pct = (saved / baseline) * 100 if baseline else 0

        print(f"\nBaseline time: {baseline:.2f}s")
        print(f"Time saved: {saved:.2f}s ({pct:.1f}% faster)")
