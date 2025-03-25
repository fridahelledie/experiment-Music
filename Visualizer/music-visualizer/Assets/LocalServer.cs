using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using System.Threading;

public class LocalServer : MonoBehaviour
{
    Thread thread;
    public int connectionPort = 25001;
    TcpListener server;
    TcpClient client;
    bool running;

    // Position is the data being received in this example
    Vector3 position = Vector3.zero;
    ChromaFeature chromaFeature = ChromaFeature.zero();

    //Delegates
    public delegate void ChromaFeatureRecieved(ChromaFeature chromaFeature);
    public static ChromaFeatureRecieved onChromaFeatureRecieved;

    void Start()
    {
        // Receive on a separate thread so Unity doesn't freeze waiting for data
        ThreadStart ts = new ThreadStart(GetData);
        thread = new Thread(ts);
        thread.Start();
    }

    private void OnDestroy()
    {
        thread.Abort();
    }

    void GetData()
    {
        // Create the server
        server = new TcpListener(IPAddress.Any, connectionPort);
        server.Start();

        // Create a client to get the data stream
        client = server.AcceptTcpClient();

        // Start listening
        running = true;
        while (running)
        {
            Connection();
        }
        server.Stop();
    }

    void Connection()
    {
        // Read data from the network stream
        NetworkStream nwStream = client.GetStream();
        byte[] buffer = new byte[client.ReceiveBufferSize];
        int bytesRead = nwStream.Read(buffer, 0, client.ReceiveBufferSize);

        // Decode the bytes into a string
        string dataReceived = Encoding.UTF8.GetString(buffer, 0, bytesRead);

        // Make sure we're not getting an empty string
        //dataReceived.Trim();
        if (dataReceived != null && dataReceived != "")
        {
            // Convert the received string of data to the format we are using
            chromaFeature = ParseChromaFeature(dataReceived);
            Debug.Log(chromaFeature.ToString());
            onChromaFeatureRecieved?.Invoke(chromaFeature); //Invokes the callback function to update the visualizer
            nwStream.Write(buffer, 0, bytesRead);
        }
    }

    //Parse date to a chroma feature
    public static ChromaFeature ParseChromaFeature(string dataString)
    {
        Debug.Log(dataString);
        // Remove the parentheses
        if (dataString.StartsWith("(") && dataString.EndsWith(")"))
        {
            dataString = dataString.Substring(1, dataString.Length - 2);
        }

        // Split the elements into an array
        string[] stringArray = dataString.Split(',');

        // Store as a Vector3
        ChromaFeature chromaFeature = new ChromaFeature(
            float.Parse(stringArray[0]),
            float.Parse(stringArray[1]),
            float.Parse(stringArray[2]),
            float.Parse(stringArray[3]),
            float.Parse(stringArray[4]),
            float.Parse(stringArray[5]),
            float.Parse(stringArray[6]),
            float.Parse(stringArray[7]),
            float.Parse(stringArray[8]),
            float.Parse(stringArray[9]),
            float.Parse(stringArray[10]),
            float.Parse(stringArray[11]));

        return chromaFeature;
    }
}