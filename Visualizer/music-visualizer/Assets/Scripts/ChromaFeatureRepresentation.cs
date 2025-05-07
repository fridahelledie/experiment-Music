using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ChromaFeatureRepresentation : MonoBehaviour
{
    [SerializeField] FeatureVisualizer A;
    [SerializeField] FeatureVisualizer A_sharp;
    [SerializeField] FeatureVisualizer B;
    [SerializeField] FeatureVisualizer C;
    [SerializeField] FeatureVisualizer C_sharp;
    [SerializeField] FeatureVisualizer D;
    [SerializeField] FeatureVisualizer D_sharp;
    [SerializeField] FeatureVisualizer E;
    [SerializeField] FeatureVisualizer F;
    [SerializeField] FeatureVisualizer F_sharp;
    [SerializeField] FeatureVisualizer G;
    [SerializeField] FeatureVisualizer G_sharp;
    

    [SerializeField] FeatureVisualizer Amplitude;

    [SerializeField] FeatureVisualizer MaxChroma;

    [SerializeField] BeatVisualzer beatVisualizer;

    [SerializeField] CircleOfFifthsVisualizer circleVisualizer;


    private void Start()
    {
        //LocalServer.onChromaFeatureRecieved += ChromaFeatureRecieved;
        //LocalServer.OnsetFeatureRecieved += OnsetFeatureRecieved;
        FeaturePlayback.onChromaFeatureRecieved += ChromaFeatureRecieved;
        FeaturePlayback.AmplitudeFeatureRecieved += AmplitudeFeatureReceived;
        FeaturePlayback.OnBeatDetected += BeatDetected;
        FeaturePlayback.OnMaxChromaRecieved += MaxChromaRecieved;
    }

    void ChromaFeatureRecieved(ChromaFeature chromaFeature)
    {
        if (circleVisualizer != null)
        {
            float[] reordered = new float[12];

            // Circle of fifths order: C, G, D, A, E, B, F#, C#, G#, D#, A#, F
            reordered[0] = chromaFeature.C;
            reordered[1] = chromaFeature.G;
            reordered[2] = chromaFeature.D;
            reordered[3] = chromaFeature.A;
            reordered[4] = chromaFeature.E;
            reordered[5] = chromaFeature.B;
            reordered[6] = chromaFeature.F_sharp;
            reordered[7] = chromaFeature.C_sharp;
            reordered[8] = chromaFeature.G_sharp;
            reordered[9] = chromaFeature.D_sharp;
            reordered[10] = chromaFeature.A_sharp;
            reordered[11] = chromaFeature.F;

            circleVisualizer.UpdateFeature(reordered);

        }

        if (A != null)
        {
            A.UpdateFeature(chromaFeature.A);
        }

        if (A_sharp != null)
        {
            A_sharp.UpdateFeature(chromaFeature.A_sharp);
        } 

        if (B != null)
        {
            B.UpdateFeature(chromaFeature.B);
        }

        if (C != null)
        {
            C.UpdateFeature(chromaFeature.C);
        }

        if (C_sharp != null)
        {
            C_sharp.UpdateFeature(chromaFeature.C_sharp);
        }

        if (D != null)
        {
            D.UpdateFeature(chromaFeature.D);
        }

        if (D_sharp != null)
        {
            D_sharp.UpdateFeature(chromaFeature.D_sharp);
        }

        if (E != null)
        {
            E.UpdateFeature(chromaFeature.E);
        }

        if (F != null)
        {
            F.UpdateFeature(chromaFeature.F);
        }

        if (F_sharp != null)
        {
            F_sharp.UpdateFeature(chromaFeature.F_sharp);
        }

        if (G != null)
        {
            G.UpdateFeature(chromaFeature.G);
        }

        if (G_sharp != null)
        {
            G_sharp.UpdateFeature(chromaFeature.G_sharp);
        }
    }

    void AmplitudeFeatureReceived(AmplitudeFeature amplitude)
    {
        if (Amplitude != null)
        {
            Amplitude.UpdateFeature(amplitude.Strenght);
        }
    }
    void BeatDetected()
    {
       

        if (beatVisualizer != null)
        {
            beatVisualizer.TriggerBeatEffect();
        }
    }

    void MaxChromaRecieved(float maxValue)
    {
        if (MaxChroma != null)
        {
            MaxChroma.UpdateFeature(maxValue);
        }
    }
}
