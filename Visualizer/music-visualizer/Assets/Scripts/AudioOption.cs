using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AudioOption : MonoBehaviour
{
    public string fileName;
    public string fileType;

    public void selectThis()
    {
        playbackInitializer.instance.selectedSong = fileName;
        playbackInitializer.instance.songFiletype = fileType;
    }
}
