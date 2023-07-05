import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [news, setNews] = useState([]);
  const [selectedNews, setSelectedNews] = useState(null);

  useEffect(() => {
    const fetchNews = async () => {
      const response = await axios.get('http://localhost:8000/');
      setNews(response.data.news);
    };

    if (news.length === 0) {
      fetchNews();
    }
  }, [news.length]);

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
    </div>
  );
}

export default App;