/****************************
 * GOOGLE CONNECT
 ****************************/
function connectGoogle() {
  const token = localStorage.getItem("token");

  if (!token) {
    alert("Please login first");
    window.location.href = "index.html";
    return;
  }

  // 🧠 AI status message
  const statusEl = document.getElementById("ai-status");
  if (statusEl) {
    statusEl.innerText = "🤖 Connecting to Google... AI preparing access";
  }

  // Redirect to backend Google OAuth
  window.location.href = "http://127.0.0.1:8000/auth/google/login";
}

/****************************
 * SEND PROPOSAL
 ****************************/
async function sendProposal() {
  const token = localStorage.getItem("token");

  if (!token) {
    alert("Please login first");
    return;
  }

  // 🧠 AI action message
  const actionEl = document.getElementById("ai-action");
  if (actionEl) {
    actionEl.innerText =
      "🧠 AI is sending proposal and will monitor replies automatically...";
  }

  const payload = {
    email: document.getElementById("to_email").value,
    subject: document.getElementById("subject").value,
    body: document.getElementById("body").value
  };

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/emails/emails/send-proposal",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      }
    );

    const data = await response.json();

    if (response.ok) {
      if (actionEl) {
        actionEl.innerText =
          "✅ Proposal sent. AI will read replies and schedule the meeting automatically.";
      }
    } else {
      if (actionEl) {
        actionEl.innerText = "❌ AI failed to send proposal.";
      }
      alert(data.detail || "Failed to send proposal");
    }
  } catch (error) {
    if (actionEl) {
      actionEl.innerText = "❌ Network error. AI could not reach server.";
    }
    alert("Network error");
  }
}

/****************************
 * CHECK GOOGLE CONNECTION STATUS
 ****************************/
async function checkGoogleStatus() {
  const token = localStorage.getItem("token");
  if (!token) return;

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/auth/google/status",
      {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      }
    );

    const data = await response.json();

    const statusEl = document.getElementById("ai-status");
    if (!statusEl) return;

    if (data.connected) {
      statusEl.innerText = "✅ Google connected — AI is active";
    } else {
      statusEl.innerText = "🔌 Google not connected";
    }
  } catch (error) {
    console.error("Failed to fetch Google status");
  }
}

/****************************
 * ON PAGE LOAD
 ****************************/
window.onload = () => {
  checkGoogleStatus();
};
