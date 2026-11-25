import { useState, type FormEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { registerCustomer, signIn } from "../api/accounts";
import { ApiError } from "../api/client";

type Mode = "sign-in" | "register";

const EMPTY_FORM = { full_name: "", email: "", phone: "", password: "" };

// The UI picks the words; api/ only reports the status (F30)
function errorMessage(error: unknown, mode: Mode): string {
  if (!(error instanceof ApiError)) return "Can't reach ByteBites right now. Please try again.";
  if (error.status === 401) return "Email or password is incorrect.";
  if (error.status === 403) return "This account is deactivated.";
  if (error.status === 409) return "That email is already registered. Sign in instead.";
  if (error.status === 422) return "Please fix the highlighted fields.";
  return mode === "register" ? "Couldn't create your account. Please try again." : "Couldn't sign you in. Please try again.";
}

export function Account() {
  const navigate = useNavigate();
  // RequireSignIn sends people here with the page they wanted; go back there after signing in
  const returnTo = (useLocation().state as { from?: string } | null)?.from ?? "/restaurants";
  const [mode, setMode] = useState<Mode>("sign-in");
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isRegistering = mode === "register";

  const updateField = (field: keyof typeof EMPTY_FORM) => (event: { target: { value: string } }) =>
    setForm({ ...form, [field]: event.target.value });

  const switchMode = () => {
    setMode(isRegistering ? "sign-in" : "register");
    setError(null);
    setFieldErrors({});
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setFieldErrors({});
    try {
      if (isRegistering) await registerCustomer(form);
      await signIn({ email: form.email, password: form.password });
      navigate(returnTo, { replace: true });
    } catch (caught) {
      setError(errorMessage(caught, mode));
      if (caught instanceof ApiError) setFieldErrors(caught.fieldErrors);
    } finally {
      setIsSubmitting(false);
    }
  };

  const field = (name: keyof typeof EMPTY_FORM, label: string, type = "text", autoComplete?: string) => (
    <div>
      <label htmlFor={`account-${name}`}>{label}</label>
      <input
        id={`account-${name}`}
        type={type}
        value={form[name]}
        onChange={updateField(name)}
        autoComplete={autoComplete}
        aria-invalid={Boolean(fieldErrors[name])}
        aria-describedby={fieldErrors[name] ? `account-${name}-error` : undefined}
        required
      />
      {fieldErrors[name] && <p id={`account-${name}-error`}>{fieldErrors[name]}</p>}
    </div>
  );

  return (
    <main>
      <h2>{isRegistering ? "Create your account" : "Sign in"}</h2>
      <form onSubmit={handleSubmit} noValidate>
        {isRegistering && field("full_name", "Full name", "text", "name")}
        {field("email", "Email", "email", "email")}
        {isRegistering && field("phone", "Phone", "tel", "tel")}
        {field("password", "Password", "password", isRegistering ? "new-password" : "current-password")}
        {error && <p role="alert">{error}</p>}
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Please wait…" : isRegistering ? "Create account" : "Sign in"}
        </button>
      </form>
      <button type="button" onClick={switchMode}>
        {isRegistering ? "Already have an account? Sign in" : "New to ByteBites? Create an account"}
      </button>
    </main>
  );
}
