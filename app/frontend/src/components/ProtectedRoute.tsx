// src/components/ProtectedRoute.tsx
import React from "react";
import { useMsal } from "@azure/msal-react";
import { Navigate } from "react-router-dom";

const ALLOWED = [
  "admin@ardurra.com",
  "manager@ardurra.com",
  "psharma@ardurra.com"
  // …etc…
];

export function ProtectedRoute({ children }: { children: JSX.Element }) {
  const { instance } = useMsal();
  const account = instance.getActiveAccount();
  if (!account) return <Navigate to="/" replace />;

  const username = account.username.toLowerCase();
  if (!ALLOWED.includes(username)) {
    return <div style={{ padding: 20 }}>🚫 You don’t have access to that page.</div>;
  }

  return children;
}