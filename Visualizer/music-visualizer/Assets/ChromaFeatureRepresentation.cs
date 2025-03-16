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

    [SerializeField] FeatureVisualizer Aonset;
    [SerializeField] FeatureVisualizer A_sharponset;
    [SerializeField] FeatureVisualizer Bonset;
    [SerializeField] FeatureVisualizer Conset;
    [SerializeField] FeatureVisualizer C_sharponset;
    [SerializeField] FeatureVisualizer Donset;
    [SerializeField] FeatureVisualizer D_sharponset;
    [SerializeField] FeatureVisualizer Eonset;
    [SerializeField] FeatureVisualizer Fonset;
    [SerializeField] FeatureVisualizer F_sharponset;
    [SerializeField] FeatureVisualizer Gonset;
    [SerializeField] FeatureVisualizer G_sharponset;

    private void Start()
    {
        LocalServer.onChromaFeatureRecieved += ChromaFeatureRecieved;
        LocalServer.OnsetFeatureRecieved += OnsetFeatureRecieved;
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
        if (Aonset != null)
        {
            Aonset.UpdateFeature(onsetStrenght.Aonset);
        }

        if (A_sharponset != null)
        {
            A_sharponset.UpdateFeature(onsetStrenght.A_sharponset);
        }

        if (Bonset != null)
        {
            Bonset.UpdateFeature(onsetStrenght.Bonset);
        }

        if (Conset != null)
        {
            Conset.UpdateFeature(onsetStrenght.Conset);
        }

        if (C_sharponset != null)
        {
            C_sharponset.UpdateFeature(onsetStrenght.C_sharponset);
        }

        if (Donset != null)
        {
            Donset.UpdateFeature(onsetStrenght.Donset);
        }

        if (D_sharponset != null)
        {
            D_sharponset.UpdateFeature(onsetStrenght.D_sharponset);
        }

        if (Eonset != null)
        {
            Eonset.UpdateFeature(onsetStrenght.Eonset);
        }

        if (Fonset != null)
        {
            Fonset.UpdateFeature(onsetStrenght.Fonset);
        }

        if (F_sharponset != null)
        {
            F_sharponset.UpdateFeature(onsetStrenght.F_sharponset);
        }

        if (Gonset != null)
        {
            Gonset.UpdateFeature(onsetStrenght.Gonset);
        }

        if (G_sharponset != null)
        {
            G_sharponset.UpdateFeature(onsetStrenght.G_sharponset);
        }
    }
}
