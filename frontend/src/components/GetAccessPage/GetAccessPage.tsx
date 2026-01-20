import { useMutation } from "@tanstack/react-query";
import toast, { Toaster } from "react-hot-toast";
import FooterContainer from "../../containers/FooterContainer";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const GetAccessPage = () => {
  const {
    mutate: generateToken,
    isPending,
    data,
    error,
  } = useMutation({
    mutationFn: async () => {
      const response = await fetch(`${API_URL}/admin/generate-token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Failed to generate token");
      }

      return result;
    },
    onSuccess: () => {
      toast.success("Access link generated successfully!");
    },
    onError: (err: Error) => {
      toast.error(err.message);
    },
  });

  const handleGenerate = () => {
    generateToken();
  };

  const copyToClipboard = () => {
    if (data?.link) {
      navigator.clipboard.writeText(data.link);
      toast.success("Link copied to clipboard!");
    }
  };

  return (
    <div className="w-full h-full bg-[#242424] flex flex-col">
      <Toaster position="top-center" />
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="bg-[#2a2a2a] rounded-lg shadow-2xl p-8 max-w-md w-full border border-gray-700">
        <h1 className="text-3xl font-bold mb-6 text-white text-center">
          Get Access
        </h1>

        <div className="space-y-4">
          {/* Disclaimer */}
          <div className="">
            <p className="text-lg text-gray-400 text-justify">
              ⚠️ By generating an access link, you agree that annotation data
              will be stored on our server for 14 days. Your work is tied to
              your unique URL. Please save your URL to access your annotations
              later.
            </p>
          </div>

          {/* Status Message */}
          {isPending && (
            <p className="text-sm text-blue-400 text-center">
              🔄 Generating your access link...
            </p>
          )}
          {data && (
            <p className="text-sm text-green-400 text-center">
              ✅ Access link generated successfully!
            </p>
          )}

          {!data && (
            <button
              onClick={handleGenerate}
              disabled={isPending}
              className="w-full bg-[#B8E6D5] text-[#242424] font-extrabold py-3 px-4 mt-4 rounded-lg hover:bg-[#A3D9C7] disabled:bg-gray-600 disabled:text-gray-400 transition-colors"
            >
              {isPending ? "Generating..." : "Generate My Access Link"}
            </button>
          )}

          {data && (
            <div className="mt-6 p-4 bg-[#1a1a1a] rounded-lg border border-gray-700">
              <p className="text-sm text-gray-300 mb-2">Your Unique URL:</p>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={data.link}
                  readOnly
                  className="flex-1 px-3 py-2 bg-[#242424] border border-gray-600 rounded text-white text-sm"
                />
                <button
                  onClick={copyToClipboard}
                  className="px-4 py-2 bg-[#B8E6D5] text-[#242424] font-bold rounded hover:bg-[#A3D9C7] transition-colors"
                >
                  Copy
                </button>
              </div>
              <p className="text-xs text-gray-400 mt-4">
                Save this link to access your annotations anytime
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
    <FooterContainer />
    </div>
  );
};

export default GetAccessPage;
