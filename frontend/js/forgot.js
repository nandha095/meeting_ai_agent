/****************************
 * SEND RESET LINK
 ****************************/
async function sendResetLink() {
  const email = document.getElementById("email").value;
  const messageEl = document.getElementById("message");

  if (!email) {
    messageEl.innerText = "❌ Please enter your email";
    return;
  }

  messageEl.innerText = "🤖 AI is sending reset link...";

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/auth/forgot-password",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email })
      }
    );

    const data = await response.json();

    if (response.ok) {
      messageEl.innerText =
        "✅ Reset link sent. Check your email inbox.";
    } else {
      messageEl.innerText = data.detail || "❌ Failed to send reset link";
    }
  } catch (err) {
    messageEl.innerText = "❌ Network error";
  }
}

/****************************
 * RESET PASSWORD
 ****************************/
async function resetPassword() {
  const password = document.getElementById("password").value;
  const messageEl = document.getElementById("message");

  // Get token from URL
  const params = new URLSearchParams(window.location.search);
  const token = params.get("token");

  if (!token || !password) {
    messageEl.innerText = "❌ Invalid reset request";
    return;
  }

  messageEl.innerText = "🤖 AI is resetting your password...";

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/auth/reset-password",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          token,
          new_password: password
        })
      }
    );

    const data = await response.json();

    if (response.ok) {
      messageEl.innerText =
        "✅ Password reset successful. You can now login.";
      setTimeout(() => {
        window.location.href = "index.html";
      }, 2000);
    } else {
      messageEl.innerText = data.detail || "❌ Reset failed";
    }
  } catch (err) {
    messageEl.innerText = "❌ Network error";
  }
}
