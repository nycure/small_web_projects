let hasDownloadedThisSession = false;


function downloadLinks(urls) {
  const text = urls.join('\n');
  const base64Data = btoa(unescape(encodeURIComponent(text)));
  const blobUrl = `data:text/plain;base64,${base64Data}`;

  chrome.downloads.download({
    url: blobUrl,
    filename: "video-links.txt",
    saveAs: false
  });
}


chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SAVE_URL") {
    const newUrl = message.videoUrl;

    chrome.storage.local.get({ savedUrls: [] }, (data) => {
      const urls = data.savedUrls;

      if (!urls.includes(newUrl)) {
        urls.push(newUrl);
        chrome.storage.local.set({ savedUrls: urls }, () => {
          if (!hasDownloadedThisSession) {
            downloadLinks(urls);
            hasDownloadedThisSession = true;
          }
        });
      }
    });

  } else if (message.type === "MANUAL_DOWNLOAD") {
    chrome.storage.local.get({ savedUrls: [] }, (data) => {
      if (data.savedUrls.length > 0) {
        downloadLinks(data.savedUrls);
      }
    });

  } else if (message.type === "RESET_LIST") {
    chrome.storage.local.set({ savedUrls: [] }, () => {
      hasDownloadedThisSession = false;
      sendResponse({ success: true });
    });
    return true;
  }
});
