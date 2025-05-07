public class OnsetFeatures
{
    public float Strenght = 0;
    public bool Detected = false;
    

    public OnsetFeatures(float firstValue, bool isDetected)
    {
        Strenght = firstValue;
        Detected = isDetected;
    }

    public static OnsetFeatures zero()
    {
        return new OnsetFeatures(0, false);
    }

    public override string ToString()
    {
        return $"{Strenght}";
    }
}
