import DerivAPIBasic from "https://cdn.skypack.dev/@deriv/deriv-api/dist/DerivAPIBasic";

const app_id = 53450;
const connection = new WebSocket(
  `wss://ws.derivws.com/websockets/v3?app_id=${app_id}`
);
const api = new DerivAPIBasic({ connection });

const active_symbols_request = {
  active_symbols: "brief",
  product_type: "basic",
};

const symbolsSelect = document.querySelector("#symbols");
const currentPriceDisplay = document.getElementById("currentPrice");
const currentProfitDisplay = document.getElementById("currentProfit");
const payoutValueDisplay = document.getElementById("payoutValue");
const strikePriceInput = document.getElementById("strikePrice");
const amountToStakeInput = document.getElementById("amountToStake");

const activeSymbolsResponse = async (res) => {
  const data = JSON.parse(res.data);

  if (data.error !== undefined) {
    console.error("Error:", data.error?.message);
    connection.removeEventListener("message", activeSymbolsResponse, false);
    await api.disconnect();
    return;
  }


  if (data.msg_type === "active_symbols") {
    // Clear existing options
    symbolsSelect.innerHTML = '<option value="">Select Symbol</option>';
   
    // Populate the dropdown with symbols
    data.active_symbols.forEach((symbol) => {
      const option = document.createElement("option");
      option.value = symbol.symbol;
      option.textContent = symbol.display_name;
      symbolsSelect.appendChild(option);
    });
    
  }

  connection.removeEventListener("message", activeSymbolsResponse, false);
};

const getActiveSymbols = async () => {
  connection.addEventListener("message", activeSymbolsResponse);
  await api.activeSymbols(active_symbols_request);
};

// WebSocket for tick data
const apiUrl = "wss://ws.binaryws.com/websockets/v3?app_id=53450"; // Replace with your app ID
const socket = new WebSocket(apiUrl);

socket.onopen = () => {
  console.log("WebSocket connection established.");
};

// Handle incoming tick data
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);


  // Update current price and calculate payout
  if (
    data.tick &&
    symbolsSelect.value &&
    data.tick.symbol === symbolsSelect.value
  ) {
    const currentPrice = data.tick.quote;
    currentPriceDisplay.textContent = currentPrice.toFixed(5); // Update the displayed price

    // Calculate the payout value
    const strikePrice = parseFloat(strikePriceInput.value);
    const amountStaked = parseFloat(amountToStakeInput.value);
    const optionType = "Rise"; // Assume the user selects "Rise" option

    // Example: Payout for a "Rise" option
    const payoutValue =
      optionType === "Rise"
        ? amountStaked * (1 + (currentPrice - strikePrice))
        : 0;

    payoutValueDisplay.textContent = payoutValue.toFixed(2); // Update the displayed payout
  }
};

socket.onerror = (error) => {
  console.error("WebSocket error:", error);
};

socket.onclose = (event) => {
  console.log("WebSocket connection closed:", event.code, event.reason);
};

// Update the WebSocket subscription based on selected symbol
symbolsSelect.addEventListener("change", () => {
  const selectedSymbol = symbolsSelect.value;

  // Unsubscribe from previous symbol if one is selected
  if (symbolsSelect.previousValue) {
    socket.send(
      JSON.stringify({ ticks: symbolsSelect.previousValue, unsubscribe: 1 })
    );
  }

  // Subscribe to the new selected symbol
  if (selectedSymbol) {
    socket.send(JSON.stringify({ ticks: selectedSymbol, subscribe: 1 }));
  }

  // Store the previous value to unsubscribe later
  symbolsSelect.previousValue = selectedSymbol;
});

// Event handler for Buy (Rise) button
document.getElementById("buyButton").addEventListener("click", function () {
  const currentPrice = parseFloat(currentPriceDisplay.textContent);
  const amountStaked = parseFloat(amountToStakeInput.value);
  strikePriceInput.value = currentPrice; // Set strike price to current price

  const strikePrice = parseFloat(strikePriceInput.value);
  const profit = (currentPrice - strikePrice) * amountStaked;
  currentProfitDisplay.textContent = profit.toFixed(2); // Update the displayed profit
});

// Event handler for Sell (Fall) button
document.getElementById("sellButton").addEventListener("click", function () {
  const currentPrice = parseFloat(currentPriceDisplay.textContent);
  const amountStaked = parseFloat(amountToStakeInput.value);
  strikePriceInput.value = currentPrice; // Set strike price to current price

  const strikePrice = parseFloat(strikePriceInput.value);
  const profit = (strikePrice - currentPrice) * amountStaked; // Example profit calculation for Sell
  currentProfitDisplay.textContent = profit.toFixed(2); // Update the displayed profit
});

// Call getActiveSymbols once the page loads to populate the dropdown
window.addEventListener("load", getActiveSymbols);
