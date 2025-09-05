document.getElementById("checkButton").addEventListener("click", () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.tabs.sendMessage(
      tabs[0].id,
      { action: "getSelectedText" },
      (response) => {
        if (!response || !response.text) {
          document.getElementById("verdict").textContent =
            "⚠️ Please highlight some text first.";
          document.getElementById("confidence").textContent = "";
          document.getElementById("resultContainer").style.display = "block";
          return;
        }

        chrome.runtime.sendMessage(
          { action: "checkText", text: response.text },
          (result) => {
            if (result.error) {
              document.getElementById("verdict").textContent =
                "❌ Error contacting the backend or APIs.";
              document.getElementById("confidence").textContent = "";
            } else {
              document.getElementById(
                "verdict"
              ).textContent = `Verdict: ${result.verdict}`;
              document.getElementById(
                "confidence"
              ).textContent = `Confidence: ${result.confidence}`;
            }
            document.getElementById("resultContainer").style.display = "block";
          }
        );
      }
    );
  });
});
