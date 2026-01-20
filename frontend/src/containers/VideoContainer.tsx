import CheckList from "../components/CheckList/CheckList";
import VideoPlayer from "../components/VideoPlayer/VideoPlayer";

const VideoContainer = () => {
  return (
    <div className="w-[95%] mx-auto flex flex-row flex-1 overflow-y-auto">
      <VideoPlayer />
      <CheckList />
    </div>
  );
};

export default VideoContainer;
