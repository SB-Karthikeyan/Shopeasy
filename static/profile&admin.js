document.querySelectorAll('.remove-account').forEach(remove => {
    remove.addEventListener('click', () => {
        document.querySelectorAll('.confirm-box').forEach(confirm => {
            confirm.style.scale = '1';
        });
    });
});

document.querySelectorAll('.no').forEach(no => {
    no.addEventListener('click', () => {
        document.querySelectorAll('.confirm-box').forEach(confirm => {
            confirm.style.scale = '0';
        });
    });
});


let passwordBlock = document.querySelector('.password');

document.querySelectorAll('.password-icon').forEach(container => {
    const input = container.querySelector('.password-field');
    const icon = container.querySelector('i');

    icon.addEventListener('click', () => {
        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
    });
});

let input = document.querySelectorAll('.password-field');
let button = document.querySelector('.btn');
document.querySelector('.fa-close').addEventListener('click', ()=>{
    passwordBlock.style.right = '-100%';
    input.forEach(input => input.setAttribute('tabindex', '-1'));
    button.setAttribute('tabindex', '-1');
});
document.querySelector('.password-text').addEventListener('click', ()=>{
    passwordBlock.style.right = '0%';
    input.forEach(input => input.setAttribute('tabindex', '0'));
    button.setAttribute('tabindex', '0');
});

function loadOrders(){
    fetch('/order-history')
    .then(response => response.json())
    .then(orders => {
        let orderHTML = '';
        if (orders.length === 0) {
            document.getElementById('order-container').innerHTML = '<p>No orders found.</p>';
            return;
        }
        orders.forEach(order => {
            const total = order.quantity * order.price;
            orderHTML += `
                <div class="products-ordered">
                    <div class="image-div">
                        <img src="${order.image}" alt="${order.name}"/>
                    </div>
                    <h3 class="text">${order.name}</h3>
                    <p class="text"><strong>Qty:</strong> ${order.quantity}</p>
                    <p class="text"><strong>Price:</strong> Rs.${order.price.toFixed(2)}</p>
                    <p class="text"><strong>Total:</strong> Rs.${total.toFixed(2)}</p>
                </div>
            `;
        });
        document.getElementById('order-container').innerHTML = orderHTML;
    })
    .catch(error => {
        document.getElementById('order-container').innerHTML = '<p>No orders found.</p>';
        console.error('Fetch error:', error);
    });
}
window.addEventListener('DOMContentLoaded',loadOrders);

const orderContainer = document.getElementById('order-container');
orderContainer.addEventListener('wheel', (evt) => {
    evt.preventDefault();
    orderContainer.scrollLeft += evt.deltaY * 10;
});