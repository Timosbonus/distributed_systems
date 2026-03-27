const API_URL = "http://localhost:8000";

let products = [];
let cart = [];
let currentImageIndexes = {};

async function fetchProducts() {
  const loadingEl = document.getElementById("products-loading");
  const gridEl = document.getElementById("products-grid");

  try {
    const response = await fetch(`${API_URL}/products`);
    if (!response.ok) throw new Error("Failed to fetch products");
    products = await response.json();

    loadingEl.style.display = "none";
    renderProducts();
  } catch (error) {
    loadingEl.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
  }
}

function renderProducts() {
  const gridEl = document.getElementById("products-grid");

  if (products.length === 0) {
    gridEl.innerHTML =
      '<div class="error-message">No Pokemon available. Check back later!</div>';
    return;
  }

  products.forEach((product) => {
    if (!currentImageIndexes[product.id]) {
      currentImageIndexes[product.id] = 0;
    }
  });

  gridEl.innerHTML = products
    .map((product) => {
      const images =
        product.image_data && product.image_data.length > 0
          ? product.image_data
          : ["https://via.placeholder.com/280x200?text=No+Image"];
      const currentIndex = currentImageIndexes[product.id] || 0;
      const imageUrl = images[currentIndex];
      const hasMultipleImages = images.length > 1;

      const isInStock = product.quantity > 0;

      return `
      <div class="product-card" data-id="${product.id}">
        <div class="product-image-container">
          <img src="${imageUrl}" alt="${product.name}" class="product-image">
          ${
            hasMultipleImages
              ? `
            <button class="carousel-btn carousel-prev" onclick="changeImage(${product.id}, -1)">&#10094;</button>
            <button class="carousel-btn carousel-next" onclick="changeImage(${product.id}, 1)">&#10095;</button>
            <div class="carousel-dots">
              ${images
                .map(
                  (_, idx) => `
                <span class="carousel-dot ${idx === currentIndex ? "active" : ""}" onclick="setImage(${product.id}, ${idx})"></span>
              `,
                )
                .join("")}
            </div>
          `
              : ""
          }
        </div>
        <div class="product-info">
          <h3 class="product-name">${product.name}</h3>
          <p class="product-description">${product.description || "No description available"}</p>
          
          <div class="price-section">
            <div class="sell-price">
              €${product.sell_price ? product.sell_price.toFixed(2) : "N/A"}
            </div>
          </div>
          
          <div class="stock-status ${isInStock ? "in-stock" : "out-of-stock"}">
            ${isInStock ? `In Stock (${product.quantity} available)` : "Out of Stock"}
          </div>
          
          ${
            isInStock
              ? `
            <div class="quantity-section">
              <label>Qty:</label>
              <input type="number" class="quantity-input" value="1" min="1" max="${product.quantity}">
            </div>
            <button class="add-to-cart-btn" onclick="addToCart(${product.id})">
              Add to Cart
            </button>
          `
              : `
            <button class="add-to-cart-btn" disabled>
              Out of Stock
            </button>
          `
          }
        </div>
      </div>
    `;
    })
    .join("");
}

function changeImage(productId, direction) {
  const product = products.find((p) => p.id === productId);
  if (!product || !product.image_data || product.image_data.length <= 1) return;

  const images = product.image_data;
  let newIndex = currentImageIndexes[productId] + direction;

  if (newIndex < 0) newIndex = images.length - 1;
  if (newIndex >= images.length) newIndex = 0;

  currentImageIndexes[productId] = newIndex;
  renderProducts();
}

function setImage(productId, index) {
  const product = products.find((p) => p.id === productId);
  if (
    !product ||
    !product.image_data ||
    index < 0 ||
    index >= product.image_data.length
  )
    return;

  currentImageIndexes[productId] = index;
  renderProducts();
}

function addToCart(productId) {
  const product = products.find((p) => p.id === productId);
  if (!product) return;

  const card = document.querySelector(`.product-card[data-id="${productId}"]`);
  const qtyInput = card.querySelector(".quantity-input");
  const quantity = parseInt(qtyInput.value) || 1;

  const existingItem = cart.find((item) => item.id === productId);

  if (existingItem) {
    const newQty = existingItem.quantity + quantity;
    if (newQty > product.quantity) {
      showNotification("Cannot add more than available stock", "error");
      return;
    }
    existingItem.quantity = newQty;
  } else {
    cart.push({
      id: product.id,
      name: product.name,
      price: product.sell_price,
      quantity: Math.min(quantity, product.quantity),
    });
  }

  updateCartUI();
  showNotification(`${product.name} added to your team!`, "success");
}

function removeFromCart(productId) {
  cart = cart.filter((item) => item.id !== productId);
  updateCartUI();
}

function updateCartQuantity(productId, newQty) {
  const item = cart.find((i) => i.id === productId);
  const product = products.find((p) => p.id === productId);

  if (newQty <= 0) {
    removeFromCart(productId);
    return;
  }

  if (newQty > product.quantity) {
    showNotification("Cannot exceed available stock", "error");
    return;
  }

  item.quantity = newQty;
  updateCartUI();
}

function updateCartUI() {
  document.getElementById("cart-count").textContent = cart.reduce(
    (sum, item) => sum + item.quantity,
    0,
  );

  const cartItemsEl = document.getElementById("cart-items");

  if (cart.length === 0) {
    cartItemsEl.innerHTML =
      '<div class="empty-cart">Your cart is empty - start catching some Pokemon!</div>';
  } else {
    cartItemsEl.innerHTML = cart
      .map(
        (item) => `
      <div class="cart-item">
        <div class="cart-item-info">
          <h4>${item.name}</h4>
          <span>€${item.price.toFixed(2)} each</span>
        </div>
        <div class="cart-item-actions">
          <button onclick="updateCartQuantity(${item.id}, ${item.quantity - 1})">-</button>
          <span class="cart-item-qty">${item.quantity}</span>
          <button onclick="updateCartQuantity(${item.id}, ${item.quantity + 1})">+</button>
          <button onclick="removeFromCart(${item.id})">🗑️</button>
        </div>
      </div>
    `,
      )
      .join("");
  }

  const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  document.getElementById("cart-total").textContent = total.toFixed(2);
}

function toggleCart() {
  const modal = document.getElementById("cart-modal");
  modal.classList.toggle("hidden");
}

function showNotification(message, type = "success") {
  const notification = document.getElementById("notification");
  notification.textContent = message;
  notification.className = `notification ${type}`;

  setTimeout(() => {
    notification.classList.add("hidden");
  }, 3000);
}

function checkout() {
  if (cart.length === 0) {
    showNotification("Your cart is empty!", "error");
    return;
  }

  showNotification("Checkout successful! Thank you for your order!", "success");
  cart = [];
  updateCartUI();
  toggleCart();
}

document.getElementById("cart-btn").addEventListener("click", toggleCart);
document.getElementById("close-cart").addEventListener("click", toggleCart);
document.getElementById("checkout-btn").addEventListener("click", checkout);

document.getElementById("cart-modal").addEventListener("click", (e) => {
  if (e.target.id === "cart-modal") toggleCart();
});

fetchProducts();
