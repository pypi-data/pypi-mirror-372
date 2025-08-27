let original_data = null;
const elhuyarTranslate = (selector, destination_language) => {
  let notranslates_html = [];
  const portal_url = document
    .querySelector("body")
    .getAttribute("data-portal-url");
  const lang = document.querySelector("html").getAttribute("lang");
  const content = document.querySelector(selector);
  const active = document.querySelector("button.elhuyar.active");
  const notranslates = document.querySelectorAll(".elhuyar-notranslate");
  notranslates.forEach((notranslate) =>
    notranslates_html.push(notranslate.getHTML())
  );
  if (!original_data) {
    original_data = content.getHTML();
  }
  if (active) {
    active.classList.remove("active");
  }
  if (original_data) {
    content.classList.add("elhuyar-loader-spinner");
    document
      .querySelector(`#elhuyar-translate-${destination_language}`)
      .classList.add("loading");
    postTranslation(`${portal_url}/@elhuyar-translator`, {
      language_pair: `${lang}-${destination_language}`,
      text: original_data,
    }).then((data) => {
      if (data.translated_text) {
        const current = document.querySelector(
          `#elhuyar-translate-${destination_language}`
        );
        content.innerHTML = data.translated_text;
        content.classList.remove("elhuyar-loader-spinner");
        current.classList.remove("loading");
        const notranslates = document.querySelectorAll(".elhuyar-notranslate");
        notranslates.forEach(
          (notranslate, i) => (notranslate.innerHTML = notranslates_html[i])
        );
        const current2 = document.querySelector(
          `#elhuyar-translate-${destination_language}`
        );
        current2.classList.add("active");
      } else {
        const current = document.querySelector(
          `#elhuyar-translate-${destination_language}`
        );
        content.classList.remove("elhuyar-loader-spinner");
        current.classList.remove("loading");
      }
    });
  }
};

async function postTranslation(url = "", data = {}) {
  const response = await fetch(url, {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(data),
  });
  if (response.ok) {
    return response.json();
  } else {
    console.error(response.status, response.statusText);
    return {};
  }
}
