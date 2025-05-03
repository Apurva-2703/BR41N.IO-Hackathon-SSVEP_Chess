using System;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class DataCommunicate : MonoBehaviour
{
    private Thread socketThread; // Thread for socket communication
    private bool isRunning = false; // Flag to control the thread
    private string messageToSend = ""; // Message to send
    private bool sendMessageFlag = false; // Indicates when a message needs to be sent
    public int decision = 0;

    void Start()
    {
        // Start the socket thread
        isRunning = true;
        socketThread = new Thread(SocketCommunicationThread);
        socketThread.Start();
    }

    // Function to send a message to Python
    public void SendMessageToPython(string message)
    {
        if (!sendMessageFlag) // Prevent overwriting an ongoing message
        {
            messageToSend = message; // Assign the message
            sendMessageFlag = true; // Signal that there's a message to send
        }
        else
        {
            Debug.LogWarning("Message already being sent, wait for completion.");
        }
    }

    private void SocketCommunicationThread()
    {
        try
        {
            using (TcpClient client = new TcpClient("127.0.0.1", 65432))
            {
                NetworkStream stream = client.GetStream();

                // Optionally, wait for a response
                GetAndPrintMessage(stream);

                while (isRunning)
                {
                    if (sendMessageFlag)
                    {
                        // Send the message
                        byte[] data = Encoding.UTF8.GetBytes(messageToSend);
                        stream.Write(data, 0, data.Length);
                        Debug.Log($"Message sent to Python: {messageToSend}");

                        // Clear the flag
                        sendMessageFlag = false;

                        GetAndPrintMessage(stream);
                    }

                    // Sleep briefly to avoid excessive CPU usage
                    Thread.Sleep(10);
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Socket error: {e.Message}");
        }
    }

    void GetAndPrintMessage(NetworkStream stream) {
        byte[] buffer = new byte[1024];
        int bytesRead = stream.Read(buffer, 0, buffer.Length);
        string response = Encoding.UTF8.GetString(buffer, 0, bytesRead);
        Debug.Log($"Response from Python: {response}");
        if (int.TryParse(response, out _)) {
            decision = int.Parse(response);
        }
    }


    void OnApplicationQuit()
    {
        // Stop the thread when the application quits
        isRunning = false;
        if (socketThread != null && socketThread.IsAlive)
        {
            socketThread.Abort();
        }
    }
}
