import React, { useEffect, useState } from 'react';
import { fetchGalleryItems } from '../api';
import { Award, Image as ImageIcon } from 'lucide-react';

export default function Gallery() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGalleryItems()
      .then((data) => {
        setItems(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      {/* Banner */}
      <section style={{ background: '#0f172a', color: '#ffffff', padding: '4rem 0 3rem 0', textAlign: 'center' }}>
        <div className="container">
          <span className="badge badge-amber" style={{ marginBottom: '0.75rem' }}>
            <Award size={16} /> Media & Recognition
          </span>
          <h1 className="heading-xl" style={{ color: '#ffffff', marginBottom: '0.75rem' }}>Photo Gallery & Awards</h1>
          <p className="subheading" style={{ color: '#94a3b8', margin: '0 auto' }}>
            Glimpses of our health camps, education distribution drives, community food relief, and foundation recognition.
          </p>
        </div>
      </section>

      {/* Gallery Grid */}
      <section className="section-padding" style={{ background: '#f8fafc' }}>
        <div className="container">
          {loading ? (
            <div style={{ textAlign: 'center', padding: '4rem 0', color: '#64748b' }}>Loading gallery...</div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem' }}>
              {items.map((item) => (
                <div key={item.id} className="card">
                  <div style={{ position: 'relative', height: '230px', overflow: 'hidden' }}>
                    <img
                      src={item.image_url}
                      alt={item.title}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                    <span className="badge badge-green" style={{ position: 'absolute', top: '12px', left: '12px' }}>
                      {item.category}
                    </span>
                  </div>
                  <div style={{ padding: '1.25rem' }}>
                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a' }}>{item.title}</h3>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
