document.getElementById("updateForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent page reload on form submit

    const output = document.getElementById("output");
    output.textContent = "⏳ Sending request...";

    // Collect form input values
    const formData = {
        superset_url: document.getElementById("superset_url").value,
        username: document.getElementById("username").value,
        password: document.getElementById("password").value,
        dashboard_id: document.getElementById("dashboard_id").value,
        old_id: document.getElementById("old_id").value,
        new_id: document.getElementById("new_id").value
    };

    try {
        // Send POST request to Flask backend
        const response = await fetch("/update", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(formData)
        });

        // Parse and display result
        const result = await response.json();
        if (response.ok) {
            output.textContent = "✅ Update complete:\n\n" + result.message;
        } else {
            output.textContent = "❌ Error:\n\n" + result.error;
        }
    } catch (error) {
        // Handle any JS or network errors
        output.textContent = "❌ Request failed:\n\n" + error;
    }
});
