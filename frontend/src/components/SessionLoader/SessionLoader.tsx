import { useQuery } from "@tanstack/react-query";
import { fetchSessions } from "../../api/annotations";
import useTokenContext from "../../providers/useTokenContext";
import CloseIcon from "../../assets/close.svg";

interface Session {
  frame_set_id: string;
  video_id: string;
  created_at: string;
  updated_at: string;
  total_frames: number;
  annotated_frames: number;
  status: string;
  progress_percentage: number;
}

interface SessionLoaderProps {
  onSessionLoad: (frameSetId: string) => void;
  onClose: () => void;
}

const SessionLoader = ({ onSessionLoad, onClose }: SessionLoaderProps) => {
  const token = useTokenContext();

  const { data: sessions, isLoading } = useQuery<Session[]>({
    queryKey: ["annotation-sessions", token],
    queryFn: () => fetchSessions(token || undefined),
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-3xl w-full max-h-[80vh] overflow-auto relative">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-800">
            Load Previous Session
          </h2>
          <button
            onClick={onClose}
            className="absolute top-2 right-1 text-gray-500 hover:text-gray-700 transition-colors"
          >
            <img src={CloseIcon} alt="Close" className="w-6 h-6" />
          </button>
        </div>

        {isLoading ? (
          <div className="text-center py-8">Loading sessions...</div>
        ) : sessions && sessions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No previous sessions found
          </div>
        ) : (
          <div className="space-y-3">
            {sessions?.map((session) => (
              <div
                key={session.frame_set_id}
                className="border border-gray-300 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => onSessionLoad(session.frame_set_id)}
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-semibold text-gray-800">
                      {session.video_id}
                    </h3>
                    <p className="text-sm text-gray-500">
                      Frame Set ID: {session.frame_set_id.slice(0, 8)}...
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm ${
                      session.status === "completed"
                        ? "bg-green-100 text-green-700"
                        : "bg-yellow-100 text-yellow-700"
                    }`}
                  >
                    {session.status === "completed"
                      ? "Completed"
                      : "In Progress"}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 mb-2">
                  <div>
                    <span className="font-medium">Progress:</span>{" "}
                    {session.annotated_frames}/{session.total_frames} frames (
                    {session.progress_percentage}%)
                  </div>
                  <div className="flex justify-end">
                    <span className="font-medium">Last updated:</span>{" "}
                    {formatDate(session.updated_at)}
                  </div>
                </div>

                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full transition-all"
                    style={{ width: `${session.progress_percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SessionLoader;
