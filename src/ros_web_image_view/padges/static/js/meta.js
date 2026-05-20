async function updateMetaData() {
    try {
        const response = await fetch('/meta');
        const text = await response.text();
        document.getElementById('meta').innerText = text; 
    } catch (e) {
        console.log(e);
    }
}

setInterval(updateMetaData, 500);
updateMetaData();