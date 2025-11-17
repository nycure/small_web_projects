function saveUrlToStorage(url) {
  chrome.runtime.sendMessage({ type: "SAVE_URL", videoUrl: url });
}

const video = document.querySelector("video");
if (video) {
  video.addEventListener("play", () => {
    const currentUrl = window.location.href;
    saveUrlToStorage(currentUrl);
  });
}
