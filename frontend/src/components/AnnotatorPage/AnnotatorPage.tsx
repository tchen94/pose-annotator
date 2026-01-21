import { useParams, Navigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import AppContainer from "../../containers/AppContainer";
import TokenProvider from "../../providers/TokenProvider";
import Loader from "../Loader/Loader";

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
      <div className="flex flex-col items-center justify-center h-screen">
        <Loader />
        <p className="mt-6 text-gray-300 text-lg">
          Loading<span className="animate-ellipsis">...</span>
        </p>
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
