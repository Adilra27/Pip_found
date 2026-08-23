import React, { useEffect, useState } from 'react';
import { ArrowRight, Calendar, Heart, PenTool, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { API_BASE_URL } from '../api';

const temporaryPosts = [
  {
    id: 'temporary-healthcare',
    category: 'Healthcare',
    title: 'Small acts of care can change a child\'s whole tomorrow',
    excerpt: 'From timely medical support to a reassuring hand, our healthcare work begins with seeing every child as a whole person.',
    date: 'Coming soon',
    readTime: '4 min read',
    accent: '#059669'
  },
  {
    id: 'temporary-education',
    category: 'Education',
    title: 'A learning opportunity is a door that stays open',
    excerpt: 'Quality education gives children more than supplies. It gives them confidence, choices, and a stronger voice in their future.',
    date: 'Coming soon',
    readTime: '3 min read',
    accent: '#0284c7'
  },
  {
    id: 'temporary-community',
    category: 'Community',
    title: 'Why lasting change is built together',
    excerpt: 'Our strongest work grows from local ideas, shared responsibility, and people who keep showing up for one another.',
    date: 'Coming soon',
    readTime: '5 min read',
    accent: '#d97706'
  }
];

function formatPost(post, index) {
  return {
    id: post.id || `post-${index}`,
    category: post.category || 'PWF Journal',
    title: post.title || 'A new story from Piplad Welfare Foundation',
    excerpt: post.excerpt || post.summary || post.content || 'More details from this story will be shared soon.',
    date: post.date ? new Date(post.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'Latest update',
    readTime: post.read_time || '3 min read',
    accent: ['#059669', '#0284c7', '#d97706'][index % 3]
  };
}

export default function Blog() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/blog`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch blog posts');
        return res.json();
      })
      .then((data) => setPosts(Array.isArray(data) ? data.map(formatPost) : []))
      .catch((error) => console.error('Failed to fetch blog:', error))
      .finally(() => setLoading(false));
  }, []);

  const visiblePosts = posts.length > 0 ? posts : temporaryPosts;

  return (
    <div>
      <section style={{ background: '#0f172a', color: '#fff', padding: '4rem 0', textAlign: 'center' }}>
        <div className="container">
          <span className="badge badge-green" style={{ marginBottom: '0.75rem' }}><Sparkles size={16} /> PWF Journal</span>
          <h1 className="heading-xl" style={{ color: '#fff', marginBottom: '0.75rem' }}>Stories That Move Us Forward</h1>
          <p className="subheading" style={{ color: '#cbd5e1', margin: '0 auto' }}>A closer look at the people, ideas, and everyday moments behind our mission.</p>
        </div>
      </section>

      <section className="section-padding" style={{ background: '#f8fafc' }}>
        <div className="container">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', gap: '1.5rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
            <div>
              <span className="badge badge-amber" style={{ marginBottom: '0.75rem' }}>{loading ? 'Preparing stories' : posts.length > 0 ? 'Latest from PWF' : 'Preview edition'}</span>
              <h2 className="heading-lg">Notes from the field</h2>
            </div>
            <p style={{ color: '#64748b', maxWidth: '360px', margin: 0 }}>Thoughtful updates from a foundation creating opportunities and creating lives.</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
            {visiblePosts.map((post, index) => (
              <article key={post.id} className="card" style={{ display: 'flex', flexDirection: 'column', minHeight: '360px', borderTop: `5px solid ${post.accent}` }}>
                <div style={{ padding: '1.5rem 1.5rem 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
                  <span style={{ color: post.accent, fontSize: '0.78rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>{post.category}</span>
                  <Heart size={18} color="#f59e0b" fill="#fef3c7" />
                </div>
                <div style={{ padding: '1rem 1.5rem 1.5rem', display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                  <h3 className="heading-md" style={{ marginBottom: '0.75rem' }}>{post.title}</h3>
                  <p style={{ color: '#475569', lineHeight: 1.65, marginBottom: '1.5rem' }}>{post.excerpt}</p>
                  <div style={{ display: 'flex', gap: '0.8rem', alignItems: 'center', color: '#64748b', fontSize: '0.82rem', marginTop: 'auto', flexWrap: 'wrap' }}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}><Calendar size={15} /> {post.date}</span>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}><PenTool size={15} /> {post.readTime}</span>
                  </div>
                </div>
              </article>
            ))}
          </div>

          <div style={{ marginTop: '3rem', padding: '2rem', background: '#ecfdf5', border: '1px solid #a7f3d0', borderRadius: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
            <div>
              <h3 style={{ color: '#065f46', fontSize: '1.2rem', marginBottom: '0.35rem' }}>Stay close to the work</h3>
              <p style={{ color: '#047857' }}>Explore the causes and people making these stories possible.</p>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <Link to="/causes" className="btn btn-primary">Explore Causes <ArrowRight size={17} /></Link>
              <Link to="/contact" className="btn btn-outline">Contact Us</Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
