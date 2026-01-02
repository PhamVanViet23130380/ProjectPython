document.addEventListener('DOMContentLoaded', function () {
  console.log('admin_payment.js loaded');
  // try multiple selectors to find the booking and amount fields used by admin
  let bookingSelect = document.getElementById('id_booking');
  if (!bookingSelect) bookingSelect = document.querySelector('select[name="booking"]') || document.querySelector('input[name="booking"]') || document.querySelector('[id^="id_booking"]');
  const amountInput = document.getElementById('id_amount') || document.querySelector('input[name="amount"]') || document.querySelector('[id^="id_amount"]');
  console.log('admin_payment: bookingSelect=', bookingSelect, 'amountInput=', amountInput);
  const warningElId = 'booking-amount-warning';

  function showWarning(text) {
    let w = document.getElementById(warningElId);
    if (!w) {
      w = document.createElement('div');
      w.id = warningElId;
      w.style.color = 'red';
      w.style.marginTop = '6px';
      amountInput.parentNode.appendChild(w);
    }
    w.textContent = text;
  }

  function clearWarning() {
    const w = document.getElementById(warningElId);
    if (w) w.textContent = '';
  }

  async function fetchTotal(bookingId) {
    try {
      // endpoint registered at /admin-api/... (app.urls is included at root)
      const url = `/admin-api/booking/${bookingId}/total/`;
      const res = await fetch(url, { credentials: 'same-origin' });
      if (!res.ok) {
        console.warn('admin_payment fetch error', res.status, await res.text());
        return null;
      }
      const data = await res.json();
      return data.total_price;
    } catch (e) {
      console.error('admin_payment fetch exception', e);
      return null;
    }
  }

  if (bookingSelect && amountInput) {
    bookingSelect.addEventListener('change', async function (e) {
      console.log('admin_payment: booking change event', e);
      const val = e.target.value || bookingSelect.value;
      console.log('admin_payment: booking id=', val);
      if (!val) return;
      const total = await fetchTotal(val);
      console.log('admin_payment: fetched total=', total);
      if (total !== null) {
        amountInput.value = total;
        clearWarning();
      }
    });

    // On load: if a booking is already selected (edit page), fetch and set amount
    (async function initFill() {
      try {
        const initial = bookingSelect && (bookingSelect.value || bookingSelect.getAttribute('value'));
        console.log('admin_payment init, initial booking=', initial);
        if (initial) {
          const total = await fetchTotal(initial);
          console.log('admin_payment init fetched total=', total);
          if (total !== null && amountInput && (!amountInput.value || amountInput.value === '')) {
            amountInput.value = total;
          }
        }
      } catch (err) {
        console.error('admin_payment init error', err);
      }
    })();

    // validate on amount input blur
    amountInput.addEventListener('blur', async function (e) {
      const bookingId = bookingSelect ? bookingSelect.value : null;
      if (!bookingId) return;
      const total = await fetchTotal(bookingId);
      if (total !== null && e.target.value && e.target.value !== total) {
        showWarning(`Amount should equal booking total: ${total}`);
      } else {
        clearWarning();
      }
    });
  }
});
