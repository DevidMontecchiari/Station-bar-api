// Both pages load this exact file. Styling does not save an order.
const form = document.querySelector('#order-form');
const result = document.querySelector('#result');
const select = document.querySelector('#item');
const menuView = document.querySelector('#menu');
const submit = document.querySelector('#submit');

function show(message, error = false) {
  result.textContent = message;
  result.classList.toggle('error', error);
}

function renderMenu(items) {
  menuView.replaceChildren();
  select.replaceChildren();
  for (const item of items) {
    const row = document.createElement('div');
    row.className = 'menu-row';
    const name = document.createElement('span');
    name.textContent = item.name;
    const price = document.createElement('span');
    price.textContent = `${item.currency} ${Number(item.price).toFixed(2)}${item.available ? '' : ' — unavailable'}`;
    row.append(name, price);
    menuView.append(row);
    if (item.available) {
      const option = document.createElement('option');
      option.value = item.id;
      option.textContent = item.name;
      select.append(option);
    }
  }
  submit.disabled = select.options.length === 0;
}

function orderInput() {
  return {table: Number(form.elements.table.value), items: [{
    menu_item_id: Number(select.value),
    quantity: Number(form.elements.quantity.value)
  }]};
}

// Local fixture script allows double-click/file:// use without a server or fetch.
renderMenu(window.STATION_BAR_MENU);
let nextId = 12; // Fictional prototype IDs, never backend IDs.
form.addEventListener('submit', event => {
  event.preventDefault();
  const order = orderInput();
  show(`SIMULATED order ${nextId++}: table ${order.table}, quantity ${order.items[0].quantity}. Reload clears this result.`);
});
