import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import {
  addMyAddress,
  deactivateMyAccount,
  removeMyAddress,
  updateMyAddress,
  updateMyProfile,
} from "../api/accounts";
import { ApiError } from "../api/client";
import { useMyProfile } from "../hooks/useMyProfile";
import type { CustomerAccount, DeliveryAddress, UpdateCustomerRequest } from "../types/account";

// The UI picks the words; api/ only reports the status (F30). 401 never reaches here: client.ts signs you out.
function errorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) return "Can't reach ByteBites right now. Please try again.";
  if (error.status === 409) return "That email is already used by another account.";
  if (error.status === 404) return "That address no longer exists. Refresh the page.";
  if (error.status === 422) return "Please fix the highlighted fields.";
  return "Something went wrong. Please try again.";
}

type Feedback = { error: string | null; fieldErrors: Record<string, string> };
const NO_FEEDBACK: Feedback = { error: null, fieldErrors: {} };
const toFeedback = (error: unknown): Feedback => ({
  error: errorMessage(error),
  fieldErrors: error instanceof ApiError ? error.fieldErrors : {},
});

function DetailsForm({ profile, onSaved }: { profile: CustomerAccount; onSaved: (profile: CustomerAccount) => void }) {
  const [form, setForm] = useState({ full_name: profile.full_name, email: profile.email, phone: profile.phone });
  const [feedback, setFeedback] = useState<Feedback>(NO_FEEDBACK);
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // PATCH only what changed: the backend rejects an empty body
  const changes = Object.fromEntries(
    Object.entries(form).filter(([key, value]) => value !== profile[key as keyof typeof form]),
  ) as UpdateCustomerRequest;
  const hasChanges = Object.keys(changes).length > 0;

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setIsSaving(true);
    setFeedback(NO_FEEDBACK);
    setIsSaved(false);
    try {
      const saved = await updateMyProfile(changes);
      onSaved(saved);
      setForm({ full_name: saved.full_name, email: saved.email, phone: saved.phone });
      setIsSaved(true);
    } catch (caught) {
      setFeedback(toFeedback(caught));
    } finally {
      setIsSaving(false);
    }
  };

  const field = (name: keyof typeof form, label: string, type: string) => (
    <div>
      <label htmlFor={`profile-${name}`}>{label}</label>
      <input
        id={`profile-${name}`}
        type={type}
        value={form[name]}
        onChange={(event) => setForm({ ...form, [name]: event.target.value })}
        aria-invalid={Boolean(feedback.fieldErrors[name])}
      />
      {feedback.fieldErrors[name] && <p>{feedback.fieldErrors[name]}</p>}
    </div>
  );

  return (
    <section aria-labelledby="profile-details-heading">
      <h3 id="profile-details-heading">Your details</h3>
      <form onSubmit={handleSubmit} noValidate>
        {field("full_name", "Full name", "text")}
        {field("email", "Email", "email")}
        {field("phone", "Phone", "tel")}
        {feedback.error && <p role="alert">{feedback.error}</p>}
        {isSaved && <p role="status">Saved.</p>}
        <button type="submit" disabled={!hasChanges || isSaving}>
          {isSaving ? "Saving…" : "Save details"}
        </button>
      </form>
    </section>
  );
}

function AddressRow({
  address,
  onChanged,
  onRemoved,
}: {
  address: DeliveryAddress;
  onChanged: (address: DeliveryAddress) => void;
  onRemoved: (addressId: string) => void;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [form, setForm] = useState({ label: address.label, address: address.address });
  const [feedback, setFeedback] = useState<Feedback>(NO_FEEDBACK);

  const run = async (action: () => Promise<void>) => {
    setFeedback(NO_FEEDBACK);
    try {
      await action();
    } catch (caught) {
      setFeedback(toFeedback(caught));
    }
  };

  const save = (event: FormEvent) => {
    event.preventDefault();
    return run(async () => {
      onChanged(await updateMyAddress(address.id, form));
      setIsEditing(false);
    });
  };

  const remove = () =>
    run(async () => {
      await removeMyAddress(address.id);
      onRemoved(address.id);
    });

  return (
    <li>
      {isEditing ? (
        <form onSubmit={save} aria-label={`Edit ${address.label}`}>
          <label htmlFor={`label-${address.id}`}>Label</label>
          <input id={`label-${address.id}`} value={form.label} onChange={(e) => setForm({ ...form, label: e.target.value })} />
          <label htmlFor={`address-${address.id}`}>Address</label>
          <input
            id={`address-${address.id}`}
            value={form.address}
            onChange={(e) => setForm({ ...form, address: e.target.value })}
          />
          <button type="submit">Save address</button>
          <button type="button" onClick={() => setIsEditing(false)}>
            Cancel
          </button>
        </form>
      ) : (
        <>
          <strong>{address.label}</strong>: {address.address}{" "}
          <button type="button" onClick={() => setIsEditing(true)} aria-label={`Edit ${address.label}`}>
            Edit
          </button>
          <button type="button" onClick={remove} aria-label={`Remove ${address.label}`}>
            Remove
          </button>
        </>
      )}
      {feedback.error && <p role="alert">{feedback.error}</p>}
    </li>
  );
}

function Addresses({ addresses, onChange }: { addresses: DeliveryAddress[]; onChange: (next: DeliveryAddress[]) => void }) {
  const [form, setForm] = useState({ label: "", address: "" });
  const [feedback, setFeedback] = useState<Feedback>(NO_FEEDBACK);

  const handleAdd = async (event: FormEvent) => {
    event.preventDefault();
    setFeedback(NO_FEEDBACK);
    try {
      const added = await addMyAddress(form);
      onChange([...addresses, added]);
      setForm({ label: "", address: "" });
    } catch (caught) {
      setFeedback(toFeedback(caught));
    }
  };

  return (
    <section aria-labelledby="profile-addresses-heading">
      <h3 id="profile-addresses-heading">Delivery addresses</h3>
      {addresses.length === 0 ? (
        <p>No delivery addresses yet.</p>
      ) : (
        <ul>
          {addresses.map((address) => (
            <AddressRow
              key={address.id}
              address={address}
              onChanged={(changed) => onChange(addresses.map((each) => (each.id === changed.id ? changed : each)))}
              onRemoved={(removedId) => onChange(addresses.filter((each) => each.id !== removedId))}
            />
          ))}
        </ul>
      )}
      <form onSubmit={handleAdd} aria-label="Add an address" noValidate>
        <label htmlFor="new-address-label">New address label</label>
        <input id="new-address-label" value={form.label} onChange={(e) => setForm({ ...form, label: e.target.value })} />
        <label htmlFor="new-address">New address</label>
        <input id="new-address" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
        {feedback.error && <p role="alert">{feedback.error}</p>}
        <button type="submit">Add address</button>
      </form>
    </section>
  );
}

function Deactivate() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  const handleDeactivate = async () => {
    if (!window.confirm("Deactivate your account? You will be signed out everywhere and can't sign in again.")) return;
    try {
      await deactivateMyAccount();
      navigate("/account", { replace: true });
    } catch (caught) {
      setError(errorMessage(caught));
    }
  };

  return (
    <section aria-labelledby="profile-deactivate-heading">
      <h3 id="profile-deactivate-heading">Deactivate account</h3>
      <button type="button" onClick={handleDeactivate}>
        Deactivate my account
      </button>
      {error && <p role="alert">{error}</p>}
    </section>
  );
}

export function Profile() {
  const { state, setProfile } = useMyProfile();

  if (state.status === "loading") return <p role="status">Loading your profile…</p>;
  if (state.status === "not-a-customer") return <p role="alert">Profiles are for customer accounts.</p>;
  if (state.status === "error") return <p role="alert">Can't load your profile. Please refresh to try again.</p>;

  const { profile } = state;
  return (
    <main>
      <h2>Your profile</h2>
      <DetailsForm profile={profile} onSaved={setProfile} />
      <Addresses
        addresses={profile.delivery_addresses}
        onChange={(delivery_addresses) => setProfile({ ...profile, delivery_addresses })}
      />
      <Deactivate />
    </main>
  );
}
