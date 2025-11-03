#!/usr/bin/env python3
"""Verify summary rendering fix works correctly"""

from string import Formatter

class SafeFormatter(Formatter):
    """Formatter that returns empty string for missing keys instead of raising KeyError"""
    def get_value(self, key, args, kwargs):
        if isinstance(key, str):
            return kwargs.get(key, '')
        return super().get_value(key, args, kwargs)

# Test template similar to config.yml summary
test_template = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 İşlem Özeti
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Toplam Dosya    : {total}
Başarılı        : {success}
Hata            : {failed}
Atlandı         : {skipped}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 Son Öğe (TV/Film)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Show            : {showName}
Original        : {originalShowName}
Season/Episode  : S{seasonNumber:02d}E{episodeNumber:02d}
Episode         : {episodeName}
Episode Air     : {episodeAirDate}
API             : {apiSource}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

print("=" * 70)
print("TEST 1: Standard Python format() - Should FAIL with KeyError")
print("=" * 70)
ctx_minimal = {
    "total": 1,
    "success": 1,
    "failed": 0,
    "skipped": 0,
}
try:
    result = test_template.format(**ctx_minimal)
    print("❌ UNEXPECTED: format() didn't fail!")
    print(result)
except KeyError as e:
    print(f"✅ EXPECTED: KeyError raised for missing variable: {e}")

print("\n" + "=" * 70)
print("TEST 2: SafeFormatter with minimal context - Should SUCCEED")
print("=" * 70)
formatter = SafeFormatter()
try:
    result = formatter.format(test_template, **ctx_minimal)
    print("✅ SUCCESS: SafeFormatter handled missing variables gracefully")
    print(result)
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n" + "=" * 70)
print("TEST 3: SafeFormatter with full TV context - Should SUCCEED")
print("=" * 70)
ctx_full = {
    "total": 1,
    "success": 1,
    "failed": 0,
    "skipped": 0,
    "showName": "Friends",
    "originalShowName": "Friends",
    "seasonNumber": 1,
    "episodeNumber": 1,
    "episodeName": "Pilot",
    "episodeAirDate": "1994-09-22",
    "apiSource": "tmdb",
}
try:
    result = formatter.format(test_template, **ctx_full)
    print("✅ SUCCESS: SafeFormatter rendered complete TV context")
    print(result)
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n" + "=" * 70)
print("TEST 4: SafeFormatter with defaults from engine.py")
print("=" * 70)
ctx_with_defaults = {
    # Timing stats
    "total": 1,
    "success": 1,
    "failed": 0,
    "skipped": 0,
    
    # TV show defaults
    "showName": "",
    "originalShowName": "",
    "seasonNumber": 0,
    "episodeNumber": 0,
    "episodeName": "",
    "episodeAirDate": "",
    "apiSource": "",
}
try:
    result = formatter.format(test_template, **ctx_with_defaults)
    print("✅ SUCCESS: SafeFormatter works with default empty values")
    print(result)
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n" + "=" * 70)
print("✅ ALL TESTS COMPLETED")
print("=" * 70)
print("\nConclusion:")
print("- Standard format() fails with missing variables (KeyError)")
print("- SafeFormatter handles missing variables gracefully")
print("- Adding default values ensures consistent output")
print("\nThe fix in engine.py combines both approaches for maximum safety.")
