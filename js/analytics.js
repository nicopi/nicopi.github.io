/* Preserve the site's existing analytics integrations and page scope. */
(() => {
  if (document.body.hasAttribute('data-google-analytics')) {
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', 'G-H8WN74700N');
    const google = document.createElement('script');
    google.async = true;
    google.src = 'https://www.googletagmanager.com/gtag/js?id=G-H8WN74700N';
    document.head.append(google);
  }
  const clicky = document.createElement('script');
  clicky.async = true;
  clicky.src = 'https://static.getclicky.com/js';
  clicky.addEventListener('load', () => {
    if (window.clicky) window.clicky.init(101089699);
  });
  document.head.append(clicky);
})();
