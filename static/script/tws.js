document.addEventListener('DOMContentLoaded', async() => {
  populateSymbols();
  await getOrders()
});


async function getOrders(){
  console.log("getting orders")
  const response = await fetch("/api/get_ib_orders", {
    method: "GET",
  });
  
  const result = await response.json();
  console.log({result})
}

async function placeTrade() {
  
  const formData = new FormData(document.getElementById("tradeForm"));

  const tradeData = {
    symbol: formData.get("symbols"),
    size: parseInt(formData.get("size")),
    expiry: formData.get("expiry"),
    action: formData.get("action"),
  };
  

  try {
    const response = await fetch("/api/place_trade", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tradeData),
    });
    const result = await response.json();

    showNotification(result.message);
    document.getElementById("tradeForm").reset();
    // trackProfit(); // Start tracking profit immediately after placing the trade
  } catch (error) {
    showNotification("Failed to place trade: " + error.message, "error");
  }
}

async function getPosition() {
  try {
    // Fetch position details from the API
    const response = await fetch("/api/trade_profit");
    const data = await response.json();

    // Extract necessary information from the response
    console.log("position recieved");
    console.log(data);
    console.log("end of position");
    const position = data[0]; // Assuming the response is an array
    const account = position.account;
    const symbol = position.contract.localSymbol; // 'EUR.USD' in your example
    const positionAmount = position.position;
    const avgCost = position.avgCost;

    // Update the DOM to display the position details
    document.getElementById("account").innerText = account;
    document.getElementById("symbol").innerText = symbol;
    document.getElementById("position").innerText = positionAmount;
    document.getElementById("avgCost").innerText = avgCost.toFixed(4); // Limit to 4 decimal places
  } catch (error) {
    console.error("Error fetching position data:", error);
    document.getElementById("position-info").innerHTML =
      "<p>Error loading position data.</p>";
  }
}


function populateSymbols() {
  // Target the symbol dropdown within the tradeForm
  const tradeForm = document.getElementById('tradeForm');
  const symbolSelect = tradeForm.querySelector('#symbols');



  const symbols = [
    { symbol: "AUDCAD" },
    { symbol: "AUDCHF" },
    { symbol: "AUDJPY" },
    { symbol: "AUDNZD" },
    { symbol: "AUDUSD" },
    { symbol: "EURAUD" },
    { symbol: "EURCAD" },
    { symbol: "EURCHF" },
    { symbol: "EURGBP" },
    { symbol: "EURJPY" },
    { symbol: "EURNZD" },
    { symbol: "EURUSD" },
    { symbol: "GBPAUD" },
    { symbol: "GBPCAD" },
    { symbol: "GBPCHF" },
    { symbol: "GBPJPY" },
    { symbol: "GBPNOK" },
    { symbol: "GBPNZD" },
    { symbol: "GBPUSD" },
    { symbol: "XAUUSD" },
    { symbol: "NZDJPY" },
    { symbol: "NZDUSD" },
    { symbol: "XPDUSD" },
    { symbol: "XPTUSD" },
    { symbol: "XAGUSD" },
    { symbol: "USDCAD" },
    { symbol: "USDCHF" },
    { symbol: "USDJPY" },
    { symbol: "USDMXN" },
    { symbol: "USDNOK" },
    { symbol: "USDPLN" },
    { symbol: "USDSEK" }
  ];
  // Clear the dropdown and add default option
  symbolSelect.innerHTML = '<option value="">Select a symbol</option>';

  // Populate the dropdown with symbols
  symbols.forEach(item => {
      const option = document.createElement('option');
      option.value = item.symbol;
      option.textContent = item.symbol;
      symbolSelect.appendChild(option);
  });
}

window.placeTrade = placeTrade;


