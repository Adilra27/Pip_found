import React, { useEffect, useState } from 'react';
import { PenTool, Calendar, MessageSquare } from 'lucide-react';

export default function Blog() {
  const [posts, setPosts] = useState([]);
  useEffect(() => {
    fetch('/api/blog')
      .then(res => res.json())
      .then(data => setPosts(data))
      .catch(err => console.error(err));
  }, []);
  return (
    <div>
      <section style={{ background: '#0f172a', color: '#fff', padding: '4rem 0', textAlign: 'center' }}>
        <div className="container">
          <span className="badge badge-green" style={{ marginBottom: '0.75rem' }}>Our Blog</span>
          <h1 className="heading-xl" style={{ marginBottom: '0.75rem' }}>Stories, Updates & News</h1>
          <p className="subheading" style={{ color: '#94a3b8' }}>Read about our impact, events, and the people behind the mission.</p>
        </div>
      </section>

      <section className="section-padding" style={{ background: '#f8fafc' }}>
        <div className="container" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
          {/* Example blog post cards */}
          {posts.map((post) => (
            <div key={post.id} className="card" style={{ padding: '2rem', borderTop: '4px solid #059669' }}>
              <h3 className="heading-md" style={{ marginBottom: '0.5rem', color: '#059669' }}>{post.title}</h3>
              <p style={{ color: '#475569', lineHeight: 1.6, marginBottom: '1rem' }}>{post.excerpt}</p>
              <div style={{ display: 'flex', gap: '1rem', color: '#64748b' }}>
                <PenTool size={16} />
                <span>{post.author}</span>
                <Calendar size={16} />
                <span>{post.date}</span>
                <MessageSquare size={16} />
                <span>{post.comments_count} comments</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
