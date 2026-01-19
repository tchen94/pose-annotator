import VideoContainer from "./VideoContainer";
import HeaderContainer from "./HeaderContainer";

const AppContainer = () => {
  return (
    <div className="w-screen h-screen overflow-y-auto flex flex-col">
      <HeaderContainer />
      <VideoContainer />
    </div>
  );
};

export default AppContainer;
