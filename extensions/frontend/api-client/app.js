const form = document.querySelector('#order-form');
const result = document.querySelector('#result');
const select = document.querySelector('#item');
const submit = document.querySelector('#submit');
const menuView = document.querySelector('#menu');
const readback = document.querySelector('#readback');
function show(message, error = false) {
  result.textContent = message; // API text is text, not executable HTML.
  result.classList.toggle('error', error);
}
function renderMenu(items) {
  menuView.replaceChildren(); select.replaceChildren();
  for (const item of items) {
    const row = document.createElement('div'); row.className = 'menu-row';
    const name = document.createElement('span'); name.textContent = item.name;
    const price = document.createElement('span');
    price.textContent = `${item.currency} ${Number(item.price).toFixed(2)}${item.available ? '' : ' - unavailable'}`;
    row.append(name, price); menuView.append(row);
    if (item.available) {
      const option = document.createElement('option'); option.value = item.id;
      option.textContent = item.name; select.append(option);
    }
  }
  submit.disabled = select.options.length === 0;
  if (submit.disabled) show('No available menu items. Try again later.', true);
}
function orderInput() {
  return {table: Number(form.elements.table.value), items: [{
    menu_item_id: Number(select.value), quantity: Number(form.elements.quantity.value)
  }]};
}

async function request(path, options) {
  const response = await fetch('/api' + path, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.message || `Request failed (${response.status})`);
  return body;
}
submit.disabled = true;
request('/menu-items').then(renderMenu).catch(e => show(e.message, true));
form.addEventListener('submit', async event => {
  event.preventDefault();
  submit.disabled = true; readback.hidden = true;
  show('Sending order...');
  try {
    const order = await request('/orders', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(orderInput())
    });
    show(`Order ${order.id} received | table ${order.table} | status: ${order.status}`);
    readback.href = '/api/orders/' + encodeURIComponent(order.id);
    readback.hidden = false;
  } catch (error) {
    show(error.message + ' If the connection was interrupted, check saved orders before retrying.', true);
  } finally {
    submit.disabled = select.options.length === 0;
  }
});
