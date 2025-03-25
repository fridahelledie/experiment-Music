using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ChromaFeature
{
    public float A = 0;
    public float A_sharp = 0;
    public float B = 0;
    public float C = 0;
    public float C_sharp = 0;
    public float D = 0;
    public float D_sharp = 0;
    public float E = 0;
    public float F = 0;
    public float F_sharp = 0;
    public float G = 0;
    public float G_sharp = 0;

    public ChromaFeature(float a, float a_sharp, float b, float c, float c_sharp, float d, float d_sharp, float e, float f, float f_sharp, float g, float g_sharp)
    {
        A = a;
        A_sharp = a_sharp;
        B = b;
        C = c;
        C_sharp = c_sharp;
        D = d;
        D_sharp = d_sharp;
        E = e;
        F = f;
        F_sharp = f_sharp;
        G = g;
        G_sharp = g_sharp;
    }

    public static ChromaFeature zero()
    {
        return new ChromaFeature(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
    }

    public override string ToString()
    {
        return $"{A}, {A_sharp}, {B}, {C}, {C_sharp}, {D}, {D_sharp}, {E}, {F}, {F_sharp}, {G}, {G_sharp}";
    }
}
