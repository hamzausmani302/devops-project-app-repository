// Product page script
console.log(window.__ENV__["CATALOG_SERVICE_URL"]);
const CATALOG_SERVICE_URL = window.__ENV__["CATALOG_SERVICE_URL"];

function getAuthToken() {
  return localStorage.getItem("auth_token");
}

function getQueryParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

async function fetchProducts() {
  const resp = await fetch(`${CATALOG_SERVICE_URL}/products`, {
    headers: {
      Authorization: getAuthToken(),
    },
  });
  if (!resp.ok) throw new Error("Failed to load products");
  return resp.json();
}

function showMessage(type, text) {
  const el = document.getElementById("message");
  el.className = "message " + (type === "success" ? "success" : "error");
  el.textContent = text;
  el.style.display = "block";
}

async function createOrder(product, quantity) {
  const token = getAuthToken();
  const body = { product, quantity };
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const resp = await fetch(`${CATALOG_SERVICE_URL}/order`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.detail || "Order creation failed");
  }

  return resp.json();
}

async function init() {
  try {
    const index = Number(getQueryParam("index") || 0);
    const products = await fetchProducts();
    if (!products || products.length === 0) {
      document.getElementById("productName").textContent =
        "No products available";
      return;
    }
    const product = products[index];
    if (!product) {
      document.getElementById("productName").textContent = "Product not found";
      return;
    }

    document.getElementById("productName").textContent =
      product.name || "Product";
    document.getElementById("productPrice").textContent =
      (product.currency ? product.currency + " " : "") +
      (product.price || "N/A");
    document.getElementById("productDesc").textContent =
      product.description || "";

    const user = JSON.parse(localStorage.getItem("user_info") || "null");
    if (user && user.email) {
      document.getElementById("userInfo").textContent = user.email;
    }

    document
      .getElementById("generateBtn")
      .addEventListener("click", async () => {
        const qty = Number(document.getElementById("qty").value) || 1;
        try {
          const result = await createOrder(product, qty);
          showMessage(
            "success",
            "Order created — ID: " + (result.id || result.orderId || "unknown")
          );
        } catch (err) {
          showMessage("error", err.message);
        }
      });
  } catch (err) {
    showMessage("error", err.message);
  }
}

window.addEventListener("DOMContentLoaded", init);
