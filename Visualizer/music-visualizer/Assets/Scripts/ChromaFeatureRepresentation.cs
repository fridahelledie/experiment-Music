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

    [SerializeField] FeatureVisualizer OnsetA;
    [SerializeField] FeatureVisualizer OnsetA1;
    [SerializeField] FeatureVisualizer OnsetB;
    [SerializeField] FeatureVisualizer OnsetC;
    [SerializeField] FeatureVisualizer OnsetC1;
    [SerializeField] FeatureVisualizer OnsetD;
    [SerializeField] FeatureVisualizer OnsetD1;
    [SerializeField] FeatureVisualizer OnsetE;
    [SerializeField] FeatureVisualizer OnsetF;
    [SerializeField] FeatureVisualizer OnsetF1;
    [SerializeField] FeatureVisualizer OnsetG;
    [SerializeField] FeatureVisualizer OnsetG1;

    [SerializeField] FeatureVisualizer Amplitude;

    
    [SerializeField] BeatVisualzer beatVisualizer;


    private void Start()
    {
        //LocalServer.onChromaFeatureRecieved += ChromaFeatureRecieved;
        //LocalServer.OnsetFeatureRecieved += OnsetFeatureRecieved;
        FeaturePlayback.onChromaFeatureRecieved += ChromaFeatureRecieved;
        FeaturePlayback.OnsetFeatureRecieved += OnsetFeatureRecieved;
        FeaturePlayback.AmplitudeFeatureRecieved += AmplitudeFeatureReceived;
        FeaturePlayback.OnBeatDetected += BeatDetected;



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
        
        if (OnsetA != null)
        {
            OnsetA.UpdateFeature(onsetStrenght.Strenght);  
        }
        if (OnsetA1 != null)
        {
            OnsetA1.UpdateFeature(onsetStrenght.Strenght);
        }
        if (OnsetB != null)
        {
            OnsetB.UpdateFeature(onsetStrenght.Strenght);
        }
        if (OnsetC != null)
        {
            OnsetC.UpdateFeature(onsetStrenght.Strenght);
        }
        if (OnsetC1 != null)
        {
            OnsetC1.UpdateFeature(onsetStrenght.Strenght);
        }
        if (OnsetD != null)
        {
            OnsetD.UpdateFeature(onsetStrenght.Strenght);
        }
        if (OnsetD1 != null)
        {
            OnsetD1.UpdateFeature(onsetStrenght.Strenght);
        }
        if (OnsetE != null)
        {
            OnsetE.UpdateFeature(onsetStrenght.Strenght);
        }
        if (OnsetF != null)
        {
            OnsetF.UpdateFeature(onsetStrenght.Strenght);
        }
        if (OnsetF1 != null)
        {
            OnsetF1.UpdateFeature(onsetStrenght.Strenght);
        }
        if (OnsetG != null)
        {
            OnsetG.UpdateFeature(onsetStrenght.Strenght);
        }
        if (OnsetG1 != null)
        {
            OnsetG1.UpdateFeature(onsetStrenght.Strenght);
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
        Debug.Log("Beat detected!"); // Debug log to confirm the event is triggered

        if (beatVisualizer != null)
        {
            beatVisualizer.TriggerBeatEffect();
        }
    }
}
