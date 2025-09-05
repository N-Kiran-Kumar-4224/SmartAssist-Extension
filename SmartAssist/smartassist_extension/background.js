const NEWSAPI_KEY = "84274e937dd9486392b95a29b1b7338a";
const GOOGLE_API_KEY = "AIzaSyCCiZYGOnsVmDLC1_4AquCGwtIJ1TO1HAg";
const SEARCH_ENGINE_ID = "d6687f090ae8a4e2d";

async function googleSearch(query) {
  const url = `https://www.googleapis.com/customsearch/v1?key=${GOOGLE_API_KEY}&cx=${SEARCH_ENGINE_ID}&q=${encodeURIComponent(
    query
  )}`;
  const response = await fetch(url);
  const data = await response.json();
  return data.items || [];
}

async function newsApiSearch(query) {
  const url = `https://newsapi.org/v2/everything?q=${encodeURIComponent(
    query
  )}&apiKey=${NEWSAPI_KEY}`;
  const response = await fetch(url);
  const data = await response.json();
  return data.articles || [];
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "checkText") {
    (async () => {
      try {
        // Call your backend model API
        const modelResponse = await fetch("http://localhost:8000/check_text", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: request.text }),
        });
        const modelData = await modelResponse.json();

        // Return the backend response directly (already combined)
        sendResponse(modelData);
      } catch (error) {
        sendResponse({ error: error.toString() });
      }
    })();

    return true; // Keep message channel open for async response
  }
});
