document.getElementById("download").addEventListener("click", () => {
  chrome.runtime.sendMessage({ type: "MANUAL_DOWNLOAD" });
});

document.getElementById("reset").addEventListener("click", () => {
  chrome.runtime.sendMessage({ type: "RESET_LIST" }, () => {
    alert("Saved video list has been reset.");
    updateCount(); // Refresh the counter after reset
  });
});

function updateCount() {
  chrome.storage.local.get({ savedUrls: [] }, (data) => {
    const count = data.savedUrls.length;
    document.getElementById("count").innerText = `Saved links: ${count}`;
  });
}

// Run on popup open
updateCount();
