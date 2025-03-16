using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class OnsetFeatures
{
    public float Aonset = 0;
    public float A_sharponset = 0;
    public float Bonset = 0;
    public float Conset = 0;
    public float C_sharponset = 0;
    public float Donset = 0;
    public float D_sharponset = 0;
    public float Eonset = 0;
    public float Fonset = 0;
    public float F_sharponset = 0;
    public float Gonset = 0;
    public float G_sharponset = 0;

    public OnsetFeatures(float aonset, float a_sharponset, float bonset, float conset, float c_sharponset, float donset, float d_sharponset, float eonset, float fonset, float f_sharponset, float gonset, float g_sharponset)
    {
        Aonset = aonset;
        A_sharponset = a_sharponset;
        Bonset = bonset;
        Conset = conset;
        C_sharponset = c_sharponset;
        Donset = donset;
        D_sharponset = d_sharponset;
        Eonset = eonset;
        Fonset = fonset;
        F_sharponset = f_sharponset;
        Gonset = gonset;
        G_sharponset = g_sharponset;
    }

    public static OnsetFeatures zero()
    {
        return new OnsetFeatures(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
    }

    public override string ToString()
    {
        return $"{Aonset}, {A_sharponset}, {Bonset}, {Conset}, {C_sharponset}, {Donset}, {D_sharponset}, {Eonset}, {Fonset}, {F_sharponset}, {Gonset}, {G_sharponset}";
    }
}
