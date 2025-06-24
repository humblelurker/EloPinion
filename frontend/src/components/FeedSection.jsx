

import React, { useEffect, useState } from 'react';

function FeedSection({ logged }) {
  const [feed, setFeed] = useState([]);

  useEffect(() => {
    if (logged) {
      fetch('/api/feed')
        .then((res) => res.json())
        .then((data) => setFeed(data))
        .catch((err) => console.error('Error fetching feed:', err));
    }
  }, [logged]);

  if (!logged) return null;

  return (
    <div className="feed-section">
      <h2>Tu feed personalizado</h2>
      {feed.length === 0 ? (
        <p>No hay recomendaciones aún.</p>
      ) : (
        <ul>
          {feed.map((item) => (
            <li key={item.id}>
              <strong>{item.title}</strong> - {item.summary}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default FeedSection;