public class AmplitudeFeature
{
    public float Strenght = 0;
    

    public AmplitudeFeature(float firstValue)
    {
        Strenght = firstValue;
    }

    public static AmplitudeFeature zero()
    {
        return new AmplitudeFeature(0);
    }

    public override string ToString()
    {
        return $"{Strenght}";
    }
}
