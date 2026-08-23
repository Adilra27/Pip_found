const API_BASE_URL = 'http://localhost:8000/api';

export async function fetchCauses() {
  const res = await fetch(`${API_BASE_URL}/causes`);
  if (!res.ok) throw new Error('Failed to fetch causes');
  return res.json();
}

export async function fetchCauseById(id) {
  const res = await fetch(`${API_BASE_URL}/causes/${id}`);
  if (!res.ok) throw new Error('Failed to fetch cause details');
  return res.json();
}

export async function submitContact(data) {
  const res = await fetch(`${API_BASE_URL}/contact`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to submit contact form');
  return res.json();
}

export async function createRazorpayOrder(data) {
  const res = await fetch(`${API_BASE_URL}/donate/create-order`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create donation order');
  return res.json();
}

export async function verifyPayment(data) {
  const res = await fetch(`${API_BASE_URL}/donate/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to verify payment');
  return res.json();
}

export async function fetchAdminStats() {
  const res = await fetch(`${API_BASE_URL}/admin/stats`);
  if (!res.ok) throw new Error('Failed to fetch admin stats');
  return res.json();
}

export async function fetchGalleryItems() {
  const res = await fetch(`${API_BASE_URL}/admin/gallery`);
  if (!res.ok) throw new Error('Failed to fetch gallery items');
  return res.json();
}

export async function fetchDonationsList() {
  const res = await fetch(`${API_BASE_URL}/donate`);
  if (!res.ok) throw new Error('Failed to fetch donations');
  return res.json();
}

export async function fetchContactInquiries() {
  const res = await fetch(`${API_BASE_URL}/contact`);
  if (!res.ok) throw new Error('Failed to fetch inquiries');
  return res.json();
}
