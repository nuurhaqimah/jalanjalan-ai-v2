/**
 * JalanJalan.AI — shared modal utility
 * Replaces browser confirm() and alert() with styled modals.
 *
 * Usage:
 *   jjConfirm({ title, message, confirmText, danger }, onConfirm)
 *   jjAlert({ title, message, icon })
 */

(function () {
  // Build overlay once, reuse it
  function getOrCreateOverlay() {
    let el = document.getElementById('jjModalOverlay');
    if (el) return el;

    el = document.createElement('div');
    el.id = 'jjModalOverlay';
    el.className = 'jj-overlay';
    el.innerHTML = `
      <div class="jj-modal" role="dialog" aria-modal="true">
        <div class="jj-modal-icon" id="jjModalIcon"></div>
        <div class="jj-modal-title" id="jjModalTitle"></div>
        <p  class="jj-modal-msg"   id="jjModalMsg"></p>
        <div class="jj-modal-actions" id="jjModalActions"></div>
      </div>`;
    document.body.appendChild(el);

    // Close on backdrop click
    el.addEventListener('click', (e) => {
      if (e.target === el) closeModal();
    });
    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && el.classList.contains('jj-open')) closeModal();
    });
    return el;
  }

  function openModal() {
    const el = document.getElementById('jjModalOverlay');
    // Force reflow so the enter transition fires
    el.offsetHeight;
    el.classList.add('jj-open');
  }

  function closeModal() {
    const el = document.getElementById('jjModalOverlay');
    if (el) el.classList.remove('jj-open');
  }

  /**
   * Show a confirm dialog.
   * @param {object} opts  { title, message, confirmText, cancelText, danger, icon }
   * @param {function} onConfirm  Called when user clicks the confirm button.
   */
  window.jjConfirm = function (opts, onConfirm) {
    opts = Object.assign({
      title:       'Are you sure?',
      message:     '',
      confirmText: 'Confirm',
      cancelText:  'Cancel',
      danger:      false,
      icon:        opts && opts.danger ? '🗑️' : '❓',
    }, opts);

    const overlay = getOrCreateOverlay();
    document.getElementById('jjModalIcon').textContent  = opts.icon;
    document.getElementById('jjModalTitle').textContent = opts.title;
    document.getElementById('jjModalMsg').textContent   = opts.message;

    const actions = document.getElementById('jjModalActions');
    actions.innerHTML = '';

    const confirmBtn = document.createElement('button');
    confirmBtn.className = 'jj-btn-confirm' + (opts.danger ? ' danger' : '');
    confirmBtn.textContent = opts.confirmText;
    confirmBtn.addEventListener('click', () => {
      closeModal();
      if (typeof onConfirm === 'function') onConfirm();
    });

    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'jj-btn-cancel';
    cancelBtn.textContent = opts.cancelText;
    cancelBtn.addEventListener('click', closeModal);

    actions.appendChild(confirmBtn);
    actions.appendChild(cancelBtn);

    openModal();
  };

  /**
   * Show an info / error alert.
   * @param {object} opts  { title, message, icon, btnText }
   */
  window.jjAlert = function (opts) {
    opts = Object.assign({
      title:   'Notice',
      message: '',
      icon:    'ℹ️',
      btnText: 'OK',
    }, opts);

    const overlay = getOrCreateOverlay();
    document.getElementById('jjModalIcon').textContent  = opts.icon;
    document.getElementById('jjModalTitle').textContent = opts.title;
    document.getElementById('jjModalMsg').textContent   = opts.message;

    const actions = document.getElementById('jjModalActions');
    actions.innerHTML = '';

    const okBtn = document.createElement('button');
    okBtn.className = 'jj-btn-confirm';
    okBtn.textContent = opts.btnText;
    okBtn.addEventListener('click', closeModal);
    actions.appendChild(okBtn);

    openModal();
  };
})();
