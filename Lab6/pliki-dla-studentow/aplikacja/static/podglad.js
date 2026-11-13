// Zadanie 3: tekst z fragmentu adresu wstawiamy przez textContent (dane, nie HTML),
// a skrypt jest w osobnym pliku, zgodnym z CSP script-src 'self'.
document.getElementById("podglad").textContent =
  decodeURIComponent(location.hash.slice(1));
