import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ShieldCheck, ShieldAlert, ShieldX, Loader2, ArrowLeft } from 'lucide-react';
import { verifyVolunteer } from '../api';
import '../styles/verify.css';

function Field({ label, value, full }) {
  if (!value) return null;
  return (
    <div className={`verify-field ${full ? 'full' : ''}`}>
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}

export default function VerifyVolunteer() {
  const { identifier } = useParams();
  const [state, setState] = useState({ loading: true, data: null, error: null });

  useEffect(() => {
    let active = true;
    verifyVolunteer(identifier)
      .then((data) => active && setState({ loading: false, data, error: null }))
      .catch((err) => active && setState({ loading: false, data: null, error: err.message }));
    return () => { active = false; };
  }, [identifier]);

  if (state.loading) {
    return (
      <div className="verify-page">
        <div className="verify-card" style={{ textAlign: 'center' }}>
          <div className="verify-badge loading">
            <Loader2 size="32" className="spin" />
          </div>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800 }}>Verifying…</h1>
        </div>
      </div>
    );
  }

  const data = state.data;
  const kind = data?.valid ? 'valid' : data?.revoked ? 'revoked' : data?.expired ? 'expired' : 'unknown';
  const Icon = data?.valid ? ShieldCheck : data?.revoked || data?.expired ? ShieldAlert : ShieldX;

  return (
    <div className="verify-page">
      <div className="verify-card">
        <div className="verify-status">
          <div className={`verify-badge ${kind}`}>
            <Icon size="34" />
          </div>
          <h1>
            {data?.valid
              ? 'Verified Volunteer'
              : data?.revoked
                ? 'Volunteer ID Revoked'
                : data?.expired
                  ? 'Volunteer ID Expired'
                  : 'Volunteer ID Not Found'}
          </h1>
          <p>
            {data?.reason || (data?.valid
              ? 'This volunteer is a verified member of Piplad Welfare Foundation.'
              : 'We were unable to validate this Volunteer ID with the identifier provided.')}
          </p>
        </div>

        {data?.valid && data?.full_name !== 'Unknown' && (
          <div className="verify-details">
            <Field label="Full Name" value={data.full_name} full />
            <Field label="Volunteer ID" value={data.volunteer_id} />
            <Field label="Area of Interest" value={data.interest_area} />
            <Field label="Location" value={data.location} full />
            <Field label="Card Issue Date" value={data.issue_date} />
            <Field label="Valid Till" value={data.valid_till} />
            <Field label="Issued By" value={data.issued_by} full />
          </div>
        )}

        <Link className="back-link" to="/">
          <ArrowLeft size="16" /> Back to Piplad Welfare Foundation
        </Link>
      </div>
    </div>
  );
}