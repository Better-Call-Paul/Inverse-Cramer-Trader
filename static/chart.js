//fetch the alpaca data with an Ajax request

// Fetch portfolio data from the backend
fetch('/get_portfolio_data')
  .then(response => response.json())
  .then(portfolio_data => {
    // Create an array of datasets, one for each stock
    const datasets = portfolio_data.map(stock => {
      return {
        label: stock.label,
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        data: stock.values,
        fill: false  // Set fill to false for line chart
      };
    });

    // Extract the dates from the first stock in the portfolio_data array
    const labels = portfolio_data.length > 0 ? portfolio_data[0].dates : [];

    // Define the chart data and configuration
    const data = {
      labels: labels,  // Use the extracted dates as labels
      datasets: datasets
    };

    const config = {
      type: 'line',
      data: data,
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Portfolio Performance Over Time'
          }
        }
      },
    };

    // Create the chart
    const ctx = document.getElementById('portfolio-chart').getContext('2d');
    const portfolioChart = new Chart(ctx, config);
  })
  .catch(error => console.error(error));
