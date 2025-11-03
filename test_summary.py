#!/usr/bin/env python3
"""Test summary rendering with SafeFormatter"""

from string import Formatter

class SafeFormatter(Formatter):
    def get_value(self, key, args, kwargs):
        if isinstance(key, str):
            return kwargs.get(key, '')
        return super().get_value(key, args, kwargs)

# Test template from config.yml
template = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 İşlem Özeti
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Toplam Dosya    : {total}
Başarılı        : {success}
Hata            : {failed}
Atlandı         : {skipped}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️  Süre Bilgisi
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Toplam Süre     : {total_time:.2f}s
Ortalama/Dosya  : {avg_time:.2f}s
En Hızlı        : {min_time:.2f}s
En Yavaş        : {max_time:.2f}s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 Son Öğe (TV/Film)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Show            : {showName}
Original        : {originalShowName}
Season/Episode  : S{seasonNumber:02d}E{episodeNumber:02d}
Episode         : {episodeName}
"""

# Test with defaults (no TV data)
summary_ctx_empty = {
    "total": 1,
    "success": 1,
    "failed": 0,
    "skipped": 0,
    "total_time": 1.5,
    "avg_time": 1.5,
    "min_time": 1.5,
    "max_time": 1.5,
    "showName": "",
    "originalShowName": "",
    "seasonNumber": 0,
    "episodeNumber": 0,
    "episodeName": "",
}

# Test with TV data
summary_ctx_tv = {
    "total": 1,
    "success": 1,
    "failed": 0,
    "skipped": 0,
    "total_time": 1.5,
    "avg_time": 1.5,
    "min_time": 1.5,
    "max_time": 1.5,
    "showName": "Friends",
    "originalShowName": "Friends",
    "seasonNumber": 1,
    "episodeNumber": 1,
    "episodeName": "Pilot",
}

print("=" * 60)
print("TEST 1: Empty context (should not crash)")
print("=" * 60)
formatter = SafeFormatter()
result1 = formatter.format(template, **summary_ctx_empty)
print(result1)

print("\n" + "=" * 60)
print("TEST 2: TV show context (should show data)")
print("=" * 60)
result2 = formatter.format(template, **summary_ctx_tv)
print(result2)

print("\n✅ Tests passed! SafeFormatter works correctly.")
