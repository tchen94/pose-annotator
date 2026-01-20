import { createContext, type ReactNode } from "react";

interface TokenProviderProps {
  token: string;
  children: ReactNode;
}

export const TokenContext = createContext<string | null>(null);

const TokenProvider = ({ token, children }: TokenProviderProps) => {
  return (
    <TokenContext.Provider value={token}>{children}</TokenContext.Provider>
  );
};

export default TokenProvider;
