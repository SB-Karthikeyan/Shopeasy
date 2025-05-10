// Cart Array
let cart = [];
loadCart();

window.addEventListener("load", function(){
    setTimeout(function(){
        document.getElementById("preloader-page").style.display = "none";
    }, 1000);
});

// Clear cart items on button click
document.getElementById('clear-cart').addEventListener('click', () => {
    cart = [];
    localStorage.clear();
    renderCart();

    fetch('/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: [] })
    })
    .then(response => response.json())
    .then(result => console.log('Server cart cleared:', result))
    .catch(error => console.error('Error clearing server cart:', error)); 
});


// Index page user icon function
let userIcon = document.querySelector('.user-icon');
let option = document.querySelector('.option');
userIcon.addEventListener('click',()=>{
    if(option.style.maxHeight == '200px'){
        option.style.maxHeight = '0px';
        option.style.visibility = 'hidden';
    }
    else{
        option.style.maxHeight = '200px';
        option.style.visibility = 'visible';
    }
});

// Function to fetch products
let productContainer = document.getElementById('products-container');
fetch('/api/products')
.then(response => response.json())
.then(data => {
    const products = data.products;
    const userStatus = data.user_status;

    productContainer.innerHTML = '';
    products.forEach(product => {

        let actionHTML = (userStatus === 'admin')
        ? `<a href="/update_product/${product.id}" tabindex="-1"><i class="fa-solid fa-pen-fancy update-product"></i></a>
            <div class="delete">
                <i class="fa-solid fa-trash remove-product delete-product"></i>
                <div class="confirm-box">
                    <p>Are you sure you want to delete the product?<br>Once done, it cannot be recoverd.</p>
                    <i class="option no">No</i>
                    <a tabindex="-1"  href="/delete_product/${product.id}" class="option yes">Yes</a>
                </div>
            </div>`
        : `<a tabindex="-1" class="add-to-cart-icon fa-solid fa-cart-shopping" onclick="addToCart(${product.id}, '${product.name}', '${product.image_url}', ${product.price})"></a>`;

        let productHTML = `
        <div class="product ${product.stock} ${product.product_type}">
            <a href="/templates/product-details/${product.name}" class="product-details">
                <div class="product-image">
                    <img src="${product.image_url}" alt="${product.name}"/>
                </div>
                <i class="category" style="display:none;">${product.category}</i>
                <i class="stock" style="display:none;">${product.stock}</i>
                <h3>${product.name}</h3>
                <b class="price">Rs.${product.price}</b>
                <p class="mrp">MRP:<span>${product.mrp}</span></p>
                <p class="rating" id="rating-${product.id}"></p>
                <p class="ratingText" style="display:none">${product.rating}</p>
                <p class="type">${product.product_type}</p> 
            </a>
          ${actionHTML} 
        </div>`;
        productContainer.innerHTML += productHTML;
    });

    products.forEach(product => {
        displayStars(product.rating, `rating-${product.id}`);
    });

    document.querySelectorAll('.remove-product').forEach(remove => {
        remove.addEventListener('click', (e) => {
            e.preventDefault();
            const confirmBox = remove.nextElementSibling;
            confirmBox.style.transform = 'translateX(0%)';
        });
    });
    
    document.querySelectorAll('.no').forEach(no => {
        no.addEventListener('click', (e) => {
            e.preventDefault();
            const confirmBox = no.closest('.confirm-box');
            confirmBox.style.transform = 'translateX(110%)';
        });
    });    
    

}).catch(error => console.error("Error fetching products: ", error));

// Rating
function displayStars(rating, elementId) {
    let html = "";
    for (let i = 1; i <= 5; i++) {
        if (i <= Math.floor(rating)) {
        html += '<i class="fas fa-star" style="color: gold;"></i>'; // Full star
        } else if (i - 0.5 <= rating) {
        html += '<i class="fas fa-star-half-alt" style="color: gold;"></i>'; // Half star
        } else {
        html += '<i class="far fa-star" style="color: gray;"></i>'; // Empty star
        }
    }
    document.getElementById(elementId).innerHTML = html;
};

// Cart count
    let count = 0;
    let cartCount = document.getElementById('cart-product-count');

    // Function to render cart items
    function renderCart() {
        const cartContainer = document.getElementById('cart-products');
        cartContainer.innerHTML = cart.length == 0 ? '<div class="cart-msg"><i class="fa-solid fa-cart-shopping"></i><p>Cart is Empty !!</p></div>' : '';
        cart.forEach(item => {
            const cartProduct = `
            <div class="product">
                <div class="image">
                    <img src="${item.url}" alt="${item.name}"/>
                </div>
                <div class="details">
                    <p>${item.name}</p>
                    <p>Price: Rs.${item.price}</p>
                    <div class="quantity">
                        <i onclick="subtractOne(${item.id})" class="fa-solid fa-minus minus"></i>
                        <p id="quantity-${item.id}">${item.quantity}</p>
                        <i onclick="addOne(${item.id})" class="fa-solid fa-plus plus"></i>
                    </div>
                </div>
            </div>`;
            cartContainer.innerHTML += cartProduct;
        });
        count = 0;
        cart.forEach(item =>{
            count += item.quantity;
        })
        cartCount.textContent = count;
    };


// Function to add product to cart
function addToCart(id, name, url, price) {
    id = parseInt(id);
    price = parseInt(price);
    let existingItem = cart.find(item => item.id === id);
    if (existingItem) {
        existingItem.quantity++;
    } else {
        cart.push({ id, name, url, price, quantity: 1 });
    }
    localStorage.setItem("cart-items", JSON.stringify(cart));
    renderCart();
};

// Increase quantity of a product in cart
function addOne(productId) {
    let item = cart.find(product => product.id === productId);
    if (item) {
        item.quantity++;
        document.getElementById(`quantity-${productId}`).innerText = item.quantity;
        localStorage.setItem("cart-items", JSON.stringify(cart));
        renderCart();
    }
};

// Decrease quantity or remove from cart
function subtractOne(productId) {
    let item = cart.find(product => product.id === productId);
    if (item) {
        item.quantity--;
        if (item.quantity <= 0) {
            cart = cart.filter(product => product.id !== productId);
        }
        localStorage.setItem("cart-items", JSON.stringify(cart));
        renderCart();
    }
};

// Cart and Filter section Open & Close functionality
let cartIcon = document.getElementById('header-cart-icon');
let filterIcon = document.getElementById('filter-icon');

if (cartIcon) {
    cartIcon.addEventListener('click', () => {
        document.getElementById('cart-section').style.right = '0%';
        document.getElementById('cart-section').style.zIndex = '1000';
        document.getElementById('filter-section').style.zIndex = '999';
    });
};

if (filterIcon) {
    filterIcon.addEventListener('click', () => {
        document.getElementById('filter-section').style.right = '0%';
        document.getElementById('filter-section').style.zIndex = '1000';
        document.getElementById('cart-section').style.zIndex = '999';
    });
};

document.querySelectorAll('.fa-close').forEach(close => {
    close.addEventListener('click', (event) => {
        let parentSection = event.target.closest('.cart-section, .filter-section');
        if (parentSection) {
            parentSection.style.right = '-100%';
        }
    });
});

// Search bar functionality
let searchContainer = document.getElementById('search-container');
let searchIcon = document.getElementById('searchIcon');
const searchInput = document.getElementById("searchInput");

searchIcon.addEventListener('click',()=>{
    searchContainer.classList.toggle('active');
    if(searchContainer.classList.contains('active')){
        searchInput.focus();
    }
});
searchIcon.addEventListener('keypress',()=>{
    if (event.key === "Enter") {
        searchContainer.classList.toggle('active');
        if(searchContainer.classList.contains('active')){
            searchInput.focus();
        }
    }
});

let productFilterOption = [];
let categoryFilterOption = [];
let stockFilterOption = [];
let ratingFilterOption = [];
let priceFilterOption = [];

const notFoundMessage = document.getElementById("no-result-msg");
const notFoundFilterMessage = document.getElementById("no-filter-result-msg");

function searchProducts() {
    let input = searchInput.value.toLowerCase();
    let products = document.querySelectorAll(".product");
    let found = false;

    products.forEach(product => {
        let text = product.querySelector("h3").innerText.toLowerCase();
        let match = text.includes(input);

        product.style.display = match ? "block" : "none";
        product.classList.toggle("hidden", !match);
        if(match){
            found = true;
        }
    });

    notFoundMessage.style.display = found ? "none" : "block";
}

function filterProducts() {
    let products = document.querySelectorAll('.product');
    let input = searchInput.value.toLowerCase();
    let filterFound = false;

    products.forEach(product => {
        let text = product.querySelector("h3").innerText.toLowerCase();
        let type = product.querySelector(".type").textContent.toLowerCase();
        let category = product.querySelector(".category").textContent.toLowerCase();
        let stock = product.querySelector(".stock").textContent.toLowerCase();

        let ratingText = product.querySelector(".ratingText").textContent.trim();
        let rating = parseFloat(ratingText);
        if (isNaN(rating)) rating = 0;

        let priceText = product.querySelector(".price")?.textContent.replace(/[^\d]/g, "") || "0";
        let price = parseInt(priceText, 10);
        

        let typeMatch = !productFilterOption.length || productFilterOption.includes(type);
        let categoryMatch = !categoryFilterOption.length || categoryFilterOption.includes(category);
        let stockMatch = !stockFilterOption.length || stockFilterOption.includes(stock);
        let searchMatch = text.includes(input);

        let ratingMatch = !ratingFilterOption.length || ratingFilterOption.some(option => {
            let minRating = parseInt(option);
            return rating >= minRating;
        });

        let priceMatch = !priceFilterOption.length || priceFilterOption.some(option => {
            switch (option) {
                case "15000 and above":
                    return price > 15000
                case "10000 - 15000":
                    return price >= 10000 && price <= 15000;
                case "8000 - 10000":
                    return price >= 8000 && price <= 10000;
                case "5000 - 8000":
                    return price >= 5000 && price <= 8000;
                case "1000 - 5000":
                    return price >= 1000 && price <= 5000;
                case "1000 and below":
                    return price < 1000;
                default:
                    break;
            }
        });

        let show = typeMatch && categoryMatch && stockMatch && searchMatch && ratingMatch && priceMatch;
        product.style.display = show ? "block" : "none";
        product.classList.toggle("hidden", !show);

        if(show){
            filterFound = true;
        }
    });

    notFoundFilterMessage.style.display = filterFound ? "none" : "block";
}

function handleCheckboxFilter(filterArray, label) {
    let checkbox = label.querySelector('input[type="checkbox"]');
    let text = label.querySelector('p').textContent.trim().toLowerCase();

    label.addEventListener("click", (event) => {
        if (event.target.tagName === "P") {
            event.stopPropagation();
            return;
        }

        checkbox.checked = !checkbox.checked;
        let index = filterArray.indexOf(text);

        if (checkbox.checked && index === -1) {
            filterArray.push(text);
        } else if (!checkbox.checked && index !== -1) {
            filterArray.splice(index, 1);
        }

        filterProducts();
    });
}

// Apply event listeners to filter checkboxes
document.querySelectorAll(".filter-by-type .custom-checkbox").forEach(label => handleCheckboxFilter(productFilterOption, label));
document.querySelectorAll(".filter-by-category .custom-checkbox").forEach(label => handleCheckboxFilter(categoryFilterOption, label));
document.querySelectorAll(".filter-by-stock .custom-checkbox").forEach(label => handleCheckboxFilter(stockFilterOption, label));
document.querySelectorAll(".filter-by-rating .custom-checkbox").forEach(label => handleCheckboxFilter(ratingFilterOption, label));
document.querySelectorAll(".filter-by-price .custom-checkbox").forEach(label => handleCheckboxFilter(priceFilterOption, label));

// Search bar event listener
searchInput.addEventListener("input", () => {
        searchProducts();
});

document.addEventListener('click', function (e) {
    const target = e.target;
    if (target.classList.contains('add-to-cart-icon') ||
        target.classList.contains('minus') ||
        target.classList.contains('plus')) 
    {
        syncCart();
    }
});

function syncCart() {
    fetch('/session/data')
    .then(response => response.json())
    .then(session => {
        console.log(session);
         if (session.logged_in) {
            let cartItems = localStorage.getItem("cart-items");
            console.log(cartItems);
                if (cartItems) {
                    try {
                        const parsedItems = JSON.parse(cartItems);
                        fetch('/cart', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ data: parsedItems })
                        })
                        .then(response => response.json())
                        .then(result => console.log('Data Saved:', result))
                        .catch(error => console.error('Error saving cart:', error));
                        localStorage.clear();
                    } catch (e) {
                        console.error("Error parsing cart-items:", e);
                    }
                }
            }
        })
    }

async function loadCart() {
    try {
        const sessionResponse = await fetch('/session/data');
        const session = await sessionResponse.json();

        if (session.logged_in) {
            try {
                const cartResponse = await fetch('/api/cart/products');
                const serverCart = await cartResponse.json();
                cart = serverCart.map(item => ({
                    id: item.id,
                    name: item.name,
                    price: item.price,
                    url: item.image_url,
                    quantity: item.quantity
                }));
                renderCart();
            } catch (err) {
                console.error('Failed to load server cart:', err);
            }
        } else {
            const storedCart = localStorage.getItem('cart-items');
            cart = storedCart ? JSON.parse(storedCart) : [];
            renderCart();
        }
    } catch (err) {
        console.error('Session check failed:', err);
    }
}