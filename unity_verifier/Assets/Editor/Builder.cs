using UnityEditor;

public class Builder
{
    private static void Build(string exeF, BuildTarget target)
    {
        BuildPlayerOptions buildPlayerOptions = new BuildPlayerOptions();
        buildPlayerOptions.locationPathName = exeF;
        buildPlayerOptions.target = target;
        buildPlayerOptions.scenes = new[] { "Assets/Scenes/TestScene.unity" };
        BuildPipeline.BuildPlayer(buildPlayerOptions);
    }

    public static void BuildWindows()
    {
        Build(
            "./tmp.exe",
            BuildTarget.StandaloneWindows64
        );
    }

    public static void BuildLinux()
    {
        Build(
            "./tmp_exe",
            BuildTarget.StandaloneLinux64
        );
    }
}
