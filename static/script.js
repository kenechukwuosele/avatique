document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("waitlist-form");
  const messageDiv = document.getElementById("message");
  const submitBtn = form.querySelector('button[type="submit"]');

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Reset message
    messageDiv.classList.add("hidden");
    messageDiv.classList.remove("success", "error");

    // Loading state
    const originalBtnText = submitBtn.textContent;
    submitBtn.textContent = "Joining...";
    submitBtn.disabled = true;

    const formData = new FormData(form);

    try {
      const response = await fetch("/submit", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        // Success
        messageDiv.textContent = data.message;
        messageDiv.classList.add("success");
        messageDiv.classList.remove("hidden");
        form.reset();
      } else {
        // Error (client or server side handled)
        messageDiv.textContent = data.message || "Something went wrong.";
        messageDiv.classList.add("error");
        messageDiv.classList.remove("hidden");
      }
    } catch (error) {
      console.error("Error:", error);
      messageDiv.textContent = "Network error. Please try again.";
      messageDiv.classList.add("error");
      messageDiv.classList.remove("hidden");
    } finally {
      // Restore button
      submitBtn.textContent = originalBtnText;
      submitBtn.disabled = false;
    }
  });
});
