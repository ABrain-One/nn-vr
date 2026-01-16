using System;
using UnityEngine;

public static class DeviceAnalytics
{
    public static DeviceAnalyticsData Collect()
    {
        return new DeviceAnalyticsData
        {
            timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0,
            memory_info = new MemoryInfo
            {
                total_ram_kb = $"{SystemInfo.systemMemorySize * 1024} kB",
                free_ram_kb = "N/A" // Quest does not expose this reliably
            },
            cpu_info = new CpuInfo
            {
                raw = SystemInfo.processorType
            }
        };
    }
}
