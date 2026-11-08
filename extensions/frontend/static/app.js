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

// Only this local sample file is loaded. No request is sent to the business API.
submit.disabled = true;
fetch('/files/menu.json').then(r => { if (!r.ok) throw Error('Sample menu unavailable'); return r.json(); })
  .then(renderMenu).catch(e => show(e.message, true));
let nextId = 12; // Invented prototype IDs; these are not saved backend orders.
form.addEventListener('submit', event => {
  event.preventDefault();
  const order = orderInput();
  show(`SIMULATED order ${nextId++}: table ${order.table}, quantity ${order.items[0].quantity}. Reload clears this result.`);
});
