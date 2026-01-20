import { useParams, Navigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import AppContainer from "../../containers/AppContainer";
import TokenProvider from "../../providers/TokenProvider";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const AnnotatorPage = () => {
  const { token } = useParams<{ token: string }>();

  const { data: validation, isLoading } = useQuery({
    queryKey: ["validate-token", token],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/validate-token/${token}`);
      if (!response.ok) throw new Error("Invalid token");
      return response.json();
    },
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Validating access...</div>
      </div>
    );
  }

  if (!validation?.success) {
    return <Navigate to="/" replace />;
  }

  return (
    <TokenProvider token={token!}>
      <AppContainer />
    </TokenProvider>
  );
};

export default AnnotatorPage;
