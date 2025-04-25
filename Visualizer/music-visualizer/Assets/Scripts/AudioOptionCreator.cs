using UnityEngine;
using UnityEngine.UI;
using System.IO;
using TMPro;

public class AudioOptionCreator : MonoBehaviour
{
    public GameObject uiPrefab;
    public ScrollRect scrollRect;

    void Start()
    {
        // Call the method to load and instantiate UI elements
        CreateAudioList();
    }

    void CreateAudioList()
    {
        // Define the path to the StreamingAssets/Audio folder
        string audioFolderPath = Path.Combine(Application.streamingAssetsPath, "Audio");

        // Check if the folder exists
        if (Directory.Exists(audioFolderPath))
        {
            // Define allowed audio extensions
            string[] allowedExtensions = { ".mp3", ".wav", ".ogg", ".aiff" };

            // Get all files in the folder
            string[] allFiles = Directory.GetFiles(audioFolderPath);

            // Clear any existing content in the ScrollRect
            foreach (Transform child in scrollRect.content)
            {
                Destroy(child.gameObject);
            }

            // Instantiate a prefab for each valid audio file
            foreach (string filePath in allFiles)
            {
                string extension = Path.GetExtension(filePath).ToLower();

                // Skip files with unwanted extensions
                if (System.Array.Exists(allowedExtensions, ext => ext == extension))
                {
                    string fileName = Path.GetFileNameWithoutExtension(filePath);

                    GameObject audioItem = Instantiate(uiPrefab, scrollRect.content);
                    AudioOption a = audioItem.GetComponent<AudioOption>();
                    a.fileName = fileName;
                    a.fileType = extension;

                    audioItem.GetComponentInChildren<TextMeshProUGUI>().text = fileName;
                }
            }
        }
        else
        {
            Debug.LogError("Audio folder does not exist at path: " + audioFolderPath);
        }
    }

}