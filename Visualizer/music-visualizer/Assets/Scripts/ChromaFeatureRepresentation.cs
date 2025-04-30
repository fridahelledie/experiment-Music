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

    [SerializeField] FeatureVisualizer Onset;
    

    [SerializeField] FeatureVisualizer Amplitude;

    [SerializeField] FeatureVisualizer MaxChroma;

    [SerializeField] BeatVisualzer beatVisualizer;


    private void Start()
    {
        //LocalServer.onChromaFeatureRecieved += ChromaFeatureRecieved;
        //LocalServer.OnsetFeatureRecieved += OnsetFeatureRecieved;
        FeaturePlayback.onChromaFeatureRecieved += ChromaFeatureRecieved;
        FeaturePlayback.OnsetFeatureRecieved += OnsetFeatureRecieved;
        FeaturePlayback.AmplitudeFeatureRecieved += AmplitudeFeatureReceived;
        FeaturePlayback.OnBeatDetected += BeatDetected;
        FeaturePlayback.OnMaxChromaRecieved += MaxChromaRecieved;
    }

    void ChromaFeatureRecieved(ChromaFeature chromaFeature)
    {
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

    void OnsetFeatureRecieved(OnsetFeatures onsetStrenght)
    {
        
        if (Onset != null)
        {
            Onset.UpdateFeature(onsetStrenght.Strenght);  
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
