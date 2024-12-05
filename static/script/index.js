
function showNotification(message, type = "success") {
  const notification = document.getElementById("notification");

  if (notification) {
    // Set the content of the notification
    notification.textContent = message;

    // Remove any previous type classes (success, error) before adding the new one
    notification.classList.remove("success", "error");

    // Add the correct type class (success or error)
    notification.classList.add(type); // Add success or error class

    // Make the notification visible
    notification.classList.add("show");

    // Automatically hide the notification after 3 seconds
    setTimeout(() => {
      notification.classList.remove("show");
      notification.classList.add("hidden");
    }, 3000);
  } else {
    console.error("Notification container not found.");
  }
}

window.showNotification = showNotification;


const symbolsUrl = "http://127.0.0.1:8000/symbols"; // Endpoint to fetch symbols
const symbolSelect = document.getElementById("symbol-select");
const currentPriceDisplay = document.getElementById("currentPrice");
const ibSymbolInput = document.getElementById("ib-symbol");
const currentProfitDisplay = document.getElementById("currentProfit");
const payoutValueDisplay = document.getElementById("payoutValue");
const strikePriceInput = document.getElementById("strikePrice");
const amountToStakeInput = document.getElementById("amountToStake");
const daysToExpiryInput = document.getElementById("daysToExpiry");

let ws = null;

// Fetch available symbols and populate the dropdown
async function fetchSymbols() {
  try {
    const response = await fetch(symbolsUrl);
    const data = await response.json();
    const symbols = data.symbols;

    // Populate dropdown
    symbols.forEach(symbol => {
      const option = document.createElement("option");
      option.value = symbol.symbol;
      option.textContent = symbol.name;
      symbolSelect.appendChild(option);
    });
  } catch (error) {
    console.error("Error fetching symbols:", error);
  }
}

// Handle symbol selection and connect WebSocket
symbolSelect.addEventListener("change", (event) => {
  const selectedSymbol = event.target.value;

  if (ws) {
    ws.close(); // Close existing WebSocket connection
  }

  // Open a new WebSocket connection for the selected symbol
  ws = new WebSocket(`ws://127.0.0.1:8000/ws/ticks/${selectedSymbol}`);

  ws.onopen = () => {
    console.log(`Connected to WebSocket for ${selectedSymbol}`);
    currentPriceDisplay.textContent = `Fetching...`;
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // console.log(data)
    if (data.error) {
      console.error("Error:", data.error);
      currentPriceDisplay.textContent = `Error: ${data.error}`;
    } else {
      currentPriceDisplay.textContent = `${data.price}` || 0;
    }
  };

  ws.onerror = (error) => {
    console.error("WebSocket Error:", error);
  };

  ws.onclose = () => {
    console.log("WebSocket connection closed");
  };
});

async function getInputValue(action = "buy") {

  const symbol = symbolSelect.value;
  const currentPrice = parseFloat(currentPriceDisplay.textContent);
  const amountStaked = parseFloat(amountToStakeInput.value);
  const ibSymbol = ibSymbolInput.value;
  const strikePrice = parseFloat(strikePriceInput.value);
  const daysToExpiry = daysToExpiryInput.value
  const targetProfit = (currentPrice - strikePrice) * amountStaked;
  
  const tradeData = {
    symbol: symbol,
    ib_symbol :ibSymbol,
    strike: strikePrice,
    expiry: daysToExpiry,
    action: action,
    targetProfit:targetProfit,
    quantity: 1,
  };

  console.log(tradeData)


  try {
    const response = await fetch("/api/place-market-order", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tradeData),
    });
    const result = await response.json();

    
    showNotification(result.message);
    document.getElementById("tradeForm").reset();
  } catch (error) {
    showNotification("Failed to place trade: " + error.message, "error");
  }


}


function validateForm() {
  let isError = true;
  let error = []

  // Validate symbol selection
  if (!symbolSelect.value) {
    error.push('Please select a symbol.');
    isError = false;
  }

  // Validate Target Profit (USD) input
  if (!targetProfitInput.value || isNaN(targetProfitInput.value) || parseFloat(targetProfitInput.value) <= 0) {
    error.push('Please enter a valid target profit (greater than 0).');
    isError = false;
  }

  // Validate Amount to Stake (USD) input
  if (!amountToStakeInput.value || isNaN(amountToStakeInput.value) || parseFloat(amountToStakeInput.value) <= 0) {
    error.push('Please enter a valid amount to stake (greater than 0).');
    isError = false;
  }

  // Validate Strike Price input
  if (!strikePriceInput.value || isNaN(strikePriceInput.value) || parseFloat(strikePriceInput.value) <= 0) {
    error.push('Please enter a valid strike price (greater than 0).');
    isError = false;
  }

  // Validate Days to Expiry input
  if (!daysToExpiryInput.value || isNaN(daysToExpiryInput.value) || parseInt(daysToExpiryInput.value) < 1) {
    error.push('Please enter a valid number of days to expiry (greater than or equal to 1).');
    isError = false;
  }
  return { isError, error }
}



async function placeOrder(action) {
  console.log("placing order")
  
  const payload = await getInputValue(action)

}
// Event handler for Buy (Rise) button
document.getElementById("buyButton").addEventListener("click", async function (e) {
  e.preventDefault()
  await placeOrder("buy")

});

// Event handler for Sell (Fall) button
document.getElementById("sellButton").addEventListener("click", async function (e) {
  e.preventDefault()
  await placeOrder("sell")

});






window.addEventListener("load", fetchSymbols);
