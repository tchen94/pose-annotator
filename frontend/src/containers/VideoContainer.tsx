import CheckList from "../components/CheckList/CheckList";
import Toolbar from "../components/Toolbar/Toolbar";
import VideoPlayer from "../components/VideoPlayer/VideoPlayer";

const VideoContainer = () => {
  return (
    <div className="flex flex-row justify-center">
      <div className="flex flex-col flex-1">
        <Toolbar />
        <VideoPlayer />
      </div>
      <CheckList />
    </div>
  );
};

export default VideoContainer;
