import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [news, setNews] = useState([]);
  const [selectedNews, setSelectedNews] = useState(null);
  const [currencyRates, setCurrencyRates] = useState({});
  const [weather, setWeather] = useState({});
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const newsResponse = await fetch(`http://localhost:8080/news/?page=${page}&size=${size}`);
        const newsData = await newsResponse.json();
        setNews(newsData);

        const totalCountHeader = newsResponse.headers.get('x-total-count');
        const totalCount = parseInt(totalCountHeader);
        setTotalCount(totalCount);

        const weatherResponse = await fetch('http://localhost:8080/weather');
        const weatherData = await weatherResponse.json();
        setWeather(weatherData);
      } catch (error) {
        console.error(error);
      }
    };

    fetchData();

    const currencySocket = new WebSocket('ws://localhost:8080/currency_rates');

    currencySocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setCurrencyRates(data);
    };

    currencySocket.onerror = (error) => {
      console.error(`WebSocket error: ${error}`);
    };

    return () => {
      currencySocket.close();
    };
  }, [page, size]);

  const handleNewsClick = async (newsId) => {
    try {
      const response = await fetch(`http://localhost:8080/news/${newsId}`);
      const data = await response.json();
      setSelectedNews(data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleBackClick = () => {
    setSelectedNews(null);
  };

  const handlePageChange = (event) => {
    const newPage = parseInt(event.target.value);
    setPage(newPage);
  };

  const handleSizeChange = (event) => {
    setSize(parseInt(event.target.value));
  };

  const totalPages = Math.ceil(totalCount / size);
  const pageNumbers = Array.from({ length: totalPages }, (_, index) => index + 1);

  return (
    <div className="app">
      <h1>News</h1>
      {!selectedNews ? (
        <div className="news-list">
          {Object.values(news).map((newsItem) => (
            <div key={newsItem.id} className="news-item" onClick={() => handleNewsClick(newsItem.id)}>
              <h2>{newsItem.title}</h2>
              <p>{newsItem.description}</p>
            </div>
          ))}
          <div className="pagination">
            <label htmlFor="page">Page:</label>
            <select id="page" name="page" value={page} onChange={handlePageChange}>
              {pageNumbers.map((pageNumber) => (
                <option key={pageNumber} value={pageNumber}>
                  {pageNumber}
                </option>
              ))}
            </select>
            <label htmlFor="size">Size:</label>
            <select id="size" name="size" value={size} onChange={handleSizeChange}>
              {[10, 20, 30].map((pageSize) => (
                <option key={pageSize} value={pageSize}>
                  {pageSize}
                </option>
              ))}
            </select>
          </div>
        </div>
      ) : (
        <div className="news-details">
          <h2>{selectedNews.title}</h2>
          <p>{selectedNews.description}</p>
          {selectedNews.content && <p>{selectedNews.content}</p>}
          <button onClick={handleBackClick}>Back</button>
        </div>
      )}
      <div className="sidebar">
        <div className="currency-rates">
          <h2>Currency Rates</h2>
          {!currencyRates.dollar ? (
            <p>No currency rates available</p>
          ) : (
            <ul>
              {Object.entries(currencyRates).map(([currencyCode, currencyData]) => (
                <li key={currencyCode}>
                  {currencyData[0]}: {currencyData[1].toFixed(2)} {currencyData[2] === 0 ? '→' : currencyData[2] === 1 ? '↑' : '↓'}
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="weather">
          {!weather.city ? (
            <div>
              <h3>Weather</h3>
              <p>No weather available</p>
            </div>
          ) : (
            <div>
              <h3>Weather in {weather.city}</h3>
              <p>
                {weather.weather} - {weather.celsius}°C
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
