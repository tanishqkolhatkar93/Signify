import React, { useState } from "react";
import { ShieldCheck, AlertCircle, Lock, EyeOff } from "lucide-react";

interface ConsentModalProps {
  isOpen: boolean;
  onGrant: () => void;
  onDeny: () => void;
}

export const ConsentModal: React.FC<ConsentModalProps> = ({ isOpen, onGrant, onDeny }) => {
  const [agreed, setAgreed] = useState(false);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="consent-title">
      <div className="modal-content">
        <div className="modal-header">
          <div className="modal-icon-badge">
            <ShieldCheck size={28} className="text-teal" />
          </div>
          <div>
            <h2 id="consent-title" className="modal-title">Camera Access & Privacy Consent</h2>
            <p className="modal-subtitle">Ethical AI Sign-Language Communication Guardrail</p>
          </div>
        </div>

        <div className="modal-body">
          <div className="privacy-callout">
            <EyeOff size={18} />
            <div>
              <strong>Zero Video Storage Policy:</strong>
              <p>Webcam frames are processed in volatile memory solely to extract 21 coordinate hand landmarks. Raw video is immediately discarded and never sent to cloud servers.</p>
            </div>
          </div>

          <ul className="consent-bullets">
            <li>
              <Lock size={15} />
              <span>Only normalized geometric coordinates $(x, y, z)$ are evaluated for gesture recognition.</span>
            </li>
            <li>
              <AlertCircle size={15} />
              <span>You have full control: you can pause or stop the camera at any moment.</span>
            </li>
            <li>
              <ShieldCheck size={15} />
              <span>No facial biometric profiles or personal recordings are retained.</span>
            </li>
          </ul>

          <label className="consent-checkbox-label">
            <input
              type="checkbox"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              className="consent-checkbox"
            />
            <span>I explicitly consent to webcam activation for real-time sign language landmark extraction.</span>
          </label>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onDeny}>
            Decline & Return
          </button>
          <button
            className="btn-primary"
            disabled={!agreed}
            onClick={() => {
              if (agreed) onGrant();
            }}
          >
            Grant Consent & Activate Camera
          </button>
        </div>
      </div>
    </div>
  );
};
