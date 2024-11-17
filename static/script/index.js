document.addEventListener("DOMContentLoaded", () => {
  // Get the current pathname from the URL
  const currentPath = window.location.pathname;

  // Find all nav links
  const navLinks = document.querySelectorAll(".navbar .nav-link");

  // Iterate through each link and check if it matches the current path
  navLinks.forEach((link) => {
    if (currentPath.includes(link.getAttribute("href"))) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
});

function showNotification(message, type = "success") {
  const notification = document.getElementById("notification");

  if (notification) {
    // Set the content of the notification
    notification.textContent = message;

    // Remove any previous type classes (success, error) before adding the new one
    notification.classList.remove("success", "error");

    // Add the correct type class (success or error)
    notification.classList.add(type); // Add success or error class

    // Make the notification visible
    notification.classList.add("show");

    // Automatically hide the notification after 3 seconds
    setTimeout(() => {
      notification.classList.remove("show");
      notification.classList.add("hidden");
    }, 3000);
  } else {
    console.error("Notification container not found.");
  }
}

window.showNotification = showNotification;
