// info.js

function showInfoPopup(info) {
    const popup = document.getElementById("infoPopup");
    const table = popup.querySelector(".info-table");
    table.innerHTML = ""; // clear previous
  
    for (const key in info) {
      const row = document.createElement("tr");
      const k = document.createElement("td");
      const v = document.createElement("td");
      k.textContent = prettifyKey(key);
      v.textContent = info[key];
      row.appendChild(k);
      row.appendChild(v);
      table.appendChild(row);
    }
  
    popup.classList.remove("hidden");
  }
  
  function hideInfoPopup() {
    const popup = document.getElementById("infoPopup");
    popup.classList.add("hidden");
  }
  
  function prettifyKey(key) {
    return key
      .replace(/_/g, " ")
      .replace(/\b\w/g, c => c.toUpperCase());
  }
  