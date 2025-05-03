using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class SSVEP_Blink : MonoBehaviour
{
    private float period;
    private float blinkingTime;
    
    [SerializeField] public float frequency;
    [SerializeField] public float phaseShift = 0; //Radians (pi)
    [SerializeField] private Color off;
    [SerializeField] private Color on;

    public SpriteRenderer image;
    private bool blinking;
    private float startTime;

    // Start is called before the first frame update
    void Start() {
        period = 1f/frequency;
        blinking = false;
    }

    void Update() {
        if (blinking) {
            Blink();
        }
    }

    public void StartBlink() {
        blinking = true;
        startTime = Time.time;
    }

    public void StopBlink() {
        blinking = false;
        image.color = off;
    }

    // Update is called once per frame
    private void Blink() {
        float colorMix = Mathf.InverseLerp(-1f, 1f, Mathf.Sin(((Time.time-startTime) % 10.0f) * Mathf.PI * frequency * 2.0f + phaseShift*Mathf.PI));
        image.color = Color.Lerp(off, on, colorMix);
    }
}
