import CheckList from "../components/CheckList/CheckList";
import VideoPlayer from "../components/VideoPlayer/VideoPlayer";

const VideoContainer = () => {
  return (
    <div className="w-[95%] mx-auto flex flex-row flex-1">
      <VideoPlayer />
      <CheckList />
    </div>
  );
};

export default VideoContainer;
