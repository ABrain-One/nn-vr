using UnityEngine;
using UnityEditor;
using System.IO;

public class OnnxAutoValidator : AssetPostprocessor
{
    private static string validationFile = "Assets/onnx_validation.txt"; 

    private static void OnPostprocessAllAssets(
        string[] importedAssets, string[] deletedAssets, string[] movedAssets, string[] movedFromAssetPaths)
    {
        foreach (string asset in importedAssets)
        {
            if (asset.EndsWith(".onnx")) 
            {
                ValidateModel(asset);
            }
        }
    }

    private static void ValidateModel(string modelPath)
    {
        var model = AssetDatabase.LoadAssetAtPath<Object>(modelPath);
        
        if (model != null) 
        {
            Debug.Log($"ONNX Model '{modelPath}' imported successfully!");
            File.WriteAllText(validationFile, "success");
        }
        else
        {
            Debug.LogError($"ONNX Model '{modelPath}' failed to import.");
            File.WriteAllText(validationFile, "failure");
        }
        
        AssetDatabase.Refresh(); 
    }
}