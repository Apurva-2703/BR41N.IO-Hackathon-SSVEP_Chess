using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Chess.Game;

public class DataCollector : MonoBehaviour
{
    public SSVEP_Blink[] stims;
    [SerializeField] public Transform stimulii;
    [SerializeField] public GameManager gameManager;
    private HumanPlayer player;

    public float stimulusTime = 4;
    public float restTime = 3;


    private float leftHandX = -5.5f;
    private float rightHandX = 3.9f;
    float[] verticalYPos = { 6.02f, 4.94f, 3.84f, 3.02f, 1.93f, 0.98f, -0.06f, -0.95f };

    private float topHandY = 7f;
    private float bottomHandY = -2.02f;
    float[] horizontalXPos = { -4.29f, -3.3f, -2.24f, -1.21f, -0.25f, 0.78f, 1.76f, 2.81f };

    public Button startButton;

    Color selected = new Color(0f, 1f, 0f, 1f);
    Color notSelected = new Color(1f, 0f, 0f, 1f);
    private bool isSelecting = true;

    [SerializeField] private DataCommunicate communicator;


    // Start is called before the first frame update
    void Start() {
        int count = 8;
        stims = new SSVEP_Blink[count];

        for (int i = 0; i < count; i++)
        {
            string name = "stim" + (i + 1); // stim1, stim2, ...
            stims[i] = stimulii.Find(name)?.gameObject.GetComponent<SSVEP_Blink>();

            if (stims[i] == null)
                Debug.LogWarning(name + " not found as a child!");
        }

        SetVerticalPositions();
        player = gameManager.GetHumanPlayerIntstance();
        isSelecting = true;
    }


    // Update is called once per frame
    void Update() {
    }


    public void StartDataCollection() {
        startButton.interactable = false;
        startButton.gameObject.SetActive(false);
        StartCoroutine(Selection());
    }



    IEnumerator Selection() {
        int selectedRow = Random.Range(1, 9); 
        int selectedCol = Random.Range(1, 9);

        // Set to vertical positions
        SetVerticalPositions();

        // Set the selected row
        ResetColors();
        // SelectStimulusColor(stims[selectedRow-1].gameObject, false);
        yield return new WaitForSeconds(restTime);

        // Blink for rows
        // communicator.SendMessageToPython("3"+selectedRow);
        communicator.SendMessageToPython("START");
        StartBlink();
        yield return new WaitForSeconds(stimulusTime);
        StopBlink();
        communicator.SendMessageToPython("STOP");
        Debug.Log(communicator.decision);
        yield return new WaitForSeconds(1);
        selectedRow = 7-communicator.decision;

        //TODO: SAVE SELECTED ROW

        // Rest
        yield return new WaitForSeconds(restTime);
        SetHorizontalPositions();
        ResetColors();
        // SelectStimulusColor(stims[selectedCol-1].gameObject, false);
        yield return new WaitForSeconds(restTime);

        // Blink for columns
        // communicator.SendMessageToPython("9"+selectedCol);
        communicator.SendMessageToPython("START");
        StartBlink();
        yield return new WaitForSeconds(stimulusTime);
        StopBlink();
        communicator.SendMessageToPython("STOP");
        yield return new WaitForSeconds(1);
        selectedCol = communicator.decision;

        SetVerticalPositions();
        ResetColors();
        startButton.interactable = true;
        startButton.gameObject.SetActive(true);

        //TODO: SAVE SELECTED COLUMN
        player.HandleInput(selectedRow, selectedCol);
        Debug.Log("Selected col " + selectedCol + " Selected Row " + selectedRow);
    }


    private void StartBlink() {
        for (int i = 0; i < 8; ++i) {
            stims[i].StartBlink();
        }
    }

    private void StopBlink() {
        for (int i = 0; i < 8; ++i) {
            stims[i].StopBlink();
        }
    }


    private void SetVerticalPositions() {
        for (int i = 0; i < 8; ++i) {
            float tempX = 0;
            if (i%2 == 0) {
                tempX = leftHandX;
            }
            else {
                tempX = rightHandX;
            }
            stims[i].gameObject.transform.localPosition = new Vector3(tempX, verticalYPos[i], 0f); // x=2, y=3, z=0
        }
    }

    private void SetHorizontalPositions() {
        for (int i = 0; i < 8; ++i) {
            float tempY = 0;
            if (i%2 == 0) {
                tempY = topHandY;
            }
            else {
                tempY = bottomHandY;
            }
            stims[i].gameObject.transform.localPosition = new Vector3(horizontalXPos[i], tempY, 0f); // x=2, y=3, z=0
        }
    }


    private void SelectStimulusColor(GameObject stim, bool isRed) {
        Transform child = stim.transform.Find("Dot");
        SpriteRenderer img = child.GetComponent<SpriteRenderer>();

        if (isRed){
            img.color = notSelected;
        }
        else{
            img.color = selected;
        }
    }

    private void ResetColors() {
        for (int i = 0; i < 8; ++i) {
            SelectStimulusColor(stims[i].gameObject, true);
        }
    }
}
