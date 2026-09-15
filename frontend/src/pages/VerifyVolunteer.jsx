import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { verifyVolunteer } from '../api';
import VerificationShell from '../components/verify/VerificationShell';
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

function formatDate(value) {
  if (!value) return null;
  const parts = String(value).split('-');
  if (parts.length !== 3) return value;
  const [year, month, day] = parts;
  return `${day}/${month}/${year}`;
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
      <VerificationShell
        documentLabel="volunteer ID"
        heading="Verifying…"
        badgeKind="loading"
        qrIdentifier={identifier}
      />
    );
  }

  const data = state.data;

  if (state.error || !data) {
    return (
      <VerificationShell
        documentLabel="volunteer ID"
        heading="Volunteer ID Not Found"
        badgeKind="unknown"
        description={state.error || 'We were unable to validate this Volunteer ID with the identifier provided.'}
        qrIdentifier={identifier}
      />
    );
  }

  if (data.valid && data.full_name !== 'Unknown') {
    return (
      <VerificationShell
        documentLabel="volunteer ID"
        heading="Volunteer ID Verified"
        badgeKind="valid"
        qrIdentifier={identifier}
      >
        <div className="verify-details">
          <Field label="Full Name" value={data.full_name} full />
          <Field label="Volunteer ID" value={data.volunteer_id} />
          <Field label="Area of Interest" value={data.interest_area} />
          <Field label="Location" value={data.location} full />
          <Field label="Card Issue Date" value={formatDate(data.issue_date)} />
          <Field label="Valid Till" value={formatDate(data.valid_till)} />
          <Field label="Issued By" value={data.issued_by} full />
        </div>
      </VerificationShell>
    );
  }

  if (data.revoked) {
    return (
      <VerificationShell
        documentLabel="volunteer ID"
        heading="Volunteer ID Revoked"
        badgeKind="revoked"
        description={data.reason || 'This Volunteer ID has been revoked.'}
        qrIdentifier={identifier}
      >
        <div className="verify-details">
          <Field label="Volunteer ID" value={data.volunteer_id} full />
        </div>
      </VerificationShell>
    );
  }

  if (data.expired) {
    return (
      <VerificationShell
        documentLabel="volunteer ID"
        heading="Volunteer ID Expired"
        badgeKind="expired"
        description={data.reason || 'This Volunteer ID is no longer valid.'}
        qrIdentifier={identifier}
      >
        <div className="verify-details">
          <Field label="Volunteer ID" value={data.volunteer_id} full />
          <Field label="Valid Till" value={formatDate(data.valid_till)} />
        </div>
      </VerificationShell>
    );
  }

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
            <Field label="Position" value={data.position} />
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