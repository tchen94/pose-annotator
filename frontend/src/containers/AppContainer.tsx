import VideoContainer from "./VideoContainer";
import HeaderContainer from "./HeaderContainer";

const AppContainer = () => {
  return (
    <div className="w-full h-full flex flex-col">
      <HeaderContainer />
      <VideoContainer />
    </div>
  );
};

export default AppContainer;
