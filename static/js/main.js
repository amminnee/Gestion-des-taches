document.addEventListener("DOMContentLoaded", function() {
    const scrollableDiv = document.getElementById("message-container");
    
    // Scroll the div to the bottom on page load or refresh
    scrollableDiv.scrollTop = scrollableDiv.scrollHeight;
});


