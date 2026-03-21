// Get catalog service URL from environment variable
const CATALOG_SERVICE_URL = window.__ENV__["CATALOG_SERVICE_URL"];
const VERSION_URL = window.__ENV__["VERSION_PATH"]

function getAuthToken() {
  const key = "auth_token";
  const token = localStorage.getItem(key);
  return token;
}

function getVersion(){
  fetch(VERSION_URL, {
    headers: {
      Authorization: getAuthToken(),
      "Access-Control-Allow-Origin": "*", 
    }
  })
  .then(response => response.text)
  .then((response) =>{
    document.getElementById("version-box").innerHTML = `
    <div>
      <h1>Version = </h1>
      <p> ${response}</p>
    </div>
    `
  })
}

function getProducts() {
  fetch(`${CATALOG_SERVICE_URL}/products`, {
    headers: {
      Authorization: getAuthToken(),
      "Access-Control-Allow-Origin": "*",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Products received:", data);
      displayProducts(data);
    })
    .catch((error) => console.error("Error fetching products:", error));
}

function displayProducts(products) {
  const productList = document.getElementById("products");
  if (!productList) {
    console.error("Products container not found");
    return;
  }

  productList.innerHTML = "";
  products.forEach((product) => {
    const idx = product["id"];
    const productElement = document.createElement("div");
    productElement.className = "product-item";
    productElement.innerHTML = `
      <h3>${product.name || "N/A"}</h3>
      <div class="price">${product.currency || ""} ${
      product.price || "N/A"
    }</div>
      <p>${product.description || "No description"}</p>
      <div style="margin-top:12px; display:flex; gap:8px;">
        <a class="btn" href="./product.html?index=${idx}">View</a>
      </div>
    `;
    productList.appendChild(productElement);
  });

  // Attach click handlers for quick generate buttons
  document.querySelectorAll(".generate-btn").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      const index = e.currentTarget.getAttribute("data-index");
      const product = products[Number(index)];
      try {
        await createOrder(product, 1);
        alert("Order created successfully");
      } catch (err) {
        alert("Failed to create order: " + err.message);
      }
    });
  });
}

async function createOrder(product, quantity = 1) {
  const token = getAuthToken();
  const body = {
    product: product,
    quantity: quantity,
  };

  const resp = await fetch(`${CATALOG_SERVICE_URL}/order`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.detail || "Order creation failed");
  }

  return resp.json();
}

// Fetch products on page load
document.addEventListener("DOMContentLoaded", getProducts);
