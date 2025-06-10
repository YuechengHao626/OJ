from datetime import datetime, timezone

def to_rfc3339_seconds_zulu(dt: datetime) -> str:
    """
    将 Python datetime(naive或aware) 转换为:
    YYYY-MM-DDTHH:MM:SSZ
    例如: 2025-04-03T11:06:11Z
    """
    # 如果是 naive datetime，则假设其本身就是 UTC 时间
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # isoformat(timespec='seconds') 去掉小数秒, +00:00 → Z
    return dt.isoformat(timespec='seconds').replace("+00:00", "Z")
