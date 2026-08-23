const json = (body, status = 200, origin = '*') => new Response(JSON.stringify(body), {
  status,
  headers: {
    'content-type': 'application/json; charset=utf-8',
    'access-control-allow-origin': origin,
    'access-control-allow-headers': 'Content-Type, Authorization',
    'access-control-allow-methods': 'GET, POST, OPTIONS',
  },
});

const now = () => new Date().toISOString();
const body = async (request) => request.json().catch(() => ({}));
const rows = (result) => result.results || [];

function adminAuthorized(request, env) {
  const header = request.headers.get('Authorization') || '';
  if (!header.startsWith('Basic ')) return false;
  const decoded = atob(header.slice(6));
  const [user, password] = decoded.split(':');
  return user === (env.ADMIN_USER || 'admin') && password === (env.ADMIN_PASSWORD || 'admin');
}

async function api(request, env) {
  const url = new URL(request.url);
  const path = url.pathname.replace(/\/$/, '');
  const method = request.method;
  const origin = env.FRONTEND_ORIGIN || '*';
  if (method === 'OPTIONS') return json({}, 204, origin);

  if (method === 'GET' && path === '/') return json({ status: 'online', organization: 'Piplad Welfare Foundation', tagline: 'Creating Opportunities, Creating Lives', docs_url: '/api/health' }, 200, origin);
  if (method === 'GET' && path === '/api/health') return json({ status: 'online' }, 200, origin);

  if (path === '/api/causes' && method === 'GET') return json(rows(await env.DB.prepare('SELECT * FROM causes ORDER BY created_at DESC').all()), 200, origin);
  if (path.match(/^\/api\/causes\/\d+$/) && method === 'GET') {
    const item = await env.DB.prepare('SELECT * FROM causes WHERE id = ?').bind(path.split('/').pop()).first();
    return item ? json(item, 200, origin) : json({ detail: 'Cause not found' }, 404, origin);
  }
  if (path === '/api/causes' && method === 'POST') {
    const data = await body(request);
    try {
      const result = await env.DB.prepare('INSERT INTO causes (title, slug, short_description, category, full_description, target_amount, raised_amount, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)').bind(data.title, data.slug, data.short_description, data.category || 'General', data.full_description || null, data.target_amount || 100000, data.raised_amount || 0, data.image_url || null).run();
      return json({ id: result.meta.last_row_id, ...data, category: data.category || 'General', target_amount: data.target_amount || 100000, raised_amount: data.raised_amount || 0 }, 201, origin);
    } catch { return json({ detail: 'Cause slug already exists' }, 400, origin); }
  }

  if (path === '/api/contact' && method === 'POST') {
    const data = await body(request);
    const result = await env.DB.prepare('INSERT INTO contact_inquiries (name, email, phone, subject, message, created_at) VALUES (?, ?, ?, ?, ?, ?)').bind(data.name, data.email, data.phone || null, data.subject || null, data.message, now()).run();
    return json({ id: result.meta.last_row_id, ...data, created_at: now() }, 201, origin);
  }
  if (path === '/api/contact' && method === 'GET') return json(rows(await env.DB.prepare('SELECT * FROM contact_inquiries ORDER BY created_at DESC').all()), 200, origin);
  if (path === '/api/team' && method === 'GET') return json(rows(await env.DB.prepare('SELECT * FROM team_members ORDER BY created_at DESC').all()), 200, origin);
  if (path === '/api/certificates' && method === 'GET') return json(rows(await env.DB.prepare('SELECT * FROM certificates ORDER BY created_at DESC').all()), 200, origin);
  if (path === '/api/blog' && method === 'GET') return json(rows(await env.DB.prepare("SELECT *, summary AS excerpt, published_date AS date FROM blogs ORDER BY published_date DESC").all()), 200, origin);
  if (path === '/api/about' && method === 'GET') return json(await env.DB.prepare('SELECT * FROM about_info ORDER BY id LIMIT 1').first() || { id: 0, name: 'Piplad Welfare Foundation' }, 200, origin);
  if (path === '/api/media' && method === 'GET') return json(rows(await env.DB.prepare('SELECT * FROM media_coverage ORDER BY published_date DESC').all()), 200, origin);

  if (path === '/api/donate/create-order' && method === 'POST') {
    const data = await body(request);
    if (!data.amount || data.amount <= 0) return json({ detail: 'Amount must be greater than zero' }, 400, origin);
    const orderId = `order_${crypto.randomUUID()}`;
    const result = await env.DB.prepare('INSERT INTO donations (donor_name, donor_email, donor_phone, amount, cause_id, razorpay_order_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)').bind(data.donor_name, data.donor_email, data.donor_phone || null, data.amount, data.cause_id || null, orderId, 'pending', now()).run();
    return json({ order_id: orderId, amount: data.amount, currency: data.currency || 'INR', key_id: env.RAZORPAY_KEY_ID || 'test_mode', donation_id: result.meta.last_row_id }, 200, origin);
  }
  if (path === '/api/donate/verify' && method === 'POST') {
    const data = await body(request);
    const donation = await env.DB.prepare('SELECT * FROM donations WHERE id = ?').bind(data.donation_id).first();
    if (!donation) return json({ detail: 'Donation not found' }, 404, origin);
    await env.DB.prepare('UPDATE donations SET status = ?, razorpay_payment_id = ? WHERE id = ?').bind('completed', data.razorpay_payment_id || null, data.donation_id).run();
    if (donation.cause_id) await env.DB.prepare('UPDATE causes SET raised_amount = raised_amount + ? WHERE id = ?').bind(donation.amount, donation.cause_id).run();
    return json({ message: 'Payment verified successfully', donation_id: donation.id }, 200, origin);
  }
  if (path === '/api/donate' && method === 'GET') return json(rows(await env.DB.prepare('SELECT * FROM donations ORDER BY created_at DESC').all()), 200, origin);

  if (path.startsWith('/api/admin/')) {
    if (!adminAuthorized(request, env)) return new Response('Unauthorized', { status: 401, headers: { 'WWW-Authenticate': 'Basic', 'access-control-allow-origin': origin } });
    if (path === '/api/admin/stats' && method === 'GET') return json(await env.DB.prepare("SELECT (SELECT COALESCE(SUM(amount), 0) FROM donations WHERE status = 'completed') AS total_donations, (SELECT COUNT(DISTINCT donor_email) FROM donations WHERE status = 'completed') AS total_donors, (SELECT COUNT(*) FROM causes) AS active_causes, (SELECT COUNT(*) FROM contact_inquiries) AS inquiries_count").first(), 200, origin);
    if (path === '/api/admin/gallery' && method === 'GET') return json(rows(await env.DB.prepare('SELECT * FROM gallery_items ORDER BY created_at DESC').all()), 200, origin);
    if (path === '/api/admin/gallery' && method === 'POST') {
      const data = await body(request);
      const result = await env.DB.prepare('INSERT INTO gallery_items (title, image_url, category, created_at) VALUES (?, ?, ?, ?)').bind(data.title, data.image_url, data.category || 'Events', now()).run();
      return json({ id: result.meta.last_row_id, ...data, category: data.category || 'Events' }, 201, origin);
    }
  }
  return json({ detail: 'Not found' }, 404, origin);
}

export default { fetch: api };
