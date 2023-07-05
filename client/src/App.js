import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [news, setNews] = useState([]);
  const [selectedNews, setSelectedNews] = useState(null);
  const [currencyRates, setCurrencyRates] = useState({});
  const [weather, setWeather] = useState({});

  useEffect(() => {
    const fetchNews = async () => {
      const response = await axios.get('http://localhost:8000/');
      setNews(response.data.news);
    };

    if (news.length === 0) {
      fetchNews();
    }
  }, [news.length]);

  useEffect(() => {
    const fetchCurrencyRates = async () => {
      const response = await axios.get('http://127.0.0.1:8000/currency_rates');
      setCurrencyRates(response.data);
    };

    fetchCurrencyRates();

    const interval = setInterval(() => {
      fetchCurrencyRates();
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchWeather = async () => {
      const response = await axios.get('http://127.0.0.1:8000/weather');
      setWeather(response.data);
    };

    fetchWeather();

    const interval = setInterval(() => {
      fetchWeather();
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  const handleNewsClick = async (newsId) => {
    const response = await axios.get(`http://localhost:8000/news/${newsId}`);
    setSelectedNews(response.data.news);
  };

  const handleBackClick = () => {
    setSelectedNews(null);
  };

  return (
    <div className="app">
      <h1>News</h1>
      {!selectedNews ? (
        <div className="news-list">
          {Object.entries(news).map(([id, newsItem]) => (
            <div key={id} className="news-item" onClick={() => handleNewsClick(id)}>
              <h2>{newsItem[0]}</h2>
              <p>{newsItem[1]}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="news-details">
          <h2>{selectedNews[0]}</h2>
          <p>{selectedNews[1]}</p>
          <p>{selectedNews[2]}</p>
          <button onClick={handleBackClick}>Back</button>
        </div>
      )}
      <div className="sidebar">
        <div className="currency-rates">
          <h2>Currency Rates</h2>
          <ul>
            {Object.entries(currencyRates).map(([currency, rate]) => (
              <li key={currency}>
                {currency} {rate.toFixed(2)}
              </li>
            ))}
          </ul>
        </div>
        <div className="weather">
          <h3>Weather in {weather.city}</h3>
          <p>{weather.weather} - {weather.celsius}°C</p>
        </div>
      </div>
    </div>
  );
}

export default App;