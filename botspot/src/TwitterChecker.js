import { useState } from "react";
import "./styles.css";

export default function TwitterChecker() {
  const [username, setUsername] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const checkTwitterAccount = async () => {
    if (!username) return;
    
    setLoading(true);
    setResult(null); // Reset previous results

    try {
      const response = await fetch("http://127.0.0.1:5000/analyze_twitter_bot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch Twitter account details");
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error fetching account details:", error);
      setResult({ error: "Failed to fetch account details." });
    } finally {
      setLoading(false);
    }
  };

  // Function to apply bold styling dynamically
  const formatAnalysisText = (text) => {
    if (!text) return ""; 

    return text.split("\n").map((line, index) => (
      <p key={index} dangerouslySetInnerHTML={{ 
        __html: line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      }}></p>
    ));
  };

  return (
    <div className="container">
      <div className="card">
        <h1 className="title">Twitter Fake Account Checker</h1>
        
        {/* Input for Username */}
        <input 
          type="text" 
          placeholder="Enter Twitter username..." 
          value={username} 
          onChange={(e) => setUsername(e.target.value)} 
          className="input-box"
        />
        
        {/* Check Button */}
        <button 
          onClick={checkTwitterAccount} 
          className="check-button"
          disabled={loading} // Disable button when loading
        >
          {loading ? "Checking..." : "Check Account"}
        </button>

        {/* Display Result */}
        {result && (
          <div className="result">
            {result.error ? (
              <p className="error">{result.error}</p>
            ) : (
              <div className="account-details">
                <h2>🔍 Twitter Account Analysis</h2>
                <hr />
                <p><strong>Username:</strong> {result.username}</p>
                <p><strong>Follower Count:</strong> {result.follower_count}</p>
                <p><strong>Verified:</strong> {result.is_verified ? "✅ Yes" : "❌ No"}</p>
                <p><strong>Verification Type:</strong> {result.verified_type || "N/A"}</p>
                <p>
                <strong>Visit Profile:</strong> 
                <a href={`https://x.com/${result.username}`} target="_blank" rel="noopener noreferrer">
                    {` x.com/${result.username}`}
                </a>
                </p>
                <h3>📊 Analysis:</h3>
                <div className="analysis-content">
                  {formatAnalysisText(result.analysis)}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
