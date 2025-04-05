using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Rendering;

public class Preprocess : MonoBehaviour {

    RenderTexture renderTexture;
    Vector2 scale = new Vector2(1, 1);
    Vector2 offset = Vector2.zero;

    UnityAction<byte[]> callback;

    public void ScaleAndCropImage(WebCamTexture webCamTexture, int desiredSize, UnityAction<byte[]> callback) {

        this.callback = callback;

        if (renderTexture == null) {
            renderTexture = new RenderTexture(desiredSize, desiredSize,0,RenderTextureFormat.ARGB32);
        }

        scale.x = (float)webCamTexture.height / (float)webCamTexture.width;
        offset.x = (1 - scale.x) / 2f;
        Graphics.Blit(webCamTexture, renderTexture, scale, offset);
        AsyncGPUReadback.Request(renderTexture, 0, TextureFormat.RGB24, OnCompleteReadback);
    }

    void OnCompleteReadback(AsyncGPUReadbackRequest request) {

        if (request.hasError) {
            Debug.Log("GPU readback error detected.");
            return;
        }

        callback.Invoke(request.GetData<byte>().ToArray());
    }
}
/*using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Rendering;

public class Preprocess : MonoBehaviour {
    RenderTexture renderTexture;
    Vector2 scale = new Vector2(1, 1);
    Vector2 offset = Vector2.zero;

    UnityAction<byte[]> callback;

    public void ScaleAndCropImage(WebCamTexture webCamTexture, int targetWidth, int targetHeight, bool grayscale, UnityAction<byte[]> callback) {
        this.callback = callback;

        if (renderTexture == null || renderTexture.width != targetWidth || renderTexture.height != targetHeight) {
            renderTexture = new RenderTexture(targetWidth, targetHeight, 0, RenderTextureFormat.ARGB32);
        }

        scale.x = (float)webCamTexture.height / (float)webCamTexture.width;
        offset.x = (1 - scale.x) / 2f;
        Graphics.Blit(webCamTexture, renderTexture, scale, offset);

        if (grayscale) {
            AsyncGPUReadback.Request(renderTexture, 0, TextureFormat.R8, OnCompleteReadback);
        } else {
            AsyncGPUReadback.Request(renderTexture, 0, TextureFormat.RGB24, OnCompleteReadback);
        }
    }

    void OnCompleteReadback(AsyncGPUReadbackRequest request) {
        if (request.hasError) {
            Debug.Log("GPU readback error detected.");
            return;
        }

        callback.Invoke(request.GetData<byte>().ToArray());
    }
}*/

