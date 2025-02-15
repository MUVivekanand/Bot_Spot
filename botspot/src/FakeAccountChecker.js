import { useState } from "react";

export default function FakeAccountChecker() {
  const [username, setUsername] = useState("");
  const [platform, setPlatform] = useState("instagram"); // Default to Instagram
  const [result, setResult] = useState(null);

  const checkAccount = async () => {
    if (!username) return;

    const apiUrl = "http://127.0.0.1:5000/check";

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch account details");
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error fetching account details:", error);
    }
  };

  const openTwitterPage = () => {
    window.open("/twitter", "_blank");
  };

  return (
    <div>
      <h1 className="title">Instagram and Twitter Bot Detection</h1>
    <div style={{ textAlign: "center", fontFamily: "Arial, sans-serif", padding: "20px", background: "linear-gradient(to right, #1E3A8A, #2563EB)" }}>
      {/* Navbar */}
      
      <nav style={{ display: "flex", justifyContent: "center", alignItems: "center", marginBottom: "20px" }}>
        <button 
          style={{ padding: "10px 20px", margin: "0 10px", cursor: "pointer", backgroundColor: platform === "instagram" ? "#1E3A8A" : "#ccc", color: "white", border: "none", borderRadius: "5px" }}
          onClick={() => setPlatform("instagram")}
        >
          Instagram
        </button>
        <button 
          style={{ padding: "10px 20px", margin: "0 10px", cursor: "pointer", backgroundColor: "#1DA1F2", color: "white", border: "none", borderRadius: "5px" }}
          onClick={openTwitterPage}
        >
          Twitter
        </button>
      </nav>

      {platform === "instagram" && (
        <div style={{ maxWidth: "400px", margin: "0 auto", padding: "20px", border: "1px solid #ddd", borderRadius: "10px", boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)", background: "white" }}>
          <h1 style={{ fontSize: "20px", marginBottom: "10px", color: "#1E3A8A" }}>Instagram Fake Account Checker</h1>
          <input 
            type="text" 
            placeholder="Enter Instagram username..." 
            value={username} 
            onChange={(e) => setUsername(e.target.value)} 
            style={{ width: "80%", padding: "10px", marginBottom: "10px", borderRadius: "5px", border: "1px solid #ccc" }}
          />
          <button 
            onClick={checkAccount} 
            style={{ width: "80%", padding: "10px", backgroundColor: "#1E3A8A", color: "white", border: "none", borderRadius: "5px", cursor: "pointer" }}
          >
            Check Account
          </button>

          {result && (
            <div style={{ marginTop: "20px", textAlign: "left" }}>
              <img 
                src={result.profile_pic ? `http://127.0.0.1:5000/proxy-image?url=${encodeURIComponent(result.profile_pic)}` : "https://via.placeholder.com/150"} 
                alt="Profile" 
                style={{ width: "100px", height: "100px", borderRadius: "50%", display: "block", margin: "0 auto 10px" }} 
                onError={(e) => (e.target.src = "https://via.placeholder.com/150")} 
              />
              <p><strong>Username:</strong> {result.username}</p>
              <p><strong>User ID:</strong> {result.user_id}</p>
              <p><strong>Followers:</strong> {result.followers}</p>
              <p><strong>Following:</strong> {result.following}</p>
              <p><strong>Bio:</strong> {result.bio}</p>
              <p><strong>Private Account:</strong> {result.is_private ? "Yes" : "No"}</p>
              <p><strong>Posts:</strong> {result.post_count}</p>
              <br />
              <p><strong>Prediction:</strong> {result.prediction === "1" ? "Fake Account" : "Real Account"}</p>
              <p><strong>Probability of Being Fake:</strong> {result.prob}</p>
              <p><strong>Risks:</strong> {result.risks}</p>
            </div>
          )}
        </div>
      )}
    </div>
    </div>
  );
}