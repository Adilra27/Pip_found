import React, { useState } from 'react';
import { X, Heart, ShieldCheck, CheckCircle2, Loader2 } from 'lucide-react';
import { createRazorpayOrder, verifyPayment } from '../api';

export default function DonateModal({ isOpen, onClose, selectedCause = null, causes = [] }) {
  const [amount, setAmount] = useState(1000);
  const [customAmount, setCustomAmount] = useState('');
  const [donorName, setDonorName] = useState('');
  const [donorEmail, setDonorEmail] = useState('');
  const [donorPhone, setDonorPhone] = useState('');
  const [causeId, setCauseId] = useState(selectedCause ? selectedCause.id : '');
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  if (!isOpen) return null;

  const presetAmounts = [500, 1000, 2500, 5000];

  const handleAmountClick = (val) => {
    setAmount(val);
    setCustomAmount('');
  };

  const getEffectiveAmount = () => {
    if (customAmount) return parseFloat(customAmount) || 0;
    return amount;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg(null);
    const finalAmount = getEffectiveAmount();

    if (finalAmount <= 0) {
      setErrorMsg('Please select or enter a valid donation amount.');
      return;
    }
    if (!donorName || !donorEmail) {
      setErrorMsg('Please enter your full name and email address.');
      return;
    }

    setLoading(true);

    try {
      // 1. Create Razorpay order on Python Backend
      const orderRes = await createRazorpayOrder({
        amount: finalAmount,
        currency: 'INR',
        donor_name: donorName,
        donor_email: donorEmail,
        donor_phone: donorPhone,
        cause_id: causeId ? parseInt(causeId) : null
      });

      // 2. Open Razorpay Checkout Window if Razorpay SDK is loaded on window
      if (window.Razorpay && orderRes.key_id && !orderRes.key_id.includes('test')) {
        const options = {
          key: orderRes.key_id,
          amount: finalAmount * 100,
          currency: 'INR',
          name: 'Piplad Welfare Foundation',
          description: 'Donation for Cause',
          order_id: orderRes.order_id,
          prefill: {
            name: donorName,
            email: donorEmail,
            contact: donorPhone
          },
          handler: async function (response) {
            // Verify payment
            await verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              donation_id: orderRes.donation_id
            });
            setLoading(false);
            setSuccessMsg(`Thank you, ${donorName}! Your donation of ₹${finalAmount.toLocaleString('en-IN')} was received successfully. An 80G tax receipt will be emailed to ${donorEmail}.`);
          },
          modal: {
            ondismiss: function () {
              setLoading(false);
            }
          }
        };
        const rzp = new window.Razorpay(options);
        rzp.open();
      } else {
        // Fallback for test/sandbox mode - directly verify order
        await verifyPayment({
          razorpay_order_id: orderRes.order_id,
          razorpay_payment_id: `pay_test_${Date.now()}`,
          razorpay_signature: 'test_sig',
          donation_id: orderRes.donation_id
        });
        setLoading(false);
        setSuccessMsg(`Thank you, ${donorName}! Your donation of ₹${finalAmount.toLocaleString('en-IN')} was completed successfully in test mode. An 80G tax receipt will be sent to ${donorEmail}.`);
      }
    } catch (err) {
      setLoading(false);
      setErrorMsg(err.message || 'Error processing donation. Please try again.');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: '1.25rem', right: '1.25rem', background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
        >
          <X size={24} />
        </button>

        {successMsg ? (
          <div style={{ textAlign: 'center', padding: '1rem 0' }}>
            <CheckCircle2 size={56} color="#059669" style={{ margin: '0 auto 1rem auto' }} />
            <h3 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.75rem' }}>Donation Successful!</h3>
            <p style={{ fontSize: '0.95rem', color: '#475569', lineHeight: 1.6, marginBottom: '1.5rem' }}>
              {successMsg}
            </p>
            <button className="btn btn-primary" onClick={onClose} style={{ width: '100%' }}>
              Close Window
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
              <div style={{ background: '#d1fae5', padding: '0.5rem', borderRadius: '8px', color: '#059669' }}>
                <Heart size={22} fill="#059669" />
              </div>
              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a' }}>Support Piplad Foundation</h3>
                <span style={{ fontSize: '0.8rem', color: '#059669', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <ShieldCheck size={14} /> 80G Tax Exemption Certificate Available
                </span>
              </div>
            </div>

            {errorMsg && (
              <div style={{ background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca', padding: '0.75rem', borderRadius: '8px', fontSize: '0.85rem', marginBottom: '1rem' }}>
                {errorMsg}
              </div>
            )}

            {/* Select Cause */}
            <div className="form-group">
              <label className="form-label">Choose Cause to Support</label>
              <select className="form-select" value={causeId} onChange={(e) => setCauseId(e.target.value)}>
                <option value="">General Fund (Where Needed Most)</option>
                {causes.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.title}
                  </option>
                ))}
              </select>
            </div>

            {/* Amount Selection */}
            <div className="form-group">
              <label className="form-label">Select Amount (INR)</label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.5rem', marginBottom: '0.5rem' }}>
                {presetAmounts.map((val) => (
                  <button
                    key={val}
                    type="button"
                    onClick={() => handleAmountClick(val)}
                    style={{
                      padding: '0.6rem',
                      borderRadius: '8px',
                      border: amount === val && !customAmount ? '2px solid #059669' : '1px solid #e2e8f0',
                      background: amount === val && !customAmount ? '#d1fae5' : '#ffffff',
                      color: amount === val && !customAmount ? '#065f46' : '#334155',
                      fontWeight: 700,
                      cursor: 'pointer'
                    }}
                  >
                    ₹{val}
                  </button>
                ))}
              </div>
              <input
                type="number"
                placeholder="Or enter custom amount in ₹"
                className="form-input"
                value={customAmount}
                onChange={(e) => { setCustomAmount(e.target.value); setAmount(0); }}
              />
            </div>

            {/* Donor Fields */}
            <div className="form-group">
              <label className="form-label">Full Name *</label>
              <input
                type="text"
                required
                placeholder="Your Name"
                className="form-input"
                value={donorName}
                onChange={(e) => setDonorName(e.target.value)}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="form-group">
                <label className="form-label">Email Address *</label>
                <input
                  type="email"
                  required
                  placeholder="name@example.com"
                  className="form-input"
                  value={donorEmail}
                  onChange={(e) => setDonorEmail(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Phone Number</label>
                <input
                  type="tel"
                  placeholder="+91 Mobile No."
                  className="form-input"
                  value={donorPhone}
                  onChange={(e) => setDonorPhone(e.target.value)}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '0.5rem', padding: '0.9rem', fontSize: '1.05rem', borderRadius: '8px' }}
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin" size={20} /> Processing...
                </>
              ) : (
                <>
                  <Heart size={20} fill="#ffffff" /> Proceed to Donate ₹{getEffectiveAmount().toLocaleString('en-IN')}
                </>
              )}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
