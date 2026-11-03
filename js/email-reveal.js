document.querySelectorAll('.email-reveal').forEach(root => {
  const trigger = root.querySelector('.email-trigger');
  const address = root.querySelector('.email-address');
  trigger.addEventListener('click', () => {
    const email = atob(root.dataset.address);
    const separator = email.lastIndexOf('@');
    const domain = document.createElement('span');
    domain.className = 'email-domain';
    domain.textContent = email.slice(separator + 1);
    address.replaceChildren(document.createTextNode(email.slice(0, separator + 1)), document.createElement('wbr'), domain);
    address.href = 'mailto:' + email;
    address.hidden = false;
    trigger.hidden = true;
    address.focus();
  });
});
