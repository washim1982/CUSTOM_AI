import React from "react";
import { useAuth0 } from "@auth0/auth0-react";

export default function AuthButtons() {
  const { loginWithRedirect, logout, isAuthenticated, user } = useAuth0();

  return (
    <div className="auth-buttons">
      {isAuthenticated ? (
        <>
          <span>Welcome, {user?.name || user?.email}</span>
          <button onClick={() => logout({ returnTo: window.location.origin })}>Logout</button>
        </>
      ) : (
        <button onClick={() => loginWithRedirect()}>Login</button>
      )}
    </div>
  );
}
