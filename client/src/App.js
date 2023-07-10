import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [news, setNews] = useState([]);
  const [selectedNews, setSelectedNews] = useState(null);
  const [currencyRates, setCurrencyRates] = useState({});
  const [weather, setWeather] = useState({});

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await fetch('http://localhost:8000/news');
        const data = await response.json();
        setNews(data);
      } catch (error) {
        console.error(error);
      }
    };

    fetchNews();
  }, []);

  useEffect(() => {
    const fetchCurrencyRates = async () => {
      try {
        const response = await fetch('http://localhost:8000/currency_rates');
        const data = await response.json();
        setCurrencyRates(data);
      } catch (error) {
        console.error(error);
      }
    };

    fetchCurrencyRates();

    const interval = setInterval(() => {
      fetchCurrencyRates();
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const response = await fetch('http://localhost:8000/weather');
        const data = await response.json();
        setWeather(data);
      } catch (error) {
        console.error(error);
      }
    };

    fetchWeather();

    const interval = setInterval(() => {
      fetchWeather();
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  const handleNewsClick = async (newsId) => {
    try {
      const response = await fetch(`http://localhost:8000/news/${newsId}`);
      const data = await response.json();
      setSelectedNews(data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleBackClick = () => {
    setSelectedNews(null);
  };

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
          {currencyRates.detail ? (
            <p>No currency rates available</p>
          ) : (
            <ul>
              {Object.entries(currencyRates).map(([currencyCode, currencyData]) => (
                <li key={currencyCode}>
                  {currencyData[0]}: {currencyData[1].toFixed(2)}
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="weather">
            {weather.detail ? (
                <div>
                  <h3>Weather</h3>
                  <p>No weather available</p>
                </div>
              ) : (
                <div>
                  <h3>Weather in {weather.city}</h3>
                  <p>{weather.weather} - {weather.celsius}°C</p>
                </div>
              )}
        </div>
      </div>
    </div>
  );
}

export default App;