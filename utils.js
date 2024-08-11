function updateFavicon() {
    const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const favicon = document.getElementById('favicon');
    favicon.href = isDarkMode ? 'static/favicon-dark.png' : 'static/favicon-light.png';
}

    // Update the favicon on page load
    updateFavicon();

    // Update the favicon if the user changes the color scheme
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', updateFavicon);
