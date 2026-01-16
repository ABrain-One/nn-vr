using System;
using System.Collections.Generic;

[Serializable]
public class RunConfig
{
    public string backend;          // "cpu" | "gpu"
    public ModelEntry[] models;     // length = 1 for now
    public string output_path;
}

[Serializable]
public class ModelEntry
{
    public string name;
    public string path;
    public string hash;
}

[Serializable]
public class InferenceResult
{
    public string model_name;
    public string model_hash;
    public string backend;
    public long duration_ns;
    public string status;
    public DeviceAnalyticsData device_analytics;
}

[Serializable]
public class DeviceAnalyticsData
{
    public double timestamp;
    public MemoryInfo memory_info;
    public CpuInfo cpu_info;
}

[Serializable]
public class MemoryInfo
{
    public string total_ram_kb;
    public string free_ram_kb;
}

[Serializable]
public class CpuInfo
{
    public string raw;
}
