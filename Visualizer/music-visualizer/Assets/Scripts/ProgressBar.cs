using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

[ExecuteInEditMode()]
public class ProgressBar : MonoBehaviour
{
    public int max; //skal connectes med json
    public int current; // skal følges med timestamps
    public Image mask;

    // Start is called before the first frame update
    void Update()
    {
        GetCurrentFill();
    }

    void GetCurrentFill()
    {
        float fillamount = (float)current / (float)max;
        mask.fillAmount = fillamount;
    }
}
