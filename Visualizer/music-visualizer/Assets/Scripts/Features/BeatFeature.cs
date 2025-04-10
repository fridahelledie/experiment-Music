using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BeatFeature
{
    public float Tempo = 0; // Tempo here is one number 
    public List<float> BeatTimes = new List<float>(); //liste over beat stamps 
    public BeatFeature(float tempo, List<float> beatTimes)
    {
        Tempo = tempo;
        BeatTimes = beatTimes;
    }

    public static BeatFeature Zero()
    {
        return new BeatFeature(0, new List<float>());
    }

    public override string ToString()
    {
        return $"Tempo: {Tempo}, Beats: {string.Join(", ", BeatTimes)}";
    }
}
