using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using System.Threading;
using System.Globalization;

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

    Vector3 positionOnset = Vector3.zero;
    OnsetFeatures onsetfeature = OnsetFeatures.zero();

    //Delegates
    public delegate void ChromaFeatureRecieved(ChromaFeature chromaFeature);
    public static ChromaFeatureRecieved onChromaFeatureRecieved;

    //delegates with onset
    public delegate void OnsetFeaturesRecieved(OnsetFeatures onsetFeatures);
    public static OnsetFeaturesRecieved OnsetFeatureRecieved;

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
        if (!string.IsNullOrEmpty(dataReceived))
        {
            Debug.Log($"Received: {dataReceived}");

            if (dataReceived.StartsWith("C,"))
            {
                // Chroma feature message
                chromaFeature = ParseChromaFeature(dataReceived.Substring(2)); // Remove "C," prefix
                Debug.Log(chromaFeature.ToString());
                onChromaFeatureRecieved?.Invoke(chromaFeature);
            }
            else if (dataReceived.StartsWith("O,"))
            {
                OnsetFeatures onsetFeature = ParseConsetFeatures(dataReceived.Substring(2)); // Remove "O," prefix
                Debug.Log(onsetFeature.ToString());
                OnsetFeatureRecieved?.Invoke(onsetFeature);
            }

            // Send back acknowledgment
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
            float.Parse(stringArray[0], CultureInfo.InvariantCulture),
            float.Parse(stringArray[1], CultureInfo.InvariantCulture),
            float.Parse(stringArray[2], CultureInfo.InvariantCulture),
            float.Parse(stringArray[3], CultureInfo.InvariantCulture),
            float.Parse(stringArray[4], CultureInfo.InvariantCulture),
            float.Parse(stringArray[5], CultureInfo.InvariantCulture),
            float.Parse(stringArray[6], CultureInfo.InvariantCulture),
            float.Parse(stringArray[7], CultureInfo.InvariantCulture),
            float.Parse(stringArray[8], CultureInfo.InvariantCulture),
            float.Parse(stringArray[9], CultureInfo.InvariantCulture),
            float.Parse(stringArray[10], CultureInfo.InvariantCulture),
            float.Parse(stringArray[11], CultureInfo.InvariantCulture));

        return chromaFeature;
    }

    public static OnsetFeatures ParseConsetFeatures(string dataString)
    {
        Debug.Log(dataString);
        if (dataString.StartsWith("(") && dataString.EndsWith(")"))
        {
            dataString = dataString.Substring(1, dataString.Length - 2);
        }

        string[] stringArray = dataString.Split(',');

        OnsetFeatures onsetFeatures = new OnsetFeatures(
            float.Parse(stringArray[0], CultureInfo.InvariantCulture)
            
        );

        return onsetFeatures;  
    }
}