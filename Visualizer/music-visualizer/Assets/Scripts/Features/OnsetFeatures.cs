public class OnsetFeatures
{
    public float Strenght = 0;
    

    public OnsetFeatures(float firstValue)
    {
        Strenght = firstValue;
        
    }

    public static OnsetFeatures zero()
    {
        return new OnsetFeatures(0);
    }

    public override string ToString()
    {
        return $"{Strenght}";
    }
}
