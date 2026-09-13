import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ShieldCheck, ShieldX, ShieldAlert, Loader2, ArrowLeft } from 'lucide-react';
import { verifyCertificate } from '../api';
import '../styles/verify.css';

const TYPE_LABELS = {
  appreciation: 'Certificate of Appreciation',
  completion: 'Certificate of Completion',
  internship: 'Certificate of Internship',
  participation: 'Certificate of Participation',
  certificate: 'Certificate',
};

function Field({ label, value, full }) {
  if (!value) return null;
  return (
    <div className={`verify-field ${full ? 'full' : ''}`}>
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}

export default function VerifyCertificate() {
  const { identifier } = useParams();
  const [state, setState] = useState({ loading: true, data: null, error: null });

  useEffect(() => {
    let active = true;
    verifyCertificate(identifier)
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

  return (
    <div className="verify-page">
      <div className="verify-card">
        <div className="verify-status">
          <div className={`verify-badge ${kind}`}>
            {data?.valid ? <ShieldCheck size="34" /> : data?.revoked || data?.expired ? <ShieldAlert size="34" /> : <ShieldX size="34" />}
          </div>
          <h1>
            {data?.valid ? 'Valid Certificate' : data?.revoked ? 'Certificate Revoked' : data?.expired ? 'Certificate Expired' : 'Certificate Not Found'}
          </h1>
          <p>{data?.reason || (data?.valid ? 'This certificate was issued and verified by Piplad Welfare Foundation.' : 'We were unable to validate this certificate with the identifier provided.')}</p>
        </div>

        {data?.valid && data?.recipient_name !== 'Unknown' && (
          <div className="verify-details">
            <Field label="Recipient" value={data.recipient_name} full />
            <Field label="Certificate No." value={data.certificate_number} />
            <Field label="Type" value={TYPE_LABELS[data.certificate_type] || data.certificate_type} />
            <Field label="Program / Event" value={data.program_name} full />
            <Field label="Organisation" value={data.organisation_name} full />
            <Field label="Competition Date" value={data.competition_date} />
            <Field label="Competition Location" value={data.competition_location} />
            <Field label="Starting Date" value={data.starting_date} />
            <Field label="End Date" value={data.end_date} />
            <Field label="Issue Date" value={data.issue_date} />
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